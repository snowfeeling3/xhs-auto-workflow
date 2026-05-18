import os
import hashlib
import hmac
import html
import warnings
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

from datetime import date
from uuid import uuid4

from fastapi import FastAPI, Request, Depends, Cookie, Query, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader

from app import config
from app.database import init_db, get_db
from app.services.content_service import ContentService, _format_content_html, get_or_create_account
from app.models.post import Post
from app.models.trending import TrendingTopic
from app.models.credit import CreditAccount
from app.models.payment import PaymentRecord, PaymentStatus

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

app = FastAPI(title="AI小红书爆款生成器")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

content_service = ContentService()


class GenerateRequest(BaseModel):
    topic: str
    description: str = ""
    style: str = ""
    length: str = ""
    tone: str = ""


class PaymentSubmitRequest(BaseModel):
    transaction_id: str


def resolve_session_key(request: Request, session_key: str = Cookie(default="")) -> str:
    """读取cookie中的session_key，不存在则生成新的并存入模板上下文供页面设置。"""
    if session_key:
        return session_key
    return uuid4().hex


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def index(request: Request, session_key: str = Cookie(default=""), db: Session = Depends(get_db)):
    new_key = session_key if session_key else uuid4().hex
    account = get_or_create_account(db, new_key)
    template = jinja_env.get_template("index.html")
    resp = HTMLResponse(template.render(
        request=request,
        credits=account.credits,
        session_key=new_key,
    ))
    if not session_key:
        resp.set_cookie(key="session_key", value=new_key, max_age=365 * 24 * 3600, httponly=True, samesite="lax")
    return resp


@app.post("/generate")
def generate(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    session_key: str = Cookie(default=""),
):
    new_key = session_key if session_key else uuid4().hex
    result = content_service.generate(
        topic=req.topic,
        db=db,
        description=req.description,
        style=req.style,
        length=req.length,
        tone=req.tone,
        session_key=new_key,
    )
    # 获取最新积分
    account = get_or_create_account(db, new_key)
    result["credits"] = account.credits
    resp = JSONResponse(result)
    if not session_key:
        resp.set_cookie(key="session_key", value=new_key, max_age=365 * 24 * 3600, httponly=True, samesite="lax")
    return resp


@app.get("/result/{post_id}")
def result(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    session_key: str = Cookie(default=""),
):
    new_key = session_key if session_key else uuid4().hex
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        template = jinja_env.get_template("index.html")
        return HTMLResponse(template.render(request=request, error="记录不存在"))

    raw_content = post.content or ""

    # Extract tags
    tags = ""
    tags_lower = raw_content.lower()
    for marker in ["\n标签", "\n标签：", "\ntags：", "\ntags:"]:
        idx = tags_lower.find(marker)
        if idx != -1:
            tags = raw_content[idx + len(marker):].strip().lstrip("：:")
            break

    # Build tags list for display
    tags_list = [t.strip() for t in tags.split("#") if t.strip()] if tags else []

    # Format content to HTML (image cards, bold, paragraphs)
    content_html = _format_content_html(raw_content)

    title_len = len(post.title or "")
    content_len = len(raw_content or "")
    tag_count = len(tags_list)

    account = get_or_create_account(db, new_key)

    template = jinja_env.get_template("result.html")
    resp = HTMLResponse(template.render(
        request=request,
        post=post,
        tags=tags,
        tags_list=tags_list,
        content_html=content_html,
        title_len=title_len,
        content_len=content_len,
        tag_count=tag_count,
        credits=account.credits,
    ))
    if not session_key:
        resp.set_cookie(key="session_key", value=new_key, max_age=365 * 24 * 3600, httponly=True, samesite="lax")
    return resp


@app.get("/api/trending")
def api_trending(db: Session = Depends(get_db)):
    today = date.today()
    topics = (
        db.query(TrendingTopic)
        .filter(TrendingTopic.date == today)
        .order_by(TrendingTopic.rank)
        .all()
    )
    return {"date": today.isoformat(), "topics": [t.to_dict() for t in topics]}


@app.get("/history")
def history(
    request: Request,
    db: Session = Depends(get_db),
    session_key: str = Cookie(default=""),
):
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .limit(50)
        .all()
    )
    new_key = session_key if session_key else uuid4().hex
    account = get_or_create_account(db, new_key)
    template = jinja_env.get_template("history.html")
    resp = HTMLResponse(template.render(
        request=request,
        posts=posts,
        credits=account.credits,
    ))
    if not session_key:
        resp.set_cookie(key="session_key", value=new_key, max_age=365 * 24 * 3600, httponly=True, samesite="lax")
    return resp


