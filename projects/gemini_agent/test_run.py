import os
import sys
import asyncio
from dotenv import load_dotenv

# Set PYTHONPATH to root and the current project
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = current_script_dir
root_dir = os.path.abspath(os.path.join(current_script_dir, "../../"))
sys.path.insert(0, root_dir)
sys.path.insert(0, project_dir)

# Explicitly load .env from project directory
load_dotenv(os.path.join(project_dir, ".env"))

from gemini_agent.graph.builder import builder

async def main():
    print("Testing gemini_agent...")
    input_data = {"input": "Hello, who are you?"}
    try:
        response = await builder.ainvoke(input_data)
        print("\nAgent Response:")
        print(response.get("output", "No output field in response"))
    except Exception as e:
        print(f"Error during agent invocation: {e}")

if __name__ == "__main__":
    asyncio.run(main())
