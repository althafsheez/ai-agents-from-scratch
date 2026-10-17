from agent.runner import run_agent_openai


def test_agent():
    result = run_agent_openai(
        "List all files in the workspace directory. "
        "Then read hello.txt and notes.txt. "
        "Then write a new file called summary.txt that contains a summary of the contents of hello.txt and notes.txt."
        
    )

    print("\nAgent Response:")
    print(result)


if __name__ == "__main__":
    test_agent()