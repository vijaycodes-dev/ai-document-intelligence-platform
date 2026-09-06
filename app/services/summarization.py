from app.ai.llm import generate_response


def summarize_text(
    text: str,
    metadata: dict | None = None,
) -> str:

    if not text or not text.strip():
        raise ValueError(
            "No document text available for summarization."
        )

    metadata = metadata or {}

    prompt = f"""
Summarize the following document using the OCR text and extracted metadata.

Rules:
- Use ONLY information explicitly present in the OCR text or metadata.
- Do NOT infer, assume, or invent information.
- Preserve important names, dates, amounts, identifiers, policy numbers,
  invoice numbers, and other important details.
- If OCR text and metadata contain different values, do not combine them
  into a new value.
- Keep the summary concise.
- Return 4 to 6 bullet points.
- Do not mention that OCR or metadata was used.
- Do not add information that is not present.

Extracted Metadata:
{metadata}

OCR Text:
{text}
"""

    return generate_response(prompt)