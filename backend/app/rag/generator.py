import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4.1-mini"


def generate_answer(question: str, chunks: list[dict]) -> str:
    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"""
Source: {chunk["filename"]}
Pages: {chunk["page_start"]}-{chunk["page_end"]}

{chunk["text"]}
"""
        )

    context = "\n---\n".join(context_parts)

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a PDF question-answering assistant. "
                    "Answer questions using only the provided document context. "
                    "If the answer cannot be found in the context, say "
                    "'I couldn't find that information in the provided PDFs.' "
                    "Do not invent facts. "
                    "When possible, mention the source filename and page number."
                ),
            },
            {
                "role": "user",
                "content": f"""
Context from the user's PDFs:

{context}

Question:
{question}

Answer based only on the provided context.
""",
            },
        ],
    )

    return response.choices[0].message.content