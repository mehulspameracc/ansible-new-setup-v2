#!/usr/bin/env python3
# Remote Ansible Deployment Script (Python)
# This script installs Ansible (if not present), prompts for remote server details,
# and then runs the Ansible playbook to configure the remote machine
# based on user-selected features. Includes an interactive menu for role selection.
# Assisted by Cline on 2025-09-30.

import os
import sys
import subprocess
import shutil
import getpass
import time
import ipaddress

# --- Configuration ---
PLAYBOOK_DIR = os.path.dirname(os.path.abspath(__file__)) # Assumes script is in 'files'
PLAYBOOK_DIR = os.path.dirname(PLAYBOOK_DIR) # Go up one level to project root
INVENTORY_DIR = os.path.join(PLAYBOOK_DIR, "inventory")
INVENTORY_FILE = os.path.join(INVENTORY_DIR, "remote_hosts.ini")
# Default inventory template for a single remote server
DEFAULT_INVENTORY_TEMPLATE = "[remote_servers]\n{server_hostname} ansible_host={server_ip} ansible_user={ssh_user} ansible_port={ssh_port} {ssh_key_option}\n"
PLAYBOOK_FILE = os.path.join(PLAYBOOK_DIR, "remote_setup.yml")

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

# --- Function to Prompt for Server Details ---
def prompt_for_server_details():
    log_info("Please enter details for the remote server:")
    while True:
        server_ip = input("Server Hostname/IP Address: ").strip()
        if not server_ip:
            log_warning("Server IP/Hostname cannot be empty.")
            continue
        try:
            # Basic validation for IP address or hostname
            ipaddress.ip_address(server_ip) # Checks for IPv4/IPv6
            break
        except ValueError:
            # Not an IP, could be a hostname. For simplicity, we'll accept any non-empty string.
            # More robust hostname validation could be added if needed.
            if server_ip.replace('-', '').replace('.', '').isalnum() or ' ' not in server_ip : # Basic hostname check
                 break
            log_warning("Invalid IP address or hostname format. Please try again.")
            continue

    ssh_user = input("SSH Username (e.g., 'ubuntu', 'ec2-user'): ").strip()
    if not ssh_user:
        log_error("SSH Username cannot be empty.")
        sys.exit(1)

    while True:
        ssh_port_input = input("SSH Port (default 22): ").strip()
        if not ssh_port_input:
            ssh_port = 22
            break
        try:
            ssh_port = int(ssh_port_input)
            if 1 <= ssh_port <= 65535:
                break
            else:
                log_warning("Port must be between 1 and 65535.")
        except ValueError:
            log_warning("Invalid port number. Please enter a number.")
    
    ssh_key_path = input("Path to SSH Private Key (leave blank if using password): ").strip()
    ssh_key_option = ""
    if ssh_key_path:
        if not os.path.exists(ssh_key_path):
            log_error(f"SSH key file not found at '{ssh_key_path}'. Please check the path.")
            # Ask if user wants to continue without key or re-enter
            if not input("Continue without SSH key and use password prompt? (y/N): ").lower().startswith('y'):
                sys.exit(1)
            ssh_key_path = "" # Reset to blank if not continuing
        else:
            ssh_key_option = f"ansible_ssh_private_key_file='{ssh_key_path}'"
            log_info(f"Using SSH key: {ssh_key_path}")
    else:
        log_info("No SSH key provided. Ansible will prompt for SSH password if key is not available or agent is not running.")
    
    return server_ip, ssh_user, ssh_port, ssh_key_option, ssh_key_path


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
        print(f"{Colors.BOLD}Select roles/features to install on the remote server:{Colors.NC}")
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
def create_inventory_file(server_ip, ssh_user, ssh_port, ssh_key_option_val, ssh_key_path_val):
    log_info(f"Creating inventory file at: {INVENTORY_FILE}")
    os.makedirs(INVENTORY_DIR, exist_ok=True)
    
    server_hostname = f"remote-server-{server_ip.replace('.', '-').replace(':', '-')}" # Make hostname-safe

    inventory_content = DEFAULT_INVENTORY_TEMPLATE.format(
        server_hostname=server_hostname,
        server_ip=server_ip,
        ssh_user=ssh_user,
        ssh_port=ssh_port,
        ssh_key_option=ssh_key_option_val if ssh_key_option_val else ""
    )
    # Ensure no double newlines if ssh_key_option was empty
    inventory_content = inventory_content.replace("\n\n", "\n")

    with open(INVENTORY_FILE, "w") as f:
        f.write(inventory_content)
    log_success("Inventory file created.")

# --- Main Execution ---
def main():
    log_info("Starting remote Ansible deployment script (Python)...")
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

    # 3. Prompt for server details
    server_ip, ssh_user, ssh_port, ssh_key_option, ssh_key_path = prompt_for_server_details()

    # 4. Display interactive menu for role selection
    selected_roles = display_menu()
    if not selected_roles:
        log_error("No roles selected. Exiting.")
        sys.exit(1)
    log_info(f"Selected roles: {', '.join(selected_roles)}")

    # 5. Create inventory file
    create_inventory_file(server_ip, ssh_user, ssh_port, ssh_key_option, ssh_key_path)

    # 6. Run Ansible playbook
    log_info(f"Running Ansible playbook with selected roles against {server_ip}...")
    os.chdir(PLAYBOOK_DIR) # Change to playbook directory

    tags_argument = ""
    if selected_roles:
        tags_argument = "--tags " + ",".join(f'"{role}"' for role in selected_roles)

    ansible_command = ["ansible-playbook", "-i", INVENTORY_FILE, PLAYBOOK_FILE]
    if tags_argument:
        ansible_command.extend(tags_argument.split())
    ansible_command.extend(["--ask-become-pass", "--ask-pass"]) # For remote, need SSH password too

    if not run_command(ansible_command):
        log_error(f"Ansible playbook execution failed on {server_ip}. Please check the output above for errors.")
        sys.exit(1)
    else:
        log_success(f"Ansible playbook executed successfully on {server_ip}.")
        log_info("The remote server should now be configured with the selected features.")

if __name__ == "__main__":
    main()
