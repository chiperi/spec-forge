"""Data models (pydantic)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class Phase(str, Enum):
    spec = "spec"
    plan = "plan"
    design = "design"
    tasks = "tasks"
    validate = "validate"
    deploy = "deploy"


class InterviewAnswers(BaseModel):
    """Interview answers used to build the render context."""

    project_name: str
    stack: str = "python"
    summary: str = ""
