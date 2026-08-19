class DocumentClassifier:
    """
    Classifies OCR text into a supported document type.
    """

    INSURANCE = "insurance_policy"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    RESUME = "resume"
    BANK_STATEMENT = "bank_statement"
    MEDICAL_REPORT = "medical_report"
    UNKNOWN = "unknown"

    KEYWORDS = {
        INSURANCE: [
            "policy number",
            "insurance company",
            "premium amount",
            "sum insured",
            "claim number",
        ],
        INVOICE: [
            "invoice number",
            "invoice date",
            "total due",
            "order number",
            "tax",
        ],
        RECEIPT: [
            "receipt",
            "payment received",
            "cash",
            "paid",
        ],
        RESUME: [
            "education",
            "experience",
            "skills",
            "objective",
            "certifications",
        ],
        BANK_STATEMENT: [
            "statement period",
            "account number",
            "available balance",
            "transaction",
        ],
        MEDICAL_REPORT: [
            "patient",
            "doctor",
            "diagnosis",
            "hospital",
            "prescription",
        ],
    }

    @classmethod
    def classify(cls, text: str) -> str:

        text = text.lower()

        for document_type, keywords in cls.KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return document_type

        return cls.UNKNOWN