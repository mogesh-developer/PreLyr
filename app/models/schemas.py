from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, model_validator

class ProcessingOperation(str, Enum):
    NO_OP="NO_OP"
    CLEAN="CLEAN"
    NORMALIZE="NORMALIZE"
    STRUCTURE="STRUCTURE"
    EXTRACT="EXTRACT"
    FILTER="FILTER"
    DEDUPLICATE="DEDUPLICATE"
    SELECT_RELEVANT_CONTEXT="SELECT_RELEVANT_CONTEXT"
    COMPRESS="COMPRESS"
    CHUNK="CHUNK"
    LOCAL_EXECUTION="LOCAL_EXECUTION"
    LLM_REQUIRED="LLM_REQUIRED"

class TaskType(str, Enum):
    EXPLANATION = "EXPLANATION"
    DEBUGGING = "DEBUGGING"
    SUMMARIZATION = "SUMMARIZATION"
    EXTRACTION = "EXTRACTION"
    COMPARISON = "COMPARISON"
    GENERATION = "GENERATION"
    UNKNOWN = "UNKNOWN"

class AnalysisResult(BaseModel):
    input_text: str
    input_length: int
    sentence_count: int
    duplicate_count: int = 0
    task_type: TaskType = TaskType.UNKNOWN
    is_empty: bool = False

class ProcessingDecision(BaseModel):
    operations: list[ProcessingOperation] = Field(default_factory=list)
    reason: str

class OptimizedContext(BaseModel):
    original_text: str
    optimized_text: str

    original_length: int = 0
    optimized_length: int = 0

    original_tokens: int = 0
    optimized_tokens: int = 0
    token_reduction_percentage: float = 0.0

    operations_applied: list[ProcessingOperation] = Field(
        default_factory=list
    )

    @model_validator(mode="before")
    @classmethod
    def calculate_lengths(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "original_length" not in data or data["original_length"] is None:
                orig_text = data.get("original_text", "")
                data["original_length"] = len(orig_text) if orig_text else 0

            if "optimized_length" not in data or data["optimized_length"] is None:
                opt_text = data.get("optimized_text", "")
                data["optimized_length"] = len(opt_text) if opt_text else 0

        return data

class PreLyrResult(BaseModel):
    analysis: AnalysisResult
    decision: ProcessingDecision
    context: OptimizedContext