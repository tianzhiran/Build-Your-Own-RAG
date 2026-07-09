def build_prompt(context, question):
    """
    Build Prompt for LLM.
    """

    prompt = f"""
You are a helpful assistant.

Knowledge:

{context}

Question:

{question}

If the answer is not in the knowledge,
reply:

Knowledge not found.
"""

    return prompt