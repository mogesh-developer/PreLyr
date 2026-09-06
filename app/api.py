from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.sdk import PreLyr
from app.llm.mock import MockLLMProvider


app = FastAPI(
    title="PreLyr API",
    version="0.1.0",
    description="Adaptive NLP middleware for LLM applications.",
)


class OptimizeRequest(BaseModel):
    text: str


class GenerateRequest(BaseModel):
    text: str


class OptimizeResponse(BaseModel):
    original_text: str
    optimized_text: str
    operations_applied: list[str]
    original_tokens: int
    optimized_tokens: int
    token_reduction_percentage: float


@app.get("/", response_class=HTMLResponse)
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PreLyr v0.1.0 — Adaptive NLP Middleware Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --card-bg: rgba(18, 26, 43, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --accent-purple: #8b5cf6;
            --accent-indigo: #6366f1;
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --input-bg: #0d1322;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(139, 92, 246, 0.15) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.12) 0%, transparent 45%);
            background-attachment: fixed;
        }

        header {
            padding: 1.5rem 2rem;
            border-bottom: 1px solid var(--card-border);
            backdrop-filter: blur(12px);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .logo-group {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.25rem;
            color: #fff;
            box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4);
        }

        .brand-title {
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(to right, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .badge-version {
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.4);
            color: #c4b5fd;
            font-size: 0.75rem;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-weight: 600;
        }

        .status-tag {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            color: var(--text-muted);
        }

        .dot-green {
            width: 8px;
            height: 8px;
            background: var(--accent-emerald);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-emerald);
        }

        main {
            flex: 1;
            max-width: 1280px;
            width: 100%;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }

        @media (max-width: 900px) {
            main {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-title {
            font-size: 1.15rem;
            font-weight: 600;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        textarea {
            width: 100%;
            height: 220px;
            background: var(--input-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1rem;
            color: #e5e7eb;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            resize: vertical;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        textarea:focus {
            border-color: var(--accent-purple);
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25);
        }

        .btn-group {
            display: flex;
            gap: 1rem;
        }

        button {
            flex: 1;
            padding: 0.85rem 1.5rem;
            border-radius: 10px;
            border: none;
            font-family: 'Outfit', sans-serif;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-indigo));
            color: #fff;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border);
            color: var(--text-main);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }

        .metric-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }

        .metric-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }

        .metric-value {
            font-size: 1.35rem;
            font-weight: 700;
            color: #fff;
        }

        .metric-value.highlight {
            color: var(--accent-emerald);
        }

        .ops-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .op-badge {
            background: rgba(6, 182, 212, 0.15);
            border: 1px solid rgba(6, 182, 212, 0.3);
            color: #7dd3fc;
            padding: 0.3rem 0.7rem;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .output-box {
            background: var(--input-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1rem;
            color: #e5e7eb;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            min-height: 180px;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
        }

        footer {
            text-align: center;
            padding: 1.5rem;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--card-border);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-group">
            <div class="logo-icon">P</div>
            <span class="brand-title">PreLyr</span>
            <span class="badge-version">v0.1.0</span>
        </div>
        <div class="status-tag">
            <div class="dot-green"></div>
            <span>Adaptive Middleware Active</span>
        </div>
    </header>

    <main>
        <section class="card">
            <div class="card-header">
                <h2 class="card-title">Input Context</h2>
                <span style="font-size: 0.8rem; color: var(--text-muted);">Paste redundant or un-structured text</span>
            </div>
            <textarea id="inputText" placeholder="Paste your input here... Try pasting redundant text like:
Flask is a Python web framework. Flask is a Python web framework.
The database connection fails. The database connection fails."></textarea>
            
            <div class="btn-group">
                <button class="btn-primary" onclick="processText('optimize')">⚡ Optimize Context</button>
                <button class="btn-secondary" onclick="processText('generate')">🚀 Run Mock LLM</button>
            </div>
        </section>

        <section class="card">
            <div class="card-header">
                <h2 class="card-title">PreLyr Optimization Engine</h2>
            </div>

            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-label">Original Tokens</div>
                    <div class="metric-value" id="origTokens">-</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Optimized Tokens</div>
                    <div class="metric-value" id="optTokens">-</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Token Reduction</div>
                    <div class="metric-value highlight" id="reduction">-</div>
                </div>
            </div>

            <div>
                <div class="metric-label" style="margin-bottom: 0.5rem;">Applied NLP Operations</div>
                <div class="ops-list" id="opsList">
                    <span style="color: var(--text-muted); font-size: 0.85rem;">Run optimization to view decision pipeline...</span>
                </div>
            </div>

            <div>
                <div class="metric-label" style="margin-bottom: 0.5rem;">Optimized Context / Prompt Output</div>
                <div class="output-box" id="outputBox">Resulting context will be displayed here...</div>
            </div>
        </section>
    </main>

    <footer>
        PreLyr v0.1.0 • Adaptive NLP Middleware for LLM Applications
    </footer>

    <script>
        async function processText(mode) {
            const text = document.getElementById('inputText').value.trim();
            if (!text) {
                alert('Please enter text to process');
                return;
            }

            const opsList = document.getElementById('opsList');
            const outputBox = document.getElementById('outputBox');
            outputBox.innerText = 'Processing with PreLyr...';

            try {
                if (mode === 'optimize') {
                    const res = await fetch('/optimize', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text })
                    });
                    const data = await res.json();

                    document.getElementById('origTokens').innerText = data.original_tokens;
                    document.getElementById('optTokens').innerText = data.optimized_tokens;
                    document.getElementById('reduction').innerText = `${data.token_reduction_percentage.toFixed(1)}%`;

                    opsList.innerHTML = '';
                    data.operations_applied.forEach(op => {
                        const badge = document.createElement('span');
                        badge.className = 'op-badge';
                        badge.innerText = op;
                        opsList.appendChild(badge);
                    });

                    outputBox.innerText = data.optimized_text;
                } else if (mode === 'generate') {
                    const res = await fetch('/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text })
                    });
                    const data = await res.json();
                    
                    outputBox.innerText = `[LLM Response]\n${data.response}\n\n[Optimized Prompt Sent to Provider]\n${data.optimized_prompt}`;
                }
            } catch (err) {
                outputBox.innerText = 'Error processing request: ' + err.message;
            }
        }
    </script>
</body>
</html>"""


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "prelyr",
    }


@app.post("/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest):
    prelyr = PreLyr()

    result = prelyr.optimize(request.text)

    return OptimizeResponse(
        original_text=result.context.original_text,
        optimized_text=result.context.optimized_text,
        operations_applied=[
            operation.value
            for operation in result.context.operations_applied
        ],
        original_tokens=result.context.original_tokens,
        optimized_tokens=result.context.optimized_tokens,
        token_reduction_percentage=(
            result.context.token_reduction_percentage
        ),
    )


@app.post("/generate")
def generate(request: GenerateRequest):
    provider = MockLLMProvider()

    prelyr = PreLyr(
        llm_provider=provider,
    )

    result = prelyr.generate(request.text)

    return {
        "response": result,
        "optimized_prompt": provider.last_prompt,
    }