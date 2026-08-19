import re


class InsuranceExtractor:

    @staticmethod
    def extract(text: str):

        metadata = {}

        patterns = {
            "policy_number": r"Policy Number\s+([A-Z0-9]+)",
            "insured_name": r"Insured Name\s+(.+)",
            "premium_amount": r"Premium Amount\s+(INR\s[\d,]+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text)

            if match:
                metadata[key] = match.group(1).strip()

        return metadata