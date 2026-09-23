from app.ai.ocr import OCRService
from app.ai.extractors.insurance import InsuranceExtractor


def test_insurance_extractor(sample_pdf):
    text = OCRService.extract_text(sample_pdf)
    metadata = InsuranceExtractor.extract(text)

    assert isinstance(metadata, dict)
