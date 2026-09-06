from app.ai.llm import generate_response


def main():
    prompt = """
    Answer the question using only the information provided.

    Invoice Number: INV-3337
    Due Date: January 31, 2016
    Total Due: $93.50

    Question: What is the total amount due?
    """

    answer = generate_response(prompt)

    print("\nLLM Response:")
    print(answer)


if __name__ == "__main__":
    main()