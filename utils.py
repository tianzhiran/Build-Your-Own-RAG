from config import KNOWLEDGE_FILE


def load_knowledge():
    """
    Load knowledge base from txt file.
    """

    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        knowledge = f.readlines()

    knowledge = [line.strip() for line in knowledge]

    return knowledge