
import os
from langfuse.openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
    timeout=60,
)

MODEL = "gemini-3.5-flash-lite"

DATA_ANALYSIS_PROMPT = """
Analyze the following data:

{data}

Your job is to answer the following question:

{prompt}
"""


def analyze_data(prompt: str, data: str) -> str:
    """Analyze data using an LLM."""

    formatted_prompt = DATA_ANALYSIS_PROMPT.format(
        data=data,
        prompt=prompt
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": formatted_prompt}
        ],
    )

    return (
        response.choices[0].message.content
        or "No analysis could be generated"
    )