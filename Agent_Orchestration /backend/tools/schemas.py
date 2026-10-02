from pydantic import BaseModel, Field
from typing import Literal
import sqlite3

class WebSearchInput(BaseModel):
    query: str

class WebSearchOutput(BaseModel):
    results: list[str]
    sources: list[str]

class FileReadInput(BaseModel):
    path: str

class FileReadOutput(BaseModel):
    content: str

class FileWriteInput(BaseModel):
    path: str
    content: str


class FileWriteOutput(BaseModel):
    success: bool


class CodeExecutionInput(BaseModel):
    code: str
    language: Literal["python"] = "python"


class CodeExecutionOutput(BaseModel):
    stdout: str
    stderr: str
    exit_code: int


class DatabaseQueryInput(BaseModel):
    query: str


class DatabaseQueryOutput(BaseModel):
    rows: list[dict]


class APICallInput(BaseModel):
    url: str
    method: Literal["GET", "POST"]
    body: dict | None = None


class APICallOutput(BaseModel):
    status_code: int
    data: dict | list | str

class DatabaseQueryInput(BaseModel):
    query: str

class DatabaseQueryOutput(BaseModel):
    rows: list[dict]

class ReviewResult(BaseModel):
    approved: bool
    feedback: str

    score: int = Field(
        ge=1,
        le=5
    )

    failed_subtask_id: str | None = None

    confidence: float = Field(
        ge=0,
        le=1
    )