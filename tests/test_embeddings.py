from app.ai.embeddings import EmbeddingService


text = "Invoice payment is due within 30 days."

embedding = EmbeddingService.generate_embedding(text)

print("Embedding dimensions:", len(embedding))
print("First 5 values:", embedding[:5])