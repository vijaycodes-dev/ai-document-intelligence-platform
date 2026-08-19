import re


class InvoiceExtractor:

    @staticmethod
    def extract(text: str):

        metadata = {}

        patterns = {
            "invoice_number": r"Invoice Number\s+([A-Z0-9-]+)",
            "invoice_date": r"Invoice Date\s+(.+)",
            "due_date": r"Due Date\s+(.+)",
            "total_due": r"Total Due\s+\$?([\d,.]+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text)

            if match:
                metadata[key] = match.group(1).strip()

        return metadata