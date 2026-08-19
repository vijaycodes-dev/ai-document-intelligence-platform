from app.ai.classifier import DocumentClassifier
from app.ai.extractors.insurance import InsuranceExtractor
from app.ai.extractors.invoice import InvoiceExtractor


class ExtractorManager:

    @staticmethod
    def extract(text: str):

        document_type = DocumentClassifier.classify(text)

        if document_type == DocumentClassifier.INSURANCE:
            return InsuranceExtractor.extract(text)

        if document_type == DocumentClassifier.INVOICE:
            return InvoiceExtractor.extract(text)

        return {}