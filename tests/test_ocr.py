from app.ai.ocr import OCRService

text = OCRService.extract_text(
    "uploads/b4c70ed5-ad4f-4410-84e4-d46091063424.pdf"
)

print(text)