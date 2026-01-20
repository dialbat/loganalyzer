# Log Analyzer Agent

An AI-powered log analysis tool built with LangChain and OpenAI that automatically identifies errors, explains root causes, and suggests fixes for your application logs.

## Features

- 📤 **Simple Upload Interface** - Drag and drop or select log files
- 🤖 **AI-Powered Analysis** - Uses GPT-4o-mini to understand log context
- 🔍 **Root Cause Detection** - Identifies the most likely causes of failures
- 💡 **Actionable Insights** - Get practical next steps to fix issues
- 🎯 **Pattern Recognition** - Spots repeated issues and suspicious patterns

## Architecture

The application consists of:
- **Backend**: FastAPI server with LangChain for LLM orchestration
- **Frontend**: Clean HTML/JavaScript UI for file uploads
- **LLM**: OpenAI GPT-4o-mini for log analysis

## Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. Clone the repository or navigate to the project directory:

```bash
cd loganalyzer
```

2. Create a virtual environment:

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your OpenAI API key:

```bash
# On Linux/Mac
cp .env.example .env

# On Windows
copy .env.example .env
```

Then edit the `.env` file and replace `sk-proj-...` with your actual OpenAI API key:

```
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

Get your API key from: https://platform.openai.com/api-keys

## Running the Application

Start the server:

```bash
python app.py
```

Or use uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: **http://localhost:8000**

## Usage

1. Open your browser and navigate to `http://localhost:8000`
2. Click "Choose Log File" and select a `.txt` log file
3. Click "Analyze Logs"
4. Wait for the AI to process your logs (usually 10-30 seconds)
5. Review the analysis results with identified errors, root causes, and suggested fixes

## Testing

A sample log file is included in `sample_log.txt`. You can use this to test the application:

1. Start the server
2. Upload `sample_log.txt`
3. Review the analysis

## API Endpoints

### `GET /`
Returns the main HTML interface

### `POST /analyze`
Analyzes an uploaded log file

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (text/plain)

**Response:**
```json
{
  "analysis": "Detailed analysis of the logs..."
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "openai_api_key_configured": true
}
```

## How It Works

1. **File Upload**: User uploads a `.txt` log file through the web interface
2. **Text Splitting**: Large logs are split into chunks (2000 characters with 200 character overlap)
3. **LLM Analysis**: Each chunk is analyzed by GPT-4o-mini using a specialized prompt
4. **Results Aggregation**: Individual analyses are combined into a comprehensive report
5. **Display**: Results are shown in the web interface

## Customization

### Adjusting Chunk Size

Edit the `split_logs()` function in `app.py`:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,  # Adjust this value
    chunk_overlap=200  # Adjust overlap
)
```

### Changing the AI Model

Edit the `llm` initialization in `app.py`:

```python
llm = ChatOpenAI(
    temperature=0.2,
    model_name="gpt-4o"  # or "gpt-3.5-turbo"
)
```

### Modifying the Analysis Prompt

Edit the `log_analysis_prompt` template in `app.py` to customize what the AI looks for.

## Extending the Application

Potential enhancements:

- **Vector Search**: Use embeddings for very large log files
- **Historical Analysis**: Store and compare past incidents
- **Log Type Detection**: Adapt prompts for different log formats (nginx, apache, etc.)
- **Real-time Streaming**: Analyze logs as they're generated
- **Multi-file Support**: Analyze multiple log files together
- **Export Results**: Download analysis as PDF or JSON

## Troubleshooting

### "OpenAI API key not configured"
Make sure you've set the `OPENAI_API_KEY` environment variable before starting the server.

### "Module not found" errors
Ensure you've activated the virtual environment and installed all requirements:
```bash
pip install -r requirements.txt
```

### Analysis takes too long
For very large log files, consider:
- Reducing chunk_size
- Using a faster model (gpt-3.5-turbo)
- Pre-filtering logs to only include ERROR/WARN lines

## Security Notes

- Never commit your OpenAI API key to version control
- In production, use environment variables or secret management services
- Consider rate limiting the `/analyze` endpoint
- Validate and sanitize uploaded files

## License

MIT License - feel free to use this for personal or commercial projects.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
