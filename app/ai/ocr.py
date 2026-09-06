import pymupdf


class OCRService:

    @staticmethod
    def extract_text(file_path: str) -> str:
        try:
            document = pymupdf.open(file_path)

            text = ""

            for page in document:
                text += page.get_text()

            document.close()

        except Exception as e:
            raise RuntimeError(
                "Unable to extract text from PDF."
            ) from e

        if not text.strip():
            raise ValueError(
                "No text could be extracted from the document."
            )

        return text.strip()