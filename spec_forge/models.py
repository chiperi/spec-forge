"""Моделі даних (pydantic)."""

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
    """Відповіді інтервʼю, з яких будується контекст рендеру."""

    project_name: str
    stack: str = "python"
    summary: str = ""
