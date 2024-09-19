from fastapi import APIRouter
from models.dataclasses import ChatRequest, ChatResponse
from api.chat import get_answer
import time
from utils.logger import logger

router_chat = APIRouter(prefix="/chat")

@router_chat.post("/chat", response_model=ChatResponse)
def interact(req: ChatRequest):
    start_time = time.time()
    res = get_answer(req)
    logger.info(f"Chat request {res.session_id} processed in {round(time.time() - start_time, 2)} seconds.")
    return res