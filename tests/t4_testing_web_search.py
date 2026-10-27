from agent.runner import run_agent_openai


def test_agent():
    result = run_agent_openai(
        """
        Read the file nba.txt in the workspace directory.

        Search the web and find:
        1. The NBA championship winners for every year from 1990 to 2026.
        2. The year of the first WNBA championship and the team that won it.

        Use the information in nba.txt along with your web search results.

        Create a file named test4.txt inside the test_output directory
        within the workspace.

        The file should contain:
        - NBA champions listed by year (1990–2026).
        - The first WNBA championship year and winning team.
        - Sources used for verification.

        If the 2026 NBA champion cannot be verified, explicitly say so.
        Do not invent any championship results.

        Use the available file and web search tools to complete the task.
        Return the path of the saved file when finished.
        """
    )

    print("\nAgent Response:")
    print(result)


if __name__ == "__main__":
    test_agent()