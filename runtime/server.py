from __future__ import annotations

import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.core.engine import PreLyrEngine


app = FastAPI(
    title="PreLyr Local Runtime",
    version="0.1.0",
)

engine = PreLyrEngine()


class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ProcessResponse(BaseModel):
    optimized_text: str
    original_tokens: int
    optimized_tokens: int
    token_reduction_percentage: float
    operations: list[str]
    reason: str
    processing_time_ms: float


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "PreLyr Local Runtime",
    }


@app.post("/process", response_model=ProcessResponse)
def process(request: ProcessRequest):
    start = time.perf_counter()

    try:
        result = engine.process(request.text)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="PreLyr processing failed.",
        ) from exc

    processing_time_ms = (
        time.perf_counter() - start
    ) * 1000

    return ProcessResponse(
        optimized_text=result.context.optimized_text,
        original_tokens=result.context.original_tokens,
        optimized_tokens=result.context.optimized_tokens,
        token_reduction_percentage=(
            result.context.token_reduction_percentage
        ),
        operations=[
            operation.value
            for operation in result.decision.operations
        ],
        reason=result.decision.reason,
        processing_time_ms=round(
            processing_time_ms,
            2,
        ),
    )