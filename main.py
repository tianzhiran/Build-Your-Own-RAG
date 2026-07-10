from embedding import load_or_create_embeddings
from retrieval import build_index
from retrieval import retrieve
from prompt_builder import build_prompt
from llm import generate_answer
from utils import load_knowledge


def main():

    print("=" * 50)
    print("Mini RAG V4")
    print("=" * 50)

    # Step 1
    knowledge = load_knowledge()

    # Step 2
    embeddings = load_or_create_embeddings(knowledge)

    # Step 3
    index = build_index(embeddings)

    print("\nSystem Ready!")

    while True:

        question = input("\nQuestion: ")

        if question.lower() == "exit":
            print("Bye!")
            break

        # Step 4
        contexts = retrieve(
            question,
            index,
            knowledge
        )

        # Step 5
        prompt = build_prompt(
            contexts,
            question
        )

        # Step 6
        answer = generate_answer(prompt)

        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()