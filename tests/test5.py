from agent.runner import run_agent_openai

def test_agent():
    result = run_agent_openai( "Search for today's gold rate, summarize the last three days gold rates" \
    ", and write the summaries to gold-rates.txt.and write output to test_output folder " 
    )

    print("\nAgent Response:")
    print(result)

if __name__ == "__main__":
    test_agent()