from app.ai.classifier import DocumentClassifier
from app.ai.ocr import OCRService


def test_document_classifier(sample_pdf):
    text = OCRService.extract_text(sample_pdf)
    document_type = DocumentClassifier.classify(text)

    assert document_type is not None
