from agent.runner import run_agent_openai


def test_agent():
    result = run_agent_openai(
        """
        Find a file named secret_project.txt somewhere inside
        the workspace directory.

        First list the workspace directory.

        If you cannot find the file, investigate further using
        the available tools.

        Read secret_project.txt and explain what the secret
        project is about.

        Do not invent information.
        If you cannot find the file, clearly say so.
        """
    )

    print("\nAgent Response:")
    print(result)


if __name__ == "__main__":
    test_agent()