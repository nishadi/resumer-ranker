# Resume Ranking API

## Overview

This project implements two REST API endpoints using FastAPI to automate the resume ranking process based on job descriptions. It addresses two main tasks:

1.  **Extract Ranking Criteria**:  Extracts key ranking criteria from a job description (PDF or DOCX).
2.  **Score Resumes**: Scores resumes (PDF or DOCX) against the extracted criteria and generates a score sheet in CSV format.

This solution leverages Large Language Models (LLMs) to process text and identify relevant information, demonstrating capabilities in text extraction, data processing, and API development.

## Features

### Endpoint 1: Extract Ranking Criteria from Job Description

*   **Endpoint:** `POST /extract-criteria`
*   **Functionality:**
    *   Accepts a job description file (PDF or DOCX) via multipart form-data.
    *   Extracts text from the uploaded file.
    *   Utilizes an LLM to identify and extract key ranking criteria (skills, certifications, experience, qualifications).
    *   Returns a structured JSON response containing a list of extracted criteria.
*   **Input Payload (Multipart Form-Data):**

    ```json
    {
      "file": "<uploaded_job_description.pdf>"
    }
    ```

*   **Output Payload (JSON):**

    ```json
    {
      "criteria": [
        "Must have certification XYZ",
        "5+ years of experience in Python development",
        "Strong background in Machine Learning"
      ]
    }
    ```

*   **Swagger UI:**  Accessible at `/docs` after running the application, providing interactive documentation and testing capabilities for this endpoint.

### Endpoint 2: Score Resumes Against Extracted Criteria

*   **Endpoint:** `POST /score-resumes`
*   **Functionality:**
    *   Accepts a list of ranking criteria as strings and multiple resume files (PDF or DOCX) via multipart form-data.
    *   Extracts text from each uploaded resume file.
    *   Utilizes an LLM to assess each resume against the provided criteria.
    *   Assigns scores (0-5 scale) for each criterion based on presence and relevance in the resume.
    *   Calculates a total score for each candidate.
    *   Generates and returns an Excel (XLSX) or CSV file containing candidate names, individual criterion scores, and total scores.
*   **Input Payload (Multipart Form-Data):**

    ```json
    {
      "criteria": [
        "Must have certification XYZ",
        "5+ years of experience in Python development",
        "Strong background in Machine Learning"
      ],
      "files": [
        "<uploaded_resume_1.pdf>",
        "<uploaded_resume_2.docx>",
        "<uploaded_resume_3.pdf>"
      ]
    }
    ```

*   **Output Payload (Excel/CSV Sheet):**

    ```
    Candidate Name	Certification XYZ	Python Experience	Machine Learning	Total Score
    John Doe	5	4	4	13
    Jane Smith	4	3	5	12
    Alan Brown	3	5	4	12
    ```

*   **Swagger UI:** Accessible at `/docs` after running the application, providing interactive documentation and testing capabilities for this endpoint.

## Technologies 

*   **Programming Language:** Python (Tested with Python3)
*   **Framework:** FastAPI
*   **LLM Library:**  OpenAI SDK
*   **Document Parsing:** PyPDF2, python-docx
*   **Asynchronous Operations:** `async` and `await` for efficient API handling.
*   **Swagger UI:** Built-in documentation and interactive API testing.

## Setup Instructions

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/nishadi/resumer-ranker.git
    cd resume-ranker
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**

    *   You may need to set environment variables for your LLM API key.
    *   For example, if using OpenAI, set `OPENAI_API_KEY` environment variable.
    *   Refer to the LLM library documentation for specific environment variable names.

    ```bash
    # Example for OpenAI (replace YOUR_API_KEY with your actual API key)
    export OPENAI_API_KEY=YOUR_API_KEY  # On Linux/macOS
    set OPENAI_API_KEY=YOUR_API_KEY     # On Windows
    ```

5.  **Run the application:**

    ```bash
    cd app
    python -m uvicorn main:app --port 8000
    ```

6.  **Access Swagger UI:**

    *   Open your browser and navigate to `http://127.0.0.1:8000/docs` or `http://localhost:8000/docs` to access the Swagger UI documentation.

## Usage Instructions

1.  **Swagger UI:** The easiest way to interact with the API is through the Swagger UI at `http://127.0.0.1:8000/docs`. You can directly test both endpoints by uploading files and providing necessary inputs.

2.  **Command-line using `curl` (Examples):**

    **Task 1: Extract Criteria**

    ```bash
    curl -X POST \
      -H "Content-Type: multipart/form-data" \
      -H 'accept: application/json' \
      -F 'job_description_file=@Software Engineer Job Description.pdf;type=application/pdf' \
      http://127.0.0.1:8000/extract-criteria
    ```

    **Task 2: Score Resumes**

    ```bash
    curl -X POST \
      -H 'accept: application/json' \
      -H "Content-Type: multipart/form-data" \
      -F "criteria='[\"Must have certification XYZ\", \"5+ years of experience in Python development\", \"Strong background in Machine Learning\"]'" \
      -F "file_list=@/path/to/your/resume1.pdf" \
      -F "file_list=@/path/to/your/resume2.docx" \
      http://127.0.0.1:8000/score-resumes
    ```
    *   **Note:**  Adjust file paths and criteria list in the `curl` commands as needed.

## Author

Nishadi Kirielle
