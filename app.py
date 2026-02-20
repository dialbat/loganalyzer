import os
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

load_dotenv()

app = FastAPI(title="Log Analyzer Agent")

# -----------------------------
# Configuration (Coolify-friendly)
# -----------------------------
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))  # prevents accidental huge uploads

log_analysis_prompt_text = """You are a senior site reliability engineer.

Analyze the following application logs.
1. Identify the main errors or failures.
2. Explain the likely root cause in simple terms.
3. Suggest practical next steps to fix or investigate.
4. Mention any suspicious patterns or repeated issues.

Logs:
{log_data}

Respond in clear paragraphs. Avoid jargon where possible.
"""

# LangChain LLM client
llm = ChatOpenAI(
    temperature=0.2,
    model=OPENAI_MODEL,
)

# -----------------------------
# Helpers
# -----------------------------
def split_logs(log_text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    return splitter.split_text(log_text)


def analyze_logs(log_text: str) -> str:
    chunks = split_logs(log_text)
    combined: list[str] = []
    for chunk in chunks:
        formatted_prompt = log_analysis_prompt_text.format(log_data=chunk)
        result = llm.invoke(formatted_prompt)
        combined.append(result.content)
    return "\n\n".join(combined)


# -----------------------------
# Routes
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def root():
    # Serves index.html from repo root.
    # Make sure your index.html is actual HTML+JS that POSTs to /analyze.
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            "<h1>index.html not found</h1><p>Add an index.html in the repo root.</p>",
            status_code=500,
        )


@app.post("/analyze")
async def analyze_log_file(file: UploadFile = File(...)):
    # Basic file validation
    filename = file.filename or ""
    if not filename.lower().endswith(".txt"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .txt log files are supported"},
        )

    try:
        content = await file.read()

        # Enforce upload size limit
        max_bytes = MAX_UPLOAD_MB * 1024 * 1024
        if len(content) > max_bytes:
            return JSONResponse(
                status_code=413,
                content={"error": f"File too large. Max {MAX_UPLOAD_MB} MB."},
            )

        log_text = content.decode("utf-8", errors="replace")
        if not log_text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Log file is empty"},
            )

        insights = analyze_logs(log_text)
        return {"analysis": insights}

    except Exception as e:
        # Return JSON so the browser can show the actual backend error
        return JSONResponse(
            status_code=500,
            content={"error": f"Error analyzing logs: {str(e)}"},
        )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "openai_api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "model": OPENAI_MODEL,
        "max_upload_mb": MAX_UPLOAD_MB,
    }


# -----------------------------
# Local run (optional)
# -----------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
