from app.ai.chunking import TextChunker
from app.ai.embeddings import EmbeddingService


text = """
This is a sample insurance document.
The policy number is POL-12345.
The insured name is John Smith.
The policy starts on January 1, 2026.
The policy expires on December 31, 2026.
The total premium is 1500 dollars.
Coverage includes property and liability protection.
"""

chunker = TextChunker(
    chunk_size=100,
    chunk_overlap=20,
)

chunks = chunker.split_text(text)

print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    embedding = EmbeddingService.generate_embedding(chunk)

    print(f"\nChunk {index}")
    print("Text:", chunk)
    print("Embedding dimensions:", len(embedding))