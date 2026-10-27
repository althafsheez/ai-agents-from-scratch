from agent.runner import run_agent_openai

def test_agent():
    result = run_agent_openai(
        "Explain what Python is in one sentence. Do not use any tools."
    )

    print("\nAgent Response:")
    print(result)


if __name__ == "__main__":
    test_agent()