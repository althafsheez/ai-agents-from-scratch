from agent.runner import run_agent_openai

def test_agent():
    result = run_agent_openai(
        """Calculate the compound interest on $10,000 at
          6.5% annual rate over 20 years - write the Python code, run it, and explain the result."""
    )

    print("\nAgent Response:")
    print(result)

if __name__ == "__main__":
    test_agent()