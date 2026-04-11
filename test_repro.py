import subprocess
import os
import sys

def test_repro():
    project_name = "repro_bug"
    project_dir = os.path.join("projects", project_name)
    
    # 1. Create project
    print(f"Creating project {project_name}...")
    subprocess.run(["./bin/lapm", project_name, "create", "4", "deep_agent"], check=True)
    
    # 2. Try to run WITHOUT poetry run
    print("Running main.py WITHOUT poetry run...")
    main_py = os.path.join(project_dir, project_name, "main.py")
    
    if not os.path.exists(os.path.join(project_dir, project_name, "deepagents")):
        print("Confirmed: 'deepagents' folder does not exist in the generated project.")
    
    try:
        # We explicitly set an empty PYTHONPATH to avoid picking up the current environment if possible
        # but subprocess with 'python3' might still pick up the venv if we are IN it.
        env = os.environ.copy()
        if "PYTHONPATH" in env: del env["PYTHONPATH"]
        
        result = subprocess.run(["python3", main_py], capture_output=True, text=True, env=env)
        if "ModuleNotFoundError: No module named 'deepagents'" in result.stderr:
            print("REPRODUCED: ModuleNotFoundError: No module named 'deepagents'")
        else:
            print("Could not reproduce with simple python3 call. Maybe deepagents is in system site-packages or venv.")
            print("Stderr:", result.stderr)
    except Exception as e:
        print(f"Error during reproduction: {e}")

if __name__ == "__main__":
    test_repro()
