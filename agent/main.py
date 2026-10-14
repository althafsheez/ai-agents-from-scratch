from runner import run_agent_openai

if __name__ == "__main__":
    result = run_agent_openai(
        "List the files in the current directory, "
        "then read the contents of README.md if it exists."
    )
    print(f"\nFinal answer:\n{result}")

 