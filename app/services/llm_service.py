import os
import logging
from fastapi import HTTPException
from openai import OpenAI
from pydantic import BaseModel

from schemas.scoring_criteria import Criteria, ResumeScore

MODEL = "gpt-4o-2024-08-06"


def call_gpt_api(
        system_message: str, user_message: str, response_format: BaseModel
) -> str:
    """
    Call the OpenAI GPT API with structured format parsing.

    Args
        system_message: System message for the AI model
        user_message: User message for the AI model
        response_format: Pydantic model defining the expected response structure

    Returns:
        The parsed API response matching the specified format

    Raises:
        HTTPException: If the API call fails
    """

    # Initialize OpenAI client with API key from environment variables
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    try:
        # Make the API call with deterministic output (temperature=0)
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}],
            response_format=response_format,
            temperature=0.0
        )

        # Return the parsed response
        return completion.choices[0].message.parsed

    except Exception as e:
        logging.error(f"OpenAI GPT API call failed while parsing the response : {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request. Please try again later.")


def extract_job_criteria(
        job_description: str
) -> Criteria:
    """
    Extracts key ranking criteria from a job description using a language model.

    This function takes a job description as input and uses an AI assistant to identify
    and extract the essential criteria for ranking candidates, such as required skills,
    certifications, experience levels, etc.

    Args:
        job_description (str): The full text of the job description to analyze.

    Returns:
        Criteria: A structured object containing the extracted job criteria.

    Note:
            The function relies on an external API call to a language model that has been
            instructed to focus on extracting specific, measurable criteria.
    """
    # error_message = "Error: Invalid job description. Please provide a valid job description."

    # Define the system instructions for the LLM model
    system_message = f"""
    You are an expert HR assistant. 
    
    If the user provided text is a valid job description, extract the key ranking criteria from 
    the job description. Focus on required skills, certifications, experience levels, qualifications, 
    and competencies. Return a list of clear, concise criteria statements without numbering or bullet points.
    Each criterion should be specific and measurable. 
    Make sure to extract all key ranking criteria written in the job description along with all the keywords such as 'essential', 'must have'.
    
    If the user provided text is a not a valid job description, return an empty list.
    Invalid job descriptions can include (but is not limited to):  resumes, cvs, cover letters, portfolios,
    work samples, training manuals, job offer letters, company policies, and handbooks.     
    """

    # Pass the job description as the user message to be analyzed
    user_message = job_description

    # Send the prompt to the LLM API and get the structured response
    response = call_gpt_api(system_message, user_message, Criteria)

    # Check if an empty list is returned
    if len(response.criteria) == 0:
        error_message = "Invalid file. Please upload a valid job description."
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    return response


def score_resume(
        resume_criteria: list, resume_content: str
) -> ResumeScore:
    """
    Evaluates a resume against specified job criteria using an external LLM.

    Args:
        resume_criteria: List of job requirements to evaluate the resume against
        resume_content: The complete text of the candidate's resume

    Returns:
        ResumeScore: An object containing the evaluation scores and candidate information
    """

    # Convert criteria list to a string with each criterion on a new line
    criteria_str = "\n".join(resume_criteria)

    # Create the system prompt for the LLM
    system_message = f"""
    You are an expert HR assistant tasked with evaluating resumes against specific job criteria. 
    For each criterion, assign a score from 0 (lowest match) to 5 (highest match).

    Scoring Guidelines for each criterion can be found here:

    Skills (Hard Skills):
        - Recency and Experience: Prioritize recent experience. More years of relevant experience generally lead to higher scores.
            - 5+ years recent experience: High score (e.g., 4-5).
            - 2-3 years recent experience: Medium score (e.g., 2-3).
            - Past experience (less recent) or limited experience: Lower score (e.g., 0-2).
        - Keywords and Related Experience: Consider keywords and related experience even if the exact skill isn't explicitly stated.

    Soft Skills (e.g., Communication):
        - Evidence in Resume: Look for evidence of the soft skill throughout the resume (e.g., action verbs, descriptions of responsibilities, project examples).
        - Context and Impact: Assess how the candidate demonstrates the soft skill in their past roles and the impact of that skill. For example, "Led team presentations" suggests communication skills.
        - Keywords: Consider keywords associated with the soft skill (e.g., "collaborative," "client-facing," "presentation skills").

    Qualifications/Certifications:
        - Hierarchy: Generally, higher qualifications score higher, but relevance to the job is key.
            - PhD: Highest score (if relevant).
            - Master's Degree: High score (if relevant).
            - Bachelor's Degree: Medium score (if relevant).
            - Diploma/Certifications: Score based on relevance and level of specialization. Industry-recognized certifications may be highly valuable.
        - Relevance: Prioritize qualifications directly related to the job requirements.
        - Institution: Consider the reputation of the institution granting the qualification.

        Additionally, please extract the candidate’s name from the resume before proceeding with the evaluation.

        Given a resume, evaluate the candidate ONLY against the following criteria:

        {criteria_str}

        For each criterion, provide a score between 0 and 5. 
        Apply your HR expertise to interpret these guidelines and assign scores.
        
        In the response, make sure that the CriterionScore.criterion exactly matches the provided criterion.
        """

    # Create the user message containing the resume content
    user_message = f"Resume: {resume_content}"

    # Send the prompt to the LLM API and return the structured response
    return call_gpt_api(system_message, user_message, ResumeScore)
