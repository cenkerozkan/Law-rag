from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
from typing import List

from service.rag_service import RagService
from db.model.chat_thread_model import ChatThreadModel
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
rag_service = RagService()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for request/response
class ChatCreate(BaseModel):
    chat_name: str

class MessageSend(BaseModel):
    message: str
    chat_id: str

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/api/chats")
async def create_chat(chat: ChatCreate):
    result = await rag_service.create_new_chat_thread(chat.chat_name)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create chat")
    return result

@app.get("/api/chats")
async def get_chats():
    return await rag_service._context_repository.get_all()

@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str):
    chat = await rag_service.retrieve_chat_thread(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    success = await rag_service.delete_chat_thread(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"success": True}

@app.post("/api/chats/{chat_id}/messages")
async def send_message(chat_id: str, message: MessageSend):
    chat = await rag_service.retrieve_chat_thread(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    response = await rag_service.send_message(message.message, chat)
    return {"response": response}