from agent.runner import run_agent_openai
from langfuse import get_client

def test_agent():
    prompt = """
    You are a data analyst.

    Analyze the Iris dataset located at:
    agent/workspace/iris.csv
    before sending the url check where you are now

    Your goal is to explore the dataset, discover useful insights,
    and create meaningful data visualizations.

    TASK 1: UNDERSTAND THE DATASET
    - Identify the available columns.
    - Determine the total number of records.
    - Identify numerical and categorical variables.
    - Check for missing values.
    - Understand what the dataset represents.

    TASK 2: EXPLORE AND ANALYZE
    - Calculate descriptive statistics for numerical columns.
    - Compare measurements across different flower species.
    - Identify interesting patterns and differences.
    - Determine which measurements best distinguish species.
    - Investigate relationships between numerical variables.

    TASK 3: GENERATE VISUALIZATIONS
    Generate Python code for at least three meaningful charts.

    Choose appropriate chart types based on the data.

    The charts should help explain:
    - Differences between flower species.
    - Relationships between flower measurements.
    - Important patterns or distributions.

    Do not choose chart types randomly.
    Explain why each visualization is useful.

    TASK 4: EXECUTE AND VERIFY CHARTS
    - Use the execute_code tool to run the generated Python code.
    - Use matplotlib to create the charts.
    - Save the charts as PNG files inside agent/workspace/.
    - Check whether chart generation succeeds.
    - If execution fails, fix the code and retry.

    TASK 5: FINAL REPORT
    Provide:
    1. Dataset overview.
    2. Important statistics.
    3. At least five meaningful insights.
    4. Explanation of each visualization.
    5. Paths to the generated charts.
    6. Any errors encountered and whether they were fixed.

    IMPORTANT:
    - Use lookup_data to retrieve information from the dataset.
    - Use analyze_data to interpret the results.
    - Use generate_visualization to generate plotting code.
    - Use execute_code to run the plotting code.
    - Base your conclusions on actual dataset values.
    - Do not invent statistics or claim charts were created
      unless their files were successfully generated.
    """

    result = run_agent_openai(
        goal=prompt,
        max_steps=25
    )

    print("\n" + "=" * 60)
    print("DATA ANALYSIS AGENT TEST")
    print("=" * 60)

    print(result)

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_agent()
    finally:
        get_client().flush()