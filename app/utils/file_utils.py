import PyPDF2
from fastapi import HTTPException
from docx import Document
from io import BytesIO
import logging


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text content from a PDF file provided as bytes.

    This function processes a PDF file in memory and extracts all text content
    from each page, joining them with newlines.

    Args:
        file_bytes (bytes): Raw binary content of the PDF file.

    Returns:
        str: Extracted text from all pages of the PDF, joined with newlines.

    Raises:
        Exception: If text extraction fails for any reason, with a generic error message.
    """

    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        error_message = "Error extracting text from PDF."
        logging.error(f"{error_message} : {str(e)}")
        raise HTTPException(status_code=500, detail=error_message)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text content from a DOCX file provided as bytes.

    This function processes a DOCX file in memory and extracts all text content
    from each paragraph, joining them with newlines.

    Args:
        file_bytes (bytes): Raw binary content of the DOCX file.

    Returns:
        str: Extracted text from all paragraphs, joined with newlines.

    Raises:
        Exception: If text extraction fails for any reason, with a generic error message.
    """

    try:
        doc = Document(BytesIO(file_bytes))
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        error_message = "Error extracting text from the document."
        logging.error(f"{error_message} : {str(e)}")
        raise HTTPException(status_code=500, detail=error_message)


def extract_text_from_file(file_bytes: bytes, file_name: str) -> str:
    """
    Extract text from a file based on its extension (PDF or DOCX).

    This function determines the appropriate extraction method based on the file extension
    and delegates to the corresponding specialized function.

    Args:
        file_bytes (bytes): Raw binary content of the file.
        file_name (str): Original filename with extension, used to determine file type.

    Returns:
        str: Extracted text content from the file.

    Raises:
        HTTPException: With status code 400 if the file format is not supported.
        Exception: If text extraction fails (propagated from the specific extraction function).
    """
    if file_name.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif file_name.lower().endswith('.docx'):
        return extract_text_from_docx(file_bytes)
    else:
        error_message = "Unsupported file format. Only PDF and DOCX are supported."
        logging.error(error_message)
        raise HTTPException(status_code=400, detail=error_message)
