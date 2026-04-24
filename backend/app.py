from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import init_db, get_random_word, get_word_count, insert_words
from ai_engine import generate_batch

generation_status: dict = {"running": False, "last": None, "error": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="MyDict API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    context: str = ""


@app.get("/api/word/random")
def random_word(exclude_id: int = Query(default=None)):
    word = get_random_word(exclude_id)
    if not word:
        return {
            "error": "no_words",
            "message": "Database is empty. Open Settings → Update Word Base to generate words.",
        }
    return word


@app.get("/api/stats")
def stats():
    return {"word_count": get_word_count()}


@app.get("/api/generate/status")
def gen_status():
    return generation_status


@app.post("/api/generate")
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    if generation_status["running"]:
        return {"status": "already_running"}
    background_tasks.add_task(_run_generation, req.context)
    return {"status": "started"}


async def _run_generation(context: str):
    generation_status["running"] = True
    generation_status["error"] = None
    try:
        words = await generate_batch(context)
        inserted = insert_words(words)
        generation_status["last"] = f"Added {inserted} new words (total: {get_word_count()})"
    except Exception as e:
        generation_status["error"] = str(e)
    finally:
        generation_status["running"] = False
