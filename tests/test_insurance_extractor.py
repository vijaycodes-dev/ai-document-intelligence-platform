from app.ai.ocr import OCRService
from app.ai.extractors.insurance import InsuranceExtractor

text = OCRService.extract_text(
    "uploads/0b1c8f98-e6ff-4fd2-bb9d-ffe70c1535a2.pdf"
)

metadata = InsuranceExtractor.extract(text)

print("=" * 60)
print("Insurance Metadata")
print("=" * 60)

for key, value in metadata.items():
    print(f"{key}: {value}")
    


# from app.ai.ocr import OCRService
# from app.ai.extractors.invoice import InvoiceExtractor

# text = OCRService.extract_text(
#     "uploads/b4c70ed5-ad4f-4410-84e4-d46091063424.pdf"
# )

# metadata = InvoiceExtractor.extract(text)

# print("=" * 60)
# print("Invoice Metadata")
# print("=" * 60)

# for key, value in metadata.items():
#     print(f"{key}: {value}")