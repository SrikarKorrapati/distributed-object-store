from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from typing import Optional

app = FastAPI(title="Developer Notes")

# ── In-memory store ──────────────────────────────────────────────────────────
_notes: dict[str, dict] = {}

# ── Models ───────────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    title: str
    content: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be blank")
        if len(v) > 120:
            raise ValueError("title must be 120 characters or fewer")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("content cannot be blank")
        return v


class Note(BaseModel):
    id: str
    title: str
    content: str
    created_at: str


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.get("/notes", response_model=list[Note])
def list_notes():
    return sorted(_notes.values(), key=lambda n: n["created_at"], reverse=True)


@app.post("/notes", response_model=Note, status_code=201)
def create_note(body: NoteCreate):
    note_id = str(uuid4())
    note = {
        "id": note_id,
        "title": body.title.strip(),
        "content": body.content.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _notes[note_id] = note
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    if note_id not in _notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del _notes[note_id]


# ── Static frontend ───────────────────────────────────────────────────────────

_static = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=_static), name="static")

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(_static / "index.html")
