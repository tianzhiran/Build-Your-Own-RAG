from rag_service import RAGService


def main():

    print("=" * 50)
    print("Mini RAG V4")
    print("=" * 50)

    rag_service = RAGService()

    print("\nSystem Ready!")

    while True:

        question = input("\nQuestion: ")

        if question.lower() == "exit":
            print("Bye!")
            break

        response = rag_service.ask(question)

        print("\nAnswer:")
        print(response.answer)


if __name__ == "__main__":
    main()
