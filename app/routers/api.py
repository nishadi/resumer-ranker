import csv
import io
import logging
from fastapi import APIRouter, UploadFile, File, Form, Response
from typing import List

from utils.file_utils import extract_text_from_file
from schemas.scoring_criteria import Criteria
from services.llm_service import extract_job_criteria, score_resume

router = APIRouter()


@router.post(
    "/extract-criteria",
    summary="Extract Ranking Criteria from Job Description",
    description=(
            "This endpoint accepts a job description file (PDF or DOCX) as multipart/form-data "
            "and extracts key ranking criteria. The response is a structured JSON object containing "
            "the extracted criteria."
    ),
    response_model=Criteria,
    response_description="A structured JSON object containing the extracted ranking criteria.",
    responses={
        200: {
            "description": "Criteria extracted successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "criteria": [
                            "Must have certification XYZ",
                            "5+ years of experience in Python development",
                            "Strong background in Machine Learning"
                        ]
                    }
                }
            },
        },
        400: {
            "description": "Bad Request - Possibly due to an invalid or corrupted file.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unsupported file format. Only PDF and DOCX are supported."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - Something went wrong on the server side."
        }
    }
)
async def extract_criteria(
        job_description_file: UploadFile = File(..., description="Job description file in PDF or DOCX format.")
) -> Criteria:
    """
    Extract ranking criteria from a job description file.

    This method processes an uploaded job description file (PDF or DOCX),
    extracts the text content, and uses an LLM service to identify key
    ranking criteria that can be used for resume evaluation.

    Args:
        job_description_file (UploadFile): The uploaded job description file
            in PDF or DOCX format.

    Returns:
        Criteria: A structured object containing the extracted criteria list.

    Raises:
        HTTPException: If the file format is unsupported or if text extraction fails.
    """

    # Read the entire contents of the uploaded file
    contents = await job_description_file.read()
    logging.info(f"Processing job description from file: {job_description_file.filename}")

    # Convert file contents to text based on file extension
    job_description_text = extract_text_from_file(contents, job_description_file.filename)

    # Use AI model to extract structured criteria from plain text
    criteria = extract_job_criteria(job_description_text)

    logging.info("Successfully extracted job criteria")
    return criteria


@router.post(
    "/score-resumes",
    summary="Score multiple resumes based on provided criteria",
    description="""
        This endpoint accepts a list of criteria and multiple resume files (PDF or DOCX),
        processes each resume, scores them against the provided criteria, and returns
        a CSV file containing the scores for each candidate.
    """,
    response_description="CSV file with resume scores",
    responses={
        200: {
            "description": "Successfully processed and scored resumes",
            "content": {
                "text/csv": {
                    "example": "Candidate Name,Certification XYZ,Python Experience,Machine "
                               "Learning,Total Score\nJohn Doe,5,4,4,13\nJane Smith,4,3,5,12\n"
                               "Alan Brown,3,5,4,12"
                }
            }
        },
        400: {
            "description": "Bad Request - Possibly due to an invalid or corrupted file.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unsupported file format. Only PDF and DOCX are supported."
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - Something went wrong on the server side."
        }
    }

)
async def score_resumes(
        criteria: List[str] = Form(..., description="Criteria to score against"),
        file_list: List[UploadFile] = File(..., description="Resume files (PDF or DOCX)")
) -> Response:
    """
    Score multiple resume files against provided evaluation criteria.

    This method processes a batch of resume files, extracts text from each,
    and evaluates them against the provided criteria. It generates a CSV file
    containing scores for each resume across all criteria, along with total scores.

    Args:
        criteria (List[str]): List of criteria descriptions to score resumes against.
        file_list (List[UploadFile]): List of resume files in PDF or DOCX format.

    Returns:
        Response: A CSV file response containing the scoring results with:
            - Candidate names
            - Individual scores for each criterion
            - Total score for each candidate

    Raises:
        HTTPException: If any file format is unsupported or if text extraction fails.
    """

    # Generate the resume scores
    resume_scores = []
    for resume_file in file_list:
        # Extract resume content
        file_bytes = await resume_file.read()
        resume_content = extract_text_from_file(file_bytes, resume_file.filename)

        # Score resume
        logging.info(f"Scoring resume from file: {resume_file.filename}")
        resume_score = score_resume(criteria, resume_content)

        # Build score dictionary
        scores_by_criterion = {
            criterion_score.criterion: criterion_score.score
            for criterion_score in resume_score.criterion_scores
        }

        # Calculate total score
        total_score = sum(scores_by_criterion.values())

        # Create final record with candidate name and scores
        resume_scores.append({
            'Candidate Name': resume_score.candidate_name,
            **scores_by_criterion,
            'Total Score': total_score
        })

        logging.info("Successfully scored the resume")

    # Generate CSV content from resume scores if there are any scores
    csv_content = ""
    if resume_scores:
        # Create a string buffer to hold CSV data
        buffer = io.StringIO()

        # Set up CSV writer with field names from the first resume score
        writer = csv.DictWriter(buffer, fieldnames=list(resume_scores[0].keys()))

        # Write header row and all data rows
        writer.writeheader()
        writer.writerows(resume_scores)

        # Get the complete CSV content as a string
        csv_content = buffer.getvalue()

    return Response(content=csv_content, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=resume-scoring.csv"})
