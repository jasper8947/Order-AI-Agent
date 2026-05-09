import os
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.order_tools import order_tools
# from dotenv import load_dotenv

# load_dotenv()
# 因為 Cloud Run 不需要它，且有時會干擾系統環境變數

# 手動取得 Key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # 這樣在 Logs 裡你就會看到這行明確的錯誤
    raise ValueError("CRITICAL ERROR: GOOGLE_API_KEY is not set in environment variables!")

# 手動將 api_key 傳入
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",  # 建議先用 1.5-flash 確保穩定
    google_api_key=api_key,    # 明確傳遞參數
    temperature=0
)

model_with_tools = llm.bind_tools(order_tools)