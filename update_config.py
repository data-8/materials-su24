import os
import re
import subprocess
from github import Github

# Get the GitHub token from the environment
token = os.getenv('GH_PAT')

# Initialize the GitHub client
g = Github(token)

# The repository where the config.yml needs to be updated
repo = g.get_repo("data-8/su24")

# Get the latest commit in the current branch
output = subprocess.check_output(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"])
changed_files = output.decode("utf-8").splitlines()

# Define the base URL
base_url = "https://data8.datahub.berkeley.edu/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fdata-8%2Fmaterials-su24&urlpath=retro%2Ftree%2Fmaterials-su24%2Fmaterials%2F{parent_directory}%2F{sub_directory}%2F{sub_directory}.ipynb&branch=main"

# Find new directories
new_dirs = []
for file in changed_files:
    parts = file.split('/')
    if len(parts) == 2 and parts[0] in ["hw", "lab", "proj"]:
        new_dirs.append((parts[0], parts[1]))

if not new_dirs:
    print("No new directories found.")
    exit(0)

print(f"New directories detected: {new_dirs}")

# Clone the su24 repository
subprocess.run(["git", "clone", f"https://{token}@github.com/data-8/su24.git"])
os.chdir("su24")

# Read the current config.yml file
with open("config.yml", "r") as f:
    lines = f.readlines()

print(f"Original config.yml:\n{''.join(lines)}")

# Update the config.yml file
for parent_directory, sub_directory in new_dirs:
    new_link = base_url.format(parent_directory=parent_directory, sub_directory=sub_directory)
    for i, line in enumerate(lines):
        if line.startswith(f"{sub_directory}:"):
            name = line.split(":")[1].strip()
            lines[i] = f"{sub_directory}: [{name}]({new_link})\n"
            print(f"Updated line {i}: {lines[i]}")

# Write the changes to the config.yml file
with open("config.yml", "w") as f:
    f.writelines(lines)

print(f"Updated config.yml:\n{''.join(lines)}")

# Commit and push the changes
subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
subprocess.run(["git", "add", "config.yml"])
subprocess.run(["git", "commit", "-m", "Update config.yml with new directories"])
subprocess.run(["git", "push"])
