"""Development utilities."""
import subprocess
import sys

def run_dev():
    """Run development server with hot reload."""
    subprocess.run([
        "uv", "run", 
        "watchfiles", 
        "mcp_project.main.main", 
        "--filter", "python"
    ])

if __name__ == "__main__":
    run_dev()