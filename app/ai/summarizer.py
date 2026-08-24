class DocumentSummarizer:

    @staticmethod
    def summarize(text: str) -> str:
        if not text or not text.strip():
            return "No text available for summarization."

        # Temporary implementation.
        # We will replace this with an LLM later.
        words = text.split()

        if len(words) <= 100:
            return text.strip()

        summary_words = words[:100]

        return " ".join(summary_words) + "..."