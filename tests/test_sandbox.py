from agent.sandbox.manager import SandboxManager


def test_sandbox():
    print("Test started!", flush=True)
    manager = SandboxManager()

    try:
        # Start once
        manager.start()
        print("Sandbox started!")

        # Test 1: Basic execution
        result = manager.execute("print(10 + 20)")
        print("Test 1:", result)
        assert result["success"]

        # Test 2: Persistent Python variables
        manager.execute("x = 100")
        result = manager.execute("print(x * 2)")
        print("Test 2:", result)
        assert "200" in "".join(result["stdout"])

        # Test 3: Pandas
        result = manager.execute("""
import pandas as pd

df = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar"],
    "revenue": [1000, 2000, 3000]
})

print(df["revenue"].sum())
""")
        print("Test 3:", result)
        assert "6000" in "".join(result["stdout"])

        # Test 4: Error handling
        result = manager.execute("print(undefined_variable)")
        print("Test 4:", result)
        assert not result["success"]

        print("\nAll sandbox tests passed!")

    finally:
        manager.close()
        print("Sandbox closed!")


if __name__ == "__main__":
    test_sandbox()