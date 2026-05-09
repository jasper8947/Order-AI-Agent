# 使用輕量版 Python
FROM python:3.10.11

# 設定工作目錄
WORKDIR /app

# 複製依賴清單
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有專案檔案
COPY . .

# 啟動命令 (對應 main.py 中的 FastAPI)
CMD ["python", "main.py"]