# ── 积分查询 ──
@app.get("/api/credits")
def api_credits(
    db: Session = Depends(get_db),
    session_key: str = Cookie(default=""),
):
    new_key = session_key if session_key else uuid4().hex
    account = get_or_create_account(db, new_key)
    resp = JSONResponse({"credits": account.credits, "total_used": account.total_used})
    if not session_key:
        resp.set_cookie(key="session_key", value=new_key, max_age=365 * 24 * 3600, httponly=True, samesite="lax")
    return resp


# ── 付款页面 ──
@app.get("/payment")
def payment_page(
    request: Request,
    db: Session = Depends(get_db),
    session_key: str = Cookie(default=""),
):
    if not config.PAYMENT_QR_URL:
        return HTMLResponse("<h2>管理员尚未配置收款二维码，请联系站长。</h2>")

    new_key = session_key if session_key else uuid4().hex
    account = get_or_create_account(db, new_key)

    # 查询当前session的付款记录
    payments = (
        db.query(PaymentRecord)
        .filter(PaymentRecord.session_key == new_key)
        .order_by(PaymentRecord.created_at.desc())
        .limit(20)
        .all()
    )

    template = jinja_env.get_template("payment.html")
    resp = HTMLResponse(template.render(
        request=request,
        credits=account.credits,
        qr_url=config.PAYMENT_QR_URL,
        payments=payments,
    ))
    if not session_key:
        resp.set_cookie(key="session_key", value=new_key, max_age=365 * 24 * 3600, httponly=True, samesite="lax")
    return resp


