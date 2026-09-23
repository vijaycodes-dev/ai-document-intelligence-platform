from app.ai.ocr import OCRService


def test_extract_text(sample_pdf):
    text = OCRService.extract_text(sample_pdf)

    assert text == "Test PDF document"
