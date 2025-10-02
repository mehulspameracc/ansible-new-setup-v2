#!/usr/bin/env python3
# Local Ansible Installation and Configuration Script (Python)
# This script installs Ansible (if not present) and then runs the Ansible playbook
# to configure the local machine based on user-selected features.
# Includes an interactive menu for role selection.
# Assisted by Cline on 2025-09-30.

import os
import sys
import subprocess
import shutil
import getpass
import time

# --- Configuration ---
PLAYBOOK_DIR = os.path.dirname(os.path.abspath(__file__)) # Assumes script is in 'files'
PLAYBOOK_DIR = os.path.dirname(PLAYBOOK_DIR) # Go up one level to project root
INVENTORY_FILE = os.path.join(PLAYBOOK_DIR, "inventory", "hosts.ini")
DEFAULT_INVENTORY = "[localhost]\nlocalhost ansible_connection=local\n"
PLAYBOOK_FILE = os.path.join(PLAYBOOK_DIR, "local_setup.yml")

# --- Color Codes for Output ---
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m' # No Color

# --- Helper Functions ---
def log_info(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}", file=sys.stderr)

def run_command(command, check=True, capture_output=False):
    """Runs a shell command and returns the result."""
    log_info(f"Executing: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check, capture_output=capture_output, text=True, encoding='utf-8')
        if capture_output:
            return result.stdout.strip(), result.stderr.strip()
        return result.returncode == 0
    except FileNotFoundError:
        log_error(f"Command not found: {command[0]}")
        return False
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {' '.join(command)}")
        if capture_output:
            log_error(f"Stdout: {e.stdout.strip()}")
            log_error(f"Stderr: {e.stderr.strip()}")
        else:
            log_error(f"Return code: {e.returncode}")
        return False

# --- Function to Install Ansible ---
def install_ansible():
    log_info("Ansible not found. Installing based on your OS...")
    if shutil.which("apt-get"):
        log_info("Using apt-get (Debian/Ubuntu)...")
        run_command(["sudo", "apt-get", "update"])
        run_command(["sudo", "apt-get", "install", "-y", "ansible"])
    elif shutil.which("dnf"):
        log_info("Using dnf (Fedora/RHEL)...")
        run_command(["sudo", "dnf", "install", "-y", "ansible"])
    elif shutil.which("pacman"):
        log_info("Using pacman (Arch Linux)...")
        run_command(["sudo", "pacman", "-Sy", "--noconfirm", "ansible"])
    elif shutil.which("brew"):
        log_info("Using brew (macOS)...")
        run_command(["brew", "install", "ansible"])
    else:
        log_error("Unsupported package manager. Please install Ansible manually and re-run this script.")
        sys.exit(1)
    log_success("Ansible installed successfully.")

# --- Function to Display Interactive Menu ---
AVAILABLE_ROLES = [
    "os-detection", "prerequisites", "base-installs", "docker-setup",
    "shell-customize", "nvim-setup", "dev-envs", "security-harden",
    "fonts", "terminals", "gui-installs", "nix-gui-installs", "cloud-init"
]

ALL_ROLES_SELECTION = [r for r in AVAILABLE_ROLES if r != "cloud-init"]
FULL_ROLES_SELECTION = AVAILABLE_ROLES[:]

def display_menu():
    selected_role_names = []
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Colors.BOLD}Select roles/features to install on your local machine:{Colors.NC}")
        print("Enter numbers to toggle (comma-separated), 'a' for all, 'f' for full, 'q' to quit.")
        print("-" * 80)
        for i, role in enumerate(AVAILABLE_ROLES):
            status = "[x]" if role in selected_role_names else "[ ]"
            print(f"{i+1:2d}. {status} {role}")
        print(f"{len(AVAILABLE_ROLES)+1:2d}. [ ] all (all except cloud-init)")
        print(f"{len(AVAILABLE_ROLES)+2:2d}. [ ] full (all roles including cloud-init)")
        print("-" * 80)
        
        user_input = input("Your choice (e.g., '1,3,5', 'a', 'f', 'q'): ").strip().lower()
        
        if user_input == 'q':
            log_info("Exiting without changes.")
            sys.exit(0)
        elif user_input == 'a':
            selected_role_names = list(set(ALL_ROLES_SELECTION))
        elif user_input == 'f':
            selected_role_names = list(set(FULL_ROLES_SELECTION))
        else:
            try:
                parts = user_input.split(',')
                new_selections = []
                for part in parts:
                    part = part.strip()
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(AVAILABLE_ROLES):
                            new_selections.append(AVAILABLE_ROLES[idx])
                    elif part == 'a':
                        new_selections.extend(ALL_ROLES_SELECTION)
                    elif part == 'f':
                        new_selections.extend(FULL_ROLES_SELECTION)
                # Remove duplicates and update
                selected_role_names = list(set(selected_role_names + new_selections))
            except ValueError:
                log_warning("Invalid input. Please try again.")
                time.sleep(2)
                continue
        
        if not selected_role_names and user_input not in ['q', 'a', 'f']:
            log_warning("Please select at least one role or 'a'/'f'.")
            time.sleep(2)
            continue
        
        confirm = input(f"Selected: {', '.join(selected_role_names) or 'None'}. Confirm? (y/N): ").strip().lower()
        if confirm == 'y':
            break
            
    return selected_role_names

