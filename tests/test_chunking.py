from app.ai.chunking import TextChunker


text = """
Invoice number INV-3337.
Invoice date January 25, 2016.
The customer purchased several products.
The total amount due is 93.50.
Payment is due by January 31, 2016.
"""

chunker = TextChunker(
    chunk_size=100,
    chunk_overlap=20,
)

chunks = chunker.split_text(text)

print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    print(f"\nChunk {index}:")
    print(chunk)