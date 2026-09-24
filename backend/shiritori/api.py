from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .db import connect
from .routes import load_routes
from .service import InvalidAnswer, PlayNotFound, ShiritoriService

router = APIRouter(prefix="/shiritori", tags=["shiritori"])

_service: ShiritoriService | None = None


def get_service() -> ShiritoriService:
    global _service
    if _service is None:
        _service = ShiritoriService(connect(), load_routes())
        _service.seed_if_empty()
    return _service


class PlayCreate(BaseModel):
    player_id: str = Field(min_length=1, max_length=64)


class AnswerCreate(BaseModel):
    step: int
    choice: str


class PlayState(BaseModel):
    play_id: str
    step: int
    max_steps: int
    history: list[str]
    word: str
    kana: str
    choices: list[str]
    finished: bool


class StepResult(BaseModel):
    step: int
    from_word: str
    choice: str
    total: int
    counts: dict[str, int]
    rate: int
    is_top: bool


class PlayResult(BaseModel):
    play_id: str
    finished: bool
    score: int
    hits: int
    steps: list[StepResult]


@router.post("/plays", response_model=PlayState, status_code=201)
def create_play(body: PlayCreate, service: ShiritoriService = Depends(get_service)):
    return service.create_play(body.player_id)


@router.get("/plays/{play_id}", response_model=PlayState)
def get_play(play_id: str, service: ShiritoriService = Depends(get_service)):
    try:
        return service.state(play_id)
    except PlayNotFound:
        raise HTTPException(status_code=404, detail="Play not found")


@router.post("/plays/{play_id}/answers", response_model=PlayState)
def answer(play_id: str, body: AnswerCreate, service: ShiritoriService = Depends(get_service)):
    try:
        return service.answer(play_id, body.step, body.choice)
    except PlayNotFound:
        raise HTTPException(status_code=404, detail="Play not found")
    except InvalidAnswer as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/plays/{play_id}/result", response_model=PlayResult)
def result(play_id: str, service: ShiritoriService = Depends(get_service)):
    try:
        return service.result(play_id)
    except PlayNotFound:
        raise HTTPException(status_code=404, detail="Play not found")
