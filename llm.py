from openai import OpenAI

from config import (
    API_KEY,
    BASE_URL,
    LLM_MODEL
)

# Create OpenAI Client
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


def generate_answer(prompt):
    """
    Generate answer from LLM.
    """

    response = client.chat.completions.create(

        model=LLM_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    answer = response.choices[0].message.content

    return answer