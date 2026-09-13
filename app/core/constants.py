# Upload Settings
UPLOAD_DIRECTORY = "uploads"

# Allowed MIME Types
ALLOWED_FILE_TYPES = {
    "application/pdf",
}

# Maximum Upload Size (20 MB)
MAX_UPLOAD_SIZE = 20 * 1024 * 1024

# Document Status
DOCUMENT_STATUS_UPLOADED = "uploaded"
DOCUMENT_STATUS_PROCESSING = "processing"
DOCUMENT_STATUS_COMPLETED = "completed"
DOCUMENT_STATUS_FAILED = "failed"


# Document Processing Stages
PROCESSING_STAGE_UPLOADED = "uploaded"
PROCESSING_STAGE_OCR = "ocr"
PROCESSING_STAGE_CLASSIFICATION = "classification"
PROCESSING_STAGE_METADATA = "metadata_extraction"
PROCESSING_STAGE_EMBEDDING = "embedding"
PROCESSING_STAGE_COMPLETED = "completed"
PROCESSING_STAGE_FAILED = "failed"