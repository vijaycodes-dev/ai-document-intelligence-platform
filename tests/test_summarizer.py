from app.ai.summarizer import DocumentSummarizer


text = """
This is a sample insurance document.
The policy provides coverage for property damage,
liability and other insured risks.
The policy period starts on January 1, 2026
and ends on December 31, 2026.
"""

summary = DocumentSummarizer.summarize(text)

print(summary)