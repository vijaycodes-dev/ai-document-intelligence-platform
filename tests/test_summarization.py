from app.services.summarization import summarize_text


def main():
    document = """
    Invoice Number: INV-3337
    Invoice Date: January 25, 2016
    Due Date: January 31, 2016
    Service: Web Design
    Subtotal: $85.00
    Tax: $8.50
    Total Due: $93.50
    """

    summary = summarize_text(document)

    print("\nSummary:")
    print(summary)


if __name__ == "__main__":
    main()