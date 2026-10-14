# Understanding `runner.py`

## Importing Libraries and Creating the Client

- First, we import the required libraries: `OpenAI`, `json`, and `TOOLS` from `tools.py`.
- We load the environment variables from the `.env` file using `load_dotenv()`.
- We then create an OpenAI client using `client = OpenAI()`, which allows us to communicate with the OpenAI API.

## Defining the `run_agent_openai()` Function

- We define a function called `run_agent_openai()` that takes two parameters:
  - `goal`: The task we want the agent to complete, provided as a string.
  - `max_steps`: The maximum number of iterations the agent can perform, with a default value of 10.
- The function is expected to return a string (`-> str`).

## Creating the `openai_tools` List

- First, we create a list called `openai_tools` using the tools defined in our `TOOLS` dictionary.
- We convert the tools into the specific structure expected by the OpenAI API.
- For each tool, we define:
  - `type`: Set to `"function"` to indicate that it is a function tool.
  - `function`: Contains the details of the function.
    - `name`: The name of the function (`n`).
    - `description`: The description of the function (`t["description"]`).
    - `parameters`: The parameters accepted by the function (`t["parameters"]`).
- We use `for n, t in TOOLS.items()` to loop through the dictionary.
  - `n` represents the tool name.
  - `t` represents the dictionary containing the tool details.
- This creates a list of tool definitions that we can send to the OpenAI API.

## Creating the `messages` List

```python
messages = [{"role": "user", "content": goal}]
```

- We create a list called `messages` to store the conversation history.
- The list contains dictionaries, where each dictionary represents a message.
- Initially, we add the user's request.
- Each message contains:
  - `role`: Specifies who sent the message. Here, `"user"` indicates that the message comes from the user.
  - `content`: Contains the actual message. Here, we assign it the value of `goal`.
- This is a Python list containing a dictionary, not a JSON string.
- The OpenAI Python library handles converting the request into the appropriate format when communicating with the API.

## Creating the Agent Loop

```python
for step in range(max_steps):
```

- We create a `for` loop that runs for a maximum of `max_steps` iterations.
- During each iteration, the agent communicates with the OpenAI API.
- The loop allows the agent to make multiple tool requests until the task is completed or the maximum number of iterations is reached.

## Sending a Request to OpenAI

```python
response = client.chat.completions.create(
    model="gpt-4o",
    tools=openai_tools,
    messages=messages
)
```

- We send a request to the OpenAI API using `client.chat.completions.create()`.
- We provide three main arguments:
  - `model`: Specifies the model we want to use.
  - `tools`: Contains the list of available tools.
  - `messages`: Contains the conversation history.
- The API processes the request and returns a response.

## Extracting the Response

```python
message = response.choices[0].message
```

- We take the first choice from the API response using `response.choices[0]`.
- We then access its `message` property.
- By default, the API returns one choice.
- The message may contain either a normal text response or requests to execute tools.

## Checking for Tool Calls

```python
if not message.tool_calls:
    return message.content or "Task complete."
```

- We check whether the message contains any tool calls.
- If `message.tool_calls` is `None` or empty, it means the model has not requested any tools.
- In that case, we return `message.content`, which contains the model's response.
- If `message.content` is empty or `None`, we return `"Task complete."`.
- Since we use `return`, the function ends, and the agent loop stops.

## Adding the Assistant Message to History

```python
messages.append(message)
```

- If the model requests a tool, we add the assistant's message to the `messages` list.
- This stores the tool request in the conversation history.
- It allows the API to understand which tools were requested when we send the results back.

## Looping Through Tool Calls

```python
for tc in message.tool_calls:
```

- We create another `for` loop to go through each tool call requested by the model.
- `tc` represents the current tool call.
- This allows us to execute multiple tools if the model requests more than one.

## Getting the Tool Name

```python
name = tc.function.name
```

- We extract the function name from the current tool call.
- We store it in a variable called `name`.
- This name is used to find the corresponding function in our `TOOLS` dictionary.

## Getting the Tool Arguments

```python
args = json.loads(tc.function.arguments)
```

- We extract the arguments provided by the model.
- The arguments are received as a JSON-formatted string.
- We use `json.loads()` to convert the JSON string into a Python object, normally a dictionary in this case.
- We store the converted arguments in a variable called `args`.

## Executing the Tool

```python
result = (
    TOOLS[name]["function"](**args)
    if name in TOOLS
    else json.dumps({"error": "Unknown"})
)
```

- First, we check whether the requested function name exists in the `TOOLS` dictionary.
- If the function exists:
  - We access the tool using `TOOLS[name]`.
  - We retrieve the actual Python function using `["function"]`.
  - We use `**args` to unpack the dictionary into keyword arguments.
  - We execute the function with those arguments.
  - We store the returned value in `result`.
- If the function does not exist:
  - We return an error message using `json.dumps({"error": "Unknown"})`.
- This is where the actual Python tool function gets executed.

## Adding the Tool Result to Messages

```python
messages.append({
    "role": "tool",
    "tool_call_id": tc.id,
    "content": result
})
```

- After executing the function, we add its result to the `messages` list.
- We create a dictionary containing:
  - `role`: Set to `"tool"` to indicate that the message contains a tool result.
  - `tool_call_id`: Stores the ID of the tool call (`tc.id`), allowing the API to match the result with the original request.
  - `content`: Contains the result returned by the executed function.
- This result becomes part of the conversation history.
- During the next iteration, the updated `messages` list is sent back to the OpenAI API.
- The model can then decide whether to request another tool or generate a final response.

## Handling Maximum Steps

```python
return "Max steps reached."
```

- If the loop reaches the maximum number of iterations without receiving a final response, it stops.
- The function returns `"Max steps reached."`.
- This prevents the agent from continuing indefinitely.

## Overall Understanding

- We first load the environment variables and create an OpenAI client.
- We define the `run_agent_openai()` function, which accepts a goal and a maximum number of steps.
- We create `openai_tools` by converting our `TOOLS` dictionary into the format expected by the OpenAI API.
- We create a `messages` list to store the conversation history, starting with the user's goal.
- We then create a loop that runs for a maximum of `max_steps` iterations.
- During each iteration, we send the model, tools, and messages to the OpenAI API.
- We extract the message from the first choice in the API response.
- If the message contains no tool calls, we return its content and stop the function.
- Otherwise, we add the assistant's message to the conversation history.
- We loop through the requested tool calls, extract their names and arguments, and execute the corresponding Python functions from the `TOOLS` dictionary.
- We then add the tool results to the conversation history.
- The loop continues, allowing the model to use the results and decide what to do next.
- If the maximum number of iterations is reached, the function stops.

**In short:** `runner.py` manages communication between the LLM and our Python tools. It sends requests to OpenAI, checks whether the model wants to execute a tool, runs the requested function, sends the result back, and repeats the process until the model produces a final response or the maximum number of steps is reached.
