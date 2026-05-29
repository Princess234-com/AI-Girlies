import os

def list_project_structure(root_path):
    for folder, subfolders, files in os.walk(root_path):
        print(f"\n📁 Folder: {folder}")

        py_files = [f for f in files if f.endswith(".py")]
        if py_files:
            print("   📝 Python scripts:")
            for script in py_files:
                print(f"      - {script}")
        else:
            print("   (No Python scripts)")

# Example: point this to your VS Code project root
project_path = r"C:\Users\ahiar\OneDrive - University of Gloucestershire\Documents\GitHub\AI-Girlies"
list_project_structure(project_path)
