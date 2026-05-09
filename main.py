import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import traceback
from graph.workflow import run_agent_chat
from data.order_db import order_db

app = FastAPI(title="AI Order Agent API")

# 定義 API 請求格式
class ChatRequest(BaseModel):
    message: str
    session_id: str

# 定義 API 回應格式
class ChatResponse(BaseModel):
    answer: str
    session_id: str
    current_db: dict

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 呼叫 agent_service
        answer = await run_agent_chat(request.message, request.session_id)
        
        return ChatResponse(
            answer=answer[0]['text'] if isinstance(answer, list) and len(answer) > 0 else str(answer),
            session_id=request.session_id,
            current_db=order_db
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/static", StaticFiles(directory="static"), name="static")

# 設定根目錄回傳 index.html
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)