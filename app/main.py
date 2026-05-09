import os
import warnings
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

from datetime import date

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader

from app.database import init_db, get_db
from app.services.content_service import ContentService, _format_content_html
from app.models.post import Post
from app.models.trending import TrendingTopic

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


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def index(request: Request):
    template = jinja_env.get_template("index.html")
    return HTMLResponse(template.render(request=request))


@app.post("/generate")
def generate(req: GenerateRequest, db: Session = Depends(get_db)):
    result = content_service.generate(
        topic=req.topic,
        db=db,
        description=req.description,
        style=req.style,
        length=req.length,
        tone=req.tone,
    )
    return result


@app.get("/result/{post_id}")
def result(request: Request, post_id: int, db: Session = Depends(get_db)):
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

    template = jinja_env.get_template("result.html")
    return HTMLResponse(template.render(
        request=request,
        post=post,
        tags=tags,
        tags_list=tags_list,
        content_html=content_html,
        title_len=title_len,
        content_len=content_len,
        tag_count=tag_count,
    ))


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
def history(request: Request, db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .limit(50)
        .all()
    )
    template = jinja_env.get_template("history.html")
    return HTMLResponse(template.render(request=request, posts=posts))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