# --- Function to Create Inventory File ---
def create_inventory_file():
    log_info(f"Creating inventory file at: {INVENTORY_FILE}")
    os.makedirs(os.path.dirname(INVENTORY_FILE), exist_ok=True)
    with open(INVENTORY_FILE, "w") as f:
        f.write(DEFAULT_INVENTORY)
    log_success("Inventory file created.")

# --- Main Execution ---
def main():
    log_info("Starting local Ansible setup script (Python)...")
    log_info(f"Playbook directory: {PLAYBOOK_DIR}")

    # 1. Check for Ansible
    if not shutil.which("ansible-playbook"):
        install_ansible()
    else:
        log_success("Ansible is already installed.")

    # 2. Check for Ansible Galaxy collections
    requirements_file = os.path.join(PLAYBOOK_DIR, "requirements.yml")
    if os.path.exists(requirements_file):
        log_info("Installing/updating Ansible collections from requirements.yml...")
        run_command(["ansible-galaxy", "collection", "install", "-r", requirements_file])
        log_success("Ansible collections processed.")
    else:
        log_warning("requirements.yml not found. Skipping collection installation.")

    # 3. Display interactive menu for role selection
    selected_roles = display_menu()
    if not selected_roles:
        log_error("No roles selected. Exiting.")
        sys.exit(1)
    log_info(f"Selected roles: {', '.join(selected_roles)}")

    # 4. Create inventory file
    create_inventory_file()

    # 5. Run Ansible playbook
    log_info("Running Ansible playbook with selected roles...")
    os.chdir(PLAYBOOK_DIR) # Change to playbook directory

    tags_argument = ""
    if selected_roles:
        # Quote tags if they contain spaces or special characters, though unlikely for role names
        tags_argument = "--tags " + ",".join(f'"{role}"' for role in selected_roles)

    # Run the playbook
    # Using --ask-become-pass is good practice for roles that require sudo
    ansible_command = ["ansible-playbook", "-i", INVENTORY_FILE, PLAYBOOK_FILE]
    if tags_argument:
        ansible_command.extend(tags_argument.split())
    ansible_command.append("--ask-become-pass")

    if not run_command(ansible_command):
        log_error("Ansible playbook execution failed. Please check the output above for errors.")
        sys.exit(1)
    else:
        log_success("Ansible playbook executed successfully.")
        log_info("Your local machine should now be configured with the selected features.")
        log_info("You might need to log out and log back in for all changes (e.g., shell changes) to take full effect.")

if __name__ == "__main__":
    main()