# ── 提交付款验证 ──
@app.post("/api/payment/submit")
def submit_payment(
    req: PaymentSubmitRequest,
    db: Session = Depends(get_db),
    session_key: str = Cookie(default=""),
):
    if not session_key:
        return {"error": "会话未识别，请刷新页面后重试"}
    if not req.transaction_id.strip():
        return {"error": "请输入付款交易单号"}

    tid = req.transaction_id.strip()

    # 检查是否已提交过相同交易单号
    existing = db.query(PaymentRecord).filter(
        PaymentRecord.transaction_id == tid
    ).first()
    if existing:
        return {"error": f"该交易单号已提交过，当前状态：{existing.status}"}

    record = PaymentRecord(
        session_key=session_key,
        transaction_id=tid,
        amount_yuan=1,
        credits=3,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # 如果开启了自动验证，直接加积分
    if config.PAYMENT_AUTO_VERIFY:
        account = get_or_create_account(db, session_key)
        account.credits += 3
        record.status = PaymentStatus.verified.value
        record.remark = "自动验证"
        db.commit()
        return {
            "success": True,
            "message": "充值成功！已自动到账 3 次使用次数",
            "credits": account.credits,
        }

    return {
        "success": True,
        "message": "提交成功，等待管理员验证后到账。如有疑问请联系站长。",
    }


# ── 管理后台辅助 ──
def _admin_cookie_value() -> str:
    return hmac.new(config.ADMIN_KEY.encode(), b"admin", hashlib.sha256).hexdigest()

def _check_admin(key: str, admin_token: str) -> bool:
    if admin_token == _admin_cookie_value():
        return True
    if key == config.ADMIN_KEY:
        return True
    return False

# ── 管理后台：登录 ──
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    body = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>管理登录</title></head>
<body style="background:#09090B;color:#EDEDF0;font-family:monospace;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;">
<form method="post" action="/admin/login" style="background:#1A1A1F;padding:2rem;border-radius:12px;border:1px solid #252530;">
<h2 style="margin:0 0 1.5rem;">管理后台登录</h2>
<input type="password" name="key" placeholder="管理密钥" style="width:100%;padding:0.7rem;background:#131316;border:1px solid #252530;border-radius:8px;color:#EDEDF0;font-size:0.95rem;margin-bottom:1rem;">
<button type="submit" style="width:100%;padding:0.7rem;background:#FF2442;color:#fff;border:none;border-radius:8px;font-size:0.95rem;cursor:pointer;">登录</button>
</form></body></html>"""
    return HTMLResponse(body)

@app.post("/admin/login")
def admin_login(key: str = Form(...)):
    if key != config.ADMIN_KEY:
        return HTMLResponse("<h2>密钥错误</h2>", status_code=403)
    resp = RedirectResponse("/admin/payments", status_code=303)
    resp.set_cookie(key="admin_token", value=_admin_cookie_value(), max_age=8 * 3600, httponly=True, samesite="lax")
    return resp

# ── 管理后台：付款记录列表 ──
@app.get("/admin/payments")
def admin_payments(
    request: Request,
    key: str = Query(default=""),
    admin_token: str = Cookie(default=""),
    db: Session = Depends(get_db),
):
    if not _check_admin(key, admin_token):
        return HTMLResponse("<h2>无权访问</h2>", status_code=403)

    payments = (
        db.query(PaymentRecord)
        .order_by(PaymentRecord.created_at.desc())
        .limit(100)
        .all()
    )
    rows = ""
    for p in payments:
        tx_id = html.escape(p.transaction_id)
        remark = html.escape(p.remark or "")
        rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #333;">{p.id}</td>
            <td style="padding:8px;border:1px solid #333;">{html.escape(p.session_key[:12])}...</td>
            <td style="padding:8px;border:1px solid #333;">{tx_id}</td>
            <td style="padding:8px;border:1px solid #333;">¥{p.amount_yuan}</td>
            <td style="padding:8px;border:1px solid #333;">{p.credits}次</td>
            <td style="padding:8px;border:1px solid #333;color:{'#6EE7B7' if p.status == 'verified' else '#FCD34D' if p.status == 'pending' else '#FF2442'}">{p.status}</td>
            <td style="padding:8px;border:1px solid #333;">{p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else ''}</td>
            <td style="padding:8px;border:1px solid #333;">
                {"<a href='/admin/verify/{id}?action=approve' style='color:#6EE7B7;margin-right:8px;'>通过</a><a href='/admin/verify/{id}?action=reject' style='color:#FF2442;'>拒绝</a>".format(id=p.id) if p.status == 'pending' else remark}
            </td>
        </tr>"""
    html_body = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>付款管理</title></head>
<body style="background:#09090B;color:#EDEDF0;font-family:monospace;padding:2rem;">
<h2>付款记录管理</h2>
<table style="border-collapse:collapse;width:100%;">
<thead><tr>
    <th style="padding:8px;border:1px solid #333;">ID</th>
    <th style="padding:8px;border:1px solid #333;">Session</th>
    <th style="padding:8px;border:1px solid #333;">交易单号</th>
    <th style="padding:8px;border:1px solid #333;">金额</th>
    <th style="padding:8px;border:1px solid #333;">积分</th>
    <th style="padding:8px;border:1px solid #333;">状态</th>
    <th style="padding:8px;border:1px solid #333;">时间</th>
    <th style="padding:8px;border:1px solid #333;">操作</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
<p style="margin-top:1rem;color:#5C5C68;"><a href="/payment" style="color:#FF2442;">返回付款页</a></p>
</body></html>"""
    resp = HTMLResponse(html_body)
    if key == config.ADMIN_KEY and admin_token != _admin_cookie_value():
        resp.set_cookie(key="admin_token", value=_admin_cookie_value(), max_age=8 * 3600, httponly=True, samesite="lax")
    return resp


# ── 管理后台：审核付款 ──
@app.get("/admin/verify/{payment_id}")
def admin_verify(
    payment_id: int,
    key: str = Query(default=""),
    action: str = Query(default="approve"),
    admin_token: str = Cookie(default=""),
    db: Session = Depends(get_db),
):
    if not _check_admin(key, admin_token):
        return HTMLResponse("<h2>无权访问</h2>", status_code=403)

    record = db.query(PaymentRecord).filter(PaymentRecord.id == payment_id).first()
    if not record:
        return HTMLResponse("<h2>记录不存在</h2>", status_code=404)

    if record.status != PaymentStatus.pending.value:
        return HTMLResponse(f"<h2>该记录已处理，当前状态：{record.status}</h2>")

    if action == "approve":
        account = db.query(CreditAccount).filter(
            CreditAccount.session_key == record.session_key
        ).first()
        if account:
            account.credits += record.credits
        else:
            account = CreditAccount(
                session_key=record.session_key,
                credits=record.credits,
            )
            db.add(account)
        record.status = PaymentStatus.verified.value
        record.remark = "管理员验证通过"
        db.commit()
        return HTMLResponse(f"<h2>已通过，为用户 {html.escape(record.session_key[:12])}... 充值 {record.credits} 次</h2><p><a href='/admin/payments'>返回管理</a></p>")

    if action == "reject":
        record.status = PaymentStatus.rejected.value
        record.remark = "管理员拒绝"
        db.commit()
        return HTMLResponse(f"<h2>已拒绝</h2><p><a href='/admin/payments'>返回管理</a></p>")

    return HTMLResponse("<h2>无效操作</h2>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
