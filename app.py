from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Log Analyzer Agent")

# Log analysis prompt template
log_analysis_prompt_text = """
You are a senior site reliability engineer.

Analyze the following application logs.

1. Identify the main errors or failures.
2. Explain the likely root cause in simple terms.
3. Suggest practical next steps to fix or investigate.
4. Mention any suspicious patterns or repeated issues.

Logs:
{log_data}

Respond in clear paragraphs. Avoid jargon where possible.
"""

# Initialize LLM
llm = ChatOpenAI(
    temperature=0.2,
    model="gpt-4o-mini"
)


def split_logs(log_text: str):
    """Split log text into manageable chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    return splitter.split_text(log_text)


def analyze_logs(log_text: str):
    """Analyze logs by splitting and processing each chunk"""
    chunks = split_logs(log_text)
    combined_analysis = []

    for chunk in chunks:
        # Format the prompt with the chunk data
        formatted_prompt = log_analysis_prompt_text.format(log_data=chunk)
        # Invoke the LLM
        result = llm.invoke(formatted_prompt)
        combined_analysis.append(result.content)

    return "\n\n".join(combined_analysis)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    with open("index.html", "r") as f:
        return f.read()


@app.post("/analyze")
async def analyze_log_file(file: UploadFile = File(...)):
    """Analyze uploaded log file"""
    if not file.filename.endswith(".txt"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .txt log files are supported"}
        )

    try:
        content = await file.read()
        log_text = content.decode("utf-8", errors="ignore")

        if not log_text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Log file is empty"}
            )

        insights = analyze_logs(log_text)

        return {"analysis": insights}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error analyzing logs: {str(e)}"}
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "openai_api_key_configured": api_key_set
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
