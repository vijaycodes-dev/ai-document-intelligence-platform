from app.ai.classifier import DocumentClassifier
from app.ai.ocr import OCRService

text = OCRService.extract_text(
    "uploads/0b1c8f98-e6ff-4fd2-bb9d-ffe70c1535a2.pdf"
)

document_type = DocumentClassifier.classify(text)

print("=" * 50)
print(f"Document Type : {document_type}")
print("=" * 50)