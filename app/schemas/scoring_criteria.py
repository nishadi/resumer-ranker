from pydantic import BaseModel
from typing import List


class Criteria(BaseModel):
    criteria: List[str]


class CriterionScore(BaseModel):
    criterion: str
    score: int


class ResumeScore(BaseModel):
    candidate_name: str
    criterion_scores: List[CriterionScore]
