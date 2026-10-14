from agent.runner import run_agent_openai


def test_agent():
    result = run_agent_openai(
        "List all files in the workspace directory. "
        "Then read hello.txt and notes.txt. "
        "Tell me what Alex is learning and what the next project goal is."
    )

    print("\nAgent Response:")
    print(result)


if __name__ == "__main__":
    test_agent()