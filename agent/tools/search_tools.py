import os
import json
import requests

def web_search(query: str, num_results: int = 5) -> str:
    """Search the web and return relevant results as JSON."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return json.dumps({
    "success": False,
    "error": {
        "code": "MISSING_API_KEY",
        "message": "Web search is unavailable",
        "retryable": False
        }
    })

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "query": query,
                "max_results": num_results,
                "api_key": api_key
            },
            timeout=10  # Always set a timeout
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return json.dumps([
            {
                "title": r["title"],
                "url": r["url"],
                "snippet": r["content"][:300]  # Cap length - every token costs
            }
            for r in results
        ])
    except requests.Timeout:
        return json.dumps({
            "error": "Search timed out after 10s",
            "retry": True,
            "suggestion": "Try a more specific query or reduce num_results"
        })
    except requests.HTTPError as e:
        return json.dumps({
            "error": f"HTTP {e.response.status_code}",
            "retry": e.response.status_code == 429  # Rate limit = retry; other errors = don't
        })
    except Exception as e:
        return json.dumps({"error": str(e), "retry": False})