import os 


MEMORY_FILE="agents.md"
def load_memory() -> str:
    """Load Persistent memory from file """
    if not os.path.exists(MEMORY_FILE):
        return "No prior memory.This a fresh session"
    with open(MEMORY_FILE, "r") as f:
        return f.read()

def save_memory(content: str) -> None:
    """Overwrite Persistent memory to file"""
    with open(MEMORY_FILE, "w") as f:
        f.write(content)