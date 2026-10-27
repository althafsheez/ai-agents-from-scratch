import os
from langfuse.openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from agent.sandbox.manager import SandboxManager
load_dotenv()

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
    timeout=60,
)

MODEL = "gemini-3.5-flash-lite"


CHART_CONFIGURATION_PROMPT = """
Generate a chart configuration based on this data:

{data}

The goal is to show: {visualization_goal}
"""


class VisualizationConfig(BaseModel):
    chart_type: str = Field(
        description="Type of chart to generate"
    )

    x_axis: str = Field(
        description="Name of the x-axis column"
    )

    y_axis: str = Field(
        description="Name of the y-axis column"
    )

    title: str = Field(
        description="Title of the chart"
    )


def extract_chart_config(
    data: str,
    visualization_goal: str
) -> dict:
    """Generate chart configuration using an LLM."""

    formatted_prompt = CHART_CONFIGURATION_PROMPT.format(
        data=data,
        visualization_goal=visualization_goal
    )

    response = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "user", "content": formatted_prompt}
        ],
        response_format=VisualizationConfig,
    )

    config = response.choices[0].message.parsed

    if config is None:
        raise ValueError("Could not generate chart configuration")

    return {
        "chart_type": config.chart_type,
        "x_axis": config.x_axis,
        "y_axis": config.y_axis,
        "title": config.title,
        "data": data
    }


CREATE_CHART_PROMPT = """
Write Python code to create a chart based on the following configuration.

Only return Python code, no other text.

Use pandas and matplotlib.

Configuration:

{config}
"""


def create_chart(config: dict) -> str:
    """Generate Python visualization code."""

    formatted_prompt = CREATE_CHART_PROMPT.format(
        config=config
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": formatted_prompt}
        ],
    )

    code = response.choices[0].message.content or ""

    code = code.replace("```python", "")
    code = code.replace("```", "")

    return code.strip()


def generate_visualization(
    data: str,
    visualization_goal: str,
    sandbox_manager: SandboxManager
) -> dict:
    """Generate and execute visualization code inside E2B."""

    config = extract_chart_config(data, visualization_goal)

    code = create_chart(config)

    result = sandbox_manager.execute(code, timeout=30)

    return {
        "success": result["success"],
        "code": code,
        "output": result.get("stdout", []),
        "error": result.get("error")
    }