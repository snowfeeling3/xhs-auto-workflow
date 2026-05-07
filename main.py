import warnings
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader

from database import init_db, get_db
from services.content_service import ContentService
from models.post import Post

app = FastAPI(title="AI小红书爆款生成器")

app.mount("/static", StaticFiles(directory="static"), name="static")

jinja_env = Environment(loader=FileSystemLoader("templates"))

content_service = ContentService()


class GenerateRequest(BaseModel):
    topic: str


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def index(request: Request):
    template = jinja_env.get_template("index.html")
    return HTMLResponse(template.render(request=request))


@app.post("/generate")
def generate(req: GenerateRequest, db: Session = Depends(get_db)):
    result = content_service.generate(req.topic, db)
    return result


@app.get("/result/{post_id}")
def result(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        template = jinja_env.get_template("index.html")
        return HTMLResponse(template.render(request=request, error="记录不存在"))
    raw_content = post.content or ""
    tags = ""
    for marker in ["\n标签", "\n标签：", "\ntags：", "\ntags:"]:
        idx = raw_content.lower().find(marker)
        if idx != -1:
            tags = raw_content[idx + len(marker):].strip().lstrip("：:")
            break
    template = jinja_env.get_template("result.html")
    return HTMLResponse(template.render(request=request, post=post, tags=tags))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
