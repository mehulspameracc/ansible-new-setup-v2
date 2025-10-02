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
    selected_indices = set()
    current_index = 0
    num_options = len(AVAILABLE_ROLES)
    special_options = {"all": ALL_ROLES_SELECTION, "full": FULL_ROLES_SELECTION}
    special_options_order = ["all", "full"]
    total_options = num_options + len(special_options)

    def print_menu():
        os.system('clear' if os.name == 'posix' else 'cls') # Clear screen
        print(f"{Colors.BOLD}Select roles/features to install on your local machine:{Colors.NC}")
        print(f"Use {Colors.CYAN}UP/DOWN{Colors.NC} arrows to navigate, {Colors.CYAN}SPACE{Colors.NC} to select/deselect, {Colors.CYAN}Enter{Colors.NC} to confirm.")
        print("-" * 80)
        for i in range(total_options):
            if i == current_index:
                print("✨ ", end="")
            else:
                print("  ", end="")

            if i < num_options:
                role_name = AVAILABLE_ROLES[i]
                if i in selected_indices:
                    print(f"{Colors.GREEN}[✔] {role_name}{Colors.NC}")
                else:
                    print(f"[ ] {role_name}")
            else: # Special options
                special_key = special_options_order[i - num_options]
                special_roles = special_options[special_key]
                # Check if all roles in this special option are selected
                is_selected = True
                for r_name in special_roles:
                    try:
                        if AVAILABLE_ROLES.index(r_name) not in selected_indices:
                            is_selected = False
                            break
                    except ValueError: # Should not happen if roles are consistent
                        is_selected = False
                        break

                if is_selected:
                    print(f"{Colors.GREEN}[✔] {special_key} ({'all except cloud-init' if special_key == 'all' else 'all roles including cloud-init'}){Colors.NC}")
                else:
                    print(f"[ ] {special_key} ({'all except cloud-init' if special_key == 'all' else 'all roles including cloud-init'})")
        print("-" * 80)

    # Key reading logic differs for Windows and Linux/macOS
    if os.name == 'nt': # Windows
        import msvcrt
        while True:
            print_menu()
            key = msvcrt.getch()

            if key == b'\xe0': # Arrow key prefix
                arrow_key = msvcrt.getch()
                if arrow_key == b'H': # Up
                    current_index = (current_index - 1) % total_options
                elif arrow_key == b'P': # Down
                    current_index = (current_index + 1) % total_options
            elif key == b'\r': # Enter
                if not selected_indices and not any(
                    all(AVAILABLE_ROLES.index(r_name) in selected_indices for r_name in roles)
                    for roles in special_options.values() if roles
                ):
                     log_warning("Please select at least one role or 'all'/'full'.")
                     time.sleep(2)
                     continue
                break
            elif key == b' ': # Space
                if current_index < num_options:
                    if current_index in selected_indices:
                        selected_indices.remove(current_index)
                    else:
                        selected_indices.add(current_index)
                    # If a regular role is toggled, it might invalidate a special selection
                    # For simplicity, we don't auto-deselect specials here, user can re-toggle
                else: # Special option
                    special_key = special_options_order[current_index - num_options]
                    special_roles_list = special_options[special_key]
                    
                    # Check if all roles in this special option are currently selected
                    all_selected = True
                    for r_name in special_roles_list:
                        try:
                            if AVAILABLE_ROLES.index(r_name) not in selected_indices:
                                all_selected = False
                                break
                        except ValueError:
                            pass
                    
                    if all_selected:
                        # Deselect all roles in this special option
                        for r_name in special_roles_list:
                            try:
                                selected_indices.remove(AVAILABLE_ROLES.index(r_name))
                            except ValueError:
                                pass
                    else:
                        # Select all roles in this special option
                        for r_name in special_roles_list:
                            try:
                                selected_indices.add(AVAILABLE_ROLES.index(r_name))
                            except ValueError:
                                pass
    else: # Linux/macOS
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            while True:
                print_menu()
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                tty.setcbreak(sys.stdin.fileno())

                if key == '\x1b': # ESC
                    _ = sys.stdin.read(2) # Read [ or ]
                    arrow_key = sys.stdin.read(1)
                    if arrow_key == 'A': # Up
                        current_index = (current_index - 1) % total_options
                    elif arrow_key == 'B': # Down
                        current_index = (current_index + 1) % total_options
                elif key == '\n': # Enter
                    if not selected_indices and not any(
                        all(AVAILABLE_ROLES.index(r_name) in selected_indices for r_name in roles)
                        for roles in special_options.values() if roles
                    ):
                         log_warning("Please select at least one role or 'all'/'full'.")
                         time.sleep(2)
                         continue
                    break
                elif key == ' ': # Space
                    if current_index < num_options:
                        if current_index in selected_indices:
                            selected_indices.remove(current_index)
                        else:
                            selected_indices.add(current_index)
                    else: # Special option
                        special_key = special_options_order[current_index - num_options]
                        special_roles_list = special_options[special_key]
                        
                        all_selected = True
                        for r_name in special_roles_list:
                            try:
                                if AVAILABLE_ROLES.index(r_name) not in selected_indices:
                                    all_selected = False
                                    break
                            except ValueError:
                                pass
                        
                        if all_selected:
                            for r_name in special_roles_list:
                                try:
                                    selected_indices.remove(AVAILABLE_ROLES.index(r_name))
                                except ValueError:
                                    pass
                        else:
                            for r_name in special_roles_list:
                                try:
                                    selected_indices.add(AVAILABLE_ROLES.index(r_name))
                                except ValueError:
                                    pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Process selected indices into role names
    selected_role_names = []
    for idx in sorted(list(selected_indices)): # Sort for consistent order
        if idx < num_options:
            selected_role_names.append(AVAILABLE_ROLES[idx])
    
    # Check if any special option is fully selected and add its roles
    for special_key, roles_list in special_options.items():
        is_fully_selected = True
        for r_name in roles_list:
            try:
                if AVAILABLE_ROLES.index(r_name) not in selected_indices:
                    is_fully_selected = False
                    break
            except ValueError:
                is_fully_selected = False
                break
        if is_fully_selected:
            # Add roles from this special option, avoiding duplicates if already added by individual selection
            for r_name in roles_list:
                if r_name not in selected_role_names:
                    selected_role_names.append(r_name)
            # If a special option is active, it implies individual selections for its roles are redundant
            # We can clear the individually selected ones if we want, or just rely on the final list.
            # For now, we just add the special option's roles if not already present.
            break # Assuming only one special option can be "active" in terms of full selection

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
    ansible_command = ["ansible-playbook", "-i", INVENTORY_FILE, "site.yml"]
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
