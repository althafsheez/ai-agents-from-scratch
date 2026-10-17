import os
import json

from openai import OpenAI
from dotenv import load_dotenv
from .tools import TOOLS
import time 
from .prompts import SYSTEM_PROMPT


# Load environment variables
load_dotenv()

# Initialize Gemini through OpenAI-compatible API
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=20.0,
    max_retries=0
)


def save_message(message):
    """Append one message to the conversation history."""

    if hasattr(message, "model_dump"):
        message = message.model_dump()

    with open("history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(message) + "\n")


def run_agent_openai(goal: str, max_steps: int = 1000) -> str:
    """Run an AI agent with tool calling."""

    # Convert our tool registry into API tool definitions
    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
        }
        for name, tool in TOOLS.items()
    ]

    # Initialize conversation
    messages = [
        {   "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": goal
        }
    ]

    for message in messages:
        save_message(message)

    # Agent loop
    for step in range(max_steps):

        print(f"\n--- Step {step + 1} ---")
        start = time.perf_counter()

        response = client.chat.completions.create(
            model="gemini-3.5-flash-lite",
            tools=openai_tools,
            messages=messages
        )
        elapsed = time.perf_counter() - start
        print(f"API response time: {elapsed:.2f} seconds")

        # Get assistant response
        message = response.choices[0].message

        # Save assistant message
        messages.append(message)
        save_message(message)

        # If no tools requested, finish
        if not message.tool_calls:
            return message.content or "Task complete."

        # Execute requested tools
        for tc in message.tool_calls:

            name = tc.function.name

            print(f"Calling tool: {name}")

            try:
                args = json.loads(tc.function.arguments)

                if name not in TOOLS:
                    raise ValueError(f"Unknown tool: {name}")

                result = TOOLS[name]["function"](**args)

            except Exception as e:
                result = json.dumps({
                    "error": str(e)
                })

            # Add tool result to conversation
            tool_message = {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result
            }

            messages.append(tool_message)
            save_message(tool_message)

    return "Max steps reached."