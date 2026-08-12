from fastapi import HTTPException, status


class DocumentNotFoundException(HTTPException):
    """Raised when a requested document ID does not exist in the database."""

    def __init__(self, document_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Document #{document_id} not found.',
        )


class DocumentUploadException(HTTPException):
    """Raised when an uploaded file fails validation (type, size, etc.)."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
