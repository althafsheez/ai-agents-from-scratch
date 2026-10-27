import os
import json

from agent.sandbox.manager import SandboxManager
from langfuse.openai import OpenAI
from langfuse import observe
from dotenv import load_dotenv
from .tools.registry import TOOLS
import time 
from .prompts import get_system_prompt  
from .tools.memory import load_memory, save_memory

# Load environment variables
load_dotenv()

# Initialize Gemini through OpenAI-compatible API
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
    timeout=60,
)


def save_message(message):
    """Append one message to the conversation history."""

    if hasattr(message, "model_dump"):
        message = message.model_dump()

    with open("history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(message) + "\n")

from langfuse import observe

@observe(name="data-analytics-agent", as_type="agent")
def run_agent_openai(goal: str, max_steps: int = 13) -> str:
    """Run an AI agent with tool calling."""
    #load memory from agents.md file
    memory = load_memory()
    sandbox_manager = SandboxManager()
    sandbox_manager.upload_file("agent/workspace/iris.csv")
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
            "content": get_system_prompt(memory)
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
        
        if sandbox_manager._sandbox is not None:
            sandbox_manager._sandbox.set_timeout(300)  # Reset timeout to 5 minutes on each step

        print(f"\n--- Step {step + 1} ---")
        start = time.perf_counter()

        response = client.chat.completions.create(
        model="gemini-3.5-flash-lite",
        tools=openai_tools,
        messages=messages,
        temperature=0,
        )

        elapsed = time.perf_counter() - start
        print(f"API response time: {elapsed:.2f} seconds")

        # Get assistant response
        message = response.choices[0].message

        # Save assistant message
        messages.append(message)
        save_message(message)

        # If no tools requested, finish also if there is any memory to save , save it to agents.md file
        if not message.tool_calls:
            final_text = message.content or "Task complete."

            if "MEMORY UPDATE:" in final_text:
                lines = final_text.split("\n")

                updates = [
                    line.replace("MEMORY UPDATE:", "").strip()
                    for line in lines
                    if line.strip().startswith("MEMORY UPDATE:")
                ]

                if updates:
                    existing = load_memory()
                    updated = existing + "\n" + "\n".join(updates)

                    save_memory(updated)

                    print(f"[Memory updated with {len(updates)} new fact(s)]")

            return final_text

        # Execute requested tools
        for tc in message.tool_calls:

            name = tc.function.name

            print(f"Calling tool: {name}")

            try:
                args = json.loads(tc.function.arguments)

                if name not in TOOLS:
                    raise ValueError(f"Unknown tool: {name}")

                if name in ["execute_code", "generate_visualization"]:
                    result = TOOLS[name]["function"](
                        **args,
                        sandbox_manager=sandbox_manager,
                    )
                else:
                    result = TOOLS[name]["function"](**args)

            except Exception as e:
                result = json.dumps({
                    "error": str(e)
                })

            # Add tool result to conversation
            result_text = result if isinstance(result, str) else json.dumps(result)
            
            MAX_TOOL_OUTPUT = 2000
            
            if len(result_text) > MAX_TOOL_OUTPUT:
                result_text = result_text[:MAX_TOOL_OUTPUT] + "\n[Output truncated]"
            
            tool_message = {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_text
            }

            messages.append(tool_message)
            save_message(tool_message)

    return "Max steps reached."