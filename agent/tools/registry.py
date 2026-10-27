from .file_tools import list_files, read_file, write_file
from .search_tools import web_search
from .code_execution import execute_code

# Data analytics tools
from .lookup_data import lookup_data
from .analyze_data import analyze_data
from .generate_visualization import generate_visualization


TOOLS = {
    "list_files": {
        "function": list_files,
        "description": "List files in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list"
                }
            },
            "required": ["directory"]
        }
    },

    "read_file": {
        "function": read_file,
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Full path to the file"
                }
            },
            "required": ["filepath"]
        }
    },

    "write_file": {
        "function": write_file,
        "description": "Write content to a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Full path to the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["filepath", "content"]
        }
    },

    "web_search": {
        "function": web_search,
        "description": "Searches the web and gives result",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"],
            "additionalProperties": False
        }
    },

    "execute_code": {
        "function": execute_code,
        "description": (
            "Execute Python code and return its output, errors, and exit status. "
            "Use for calculations, data processing, and Python code execution. "
            "Only Python code is supported."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute."
                },
                "timeout_seconds": {
                    "type": "integer",
                    "description": "Maximum execution time in seconds.",
                    "default": 30
                }
            },
            "required": ["code"]
        }
    },

    "lookup_data": {
        "function": lookup_data,
        "description": "Look up data from a dataset",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The unchanged prompt that the user provided."
                },
                "filepath": {
                    "type": "string",
                    "description": "Path to the Parquet dataset relative to agent/workspace."
                }
            },
            "required": ["prompt", "filepath"]
        }
    },

    "analyze_data": {
        "function": analyze_data,
        "description": "Analyze data to extract insights",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "The lookup_data tool's output."
                },
                "prompt": {
                    "type": "string",
                    "description": "The unchanged prompt that the user provided."
                }
            },
            "required": ["data", "prompt"]
        }
    },

    "generate_visualization": {
        "function": generate_visualization,
        "description": "Generate Python code to create data visualizations",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "The lookup_data tool's output."
                },
                "visualization_goal": {
                    "type": "string",
                    "description": "The goal of the visualization."
                }
            },
            "required": ["data", "visualization_goal"]
        }
    }
}