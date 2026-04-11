import os
import sys

# Set PYTHONPATH to root and the current project
current_script_dir = os.path.dirname(os.path.abspath(__file__))
package_root = os.path.dirname(current_script_dir)
# Identify root as the parent of 'projects/'
root_dir = os.path.abspath(os.path.join(package_root, "../../"))
sys.path.insert(0, root_dir)
sys.path.insert(0, package_root)

import uvicorn
from gemini_agent.graph.builder import agent_graph
from src.core.server import create_agent_app

# FastAPI app creation
app = create_agent_app(agent_graph)

def run_api_server(port: int = 8888):
    """Start the API server"""
    uvicorn.run(app, host="0.0.0.0", port=port)

def example_api_endpoints(port: int = 8888):
    """Wrapper to show new features"""
    print(f"Starting FastAPI Server on port {port}...")
    run_api_server(port)

def main():
    """Entry point to demonstrate features"""
    import sys
    port = 8888
    if "--port" in sys.argv:
        port_idx = sys.argv.index("--port") + 1
        if port_idx < len(sys.argv):
            port = int(sys.argv[port_idx])
    example_api_endpoints(port)

if __name__ == "__main__":
    main()
