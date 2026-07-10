def build_prompt(contexts, question):
    """
    Build prompt for the LLM.

    Args:
        contexts (list[str]): Retrieved knowledge.
        question (str): User question.

    Returns:
        str: Prompt sent to the LLM.
    """

    context = "\n".join(contexts)

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question ONLY using the knowledge below.

Knowledge:
{context}

Question:
{question}

If the answer cannot be found in the knowledge,
reply exactly:

Knowledge not found.
"""

    return prompt