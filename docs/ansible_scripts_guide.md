# Ansible Deployment Scripts Guide

This guide explains how to use the provided shell (Bash) and Python scripts to automate the installation and configuration of Ansible, and subsequently apply Ansible playbooks to configure either your local machine or a remote server.

## Overview

We have four primary scripts:

1.  **`files/install_ansible.sh`**: Bash script for local Ansible setup and configuration.
2.  **`files/deploy_ansible_remote.sh`**: Bash script for remote Ansible deployment.
3.  **`files/install_ansible.py`**: Python script for local Ansible setup and configuration.
4.  **`files/deploy_ansible_remote.py`**: Python script for remote Ansible deployment.

All scripts feature an interactive menu for selecting which Ansible roles (features) to apply.

## Prerequisites

*   **For Local Scripts (`install_ansible.sh` / `install_ansible.py`):**
    *   A Linux, macOS, or Windows (with WSL/MSYS2 for Bash) environment.
    *   Appropriate permissions to install software (e.g., `sudo` access).
*   **For Remote Scripts (`deploy_ansible_remote.sh` / `deploy_ansible_remote.py`):**
    *   All local prerequisites.
    *   Access to the remote server via SSH.
    *   SSH credentials (username, and either a private key path or willingness to type the password).
    *   The remote server must have a compatible operating system (Debian/Ubuntu, Fedora/RHEL, Arch Linux, etc.) that the script can detect and install Ansible on if it's not already present. The remote server needs `python` installed for Ansible to run correctly (usually present by default on most modern Linux distributions).
*   **General:**
    *   The Ansible playbook files (this project) should be accessible on the machine running the script.

## Script Functionality

### Common Features

*   **Ansible Installation**: Checks if Ansible is installed. If not, it attempts to install it based on the detected OS package manager (`apt-get`, `dnf`, `pacman`, `brew`).
*   **Ansible Galaxy Collections**: If a `requirements.yml` file is found in the project root, it installs or updates the specified Ansible collections.
*   **Interactive Role Selection**: Presents a menu to choose which roles (e.g., `base-installs`, `docker-setup`, `nvim-setup`) to apply.
    *   Use arrow keys to navigate.
    *   Use the spacebar to select/deselect roles.
    *   Use `Enter` to confirm your selection.
    *   Special options:
        *   `all`: Selects all available roles except `cloud-init`.
        *   `full`: Selects all available roles, including `cloud-init`.
*   **Inventory File Creation**: Dynamically creates an Ansible inventory file (`hosts.ini` for local, `remote_hosts.ini` for remote) based on your input.
*   **Playbook Execution**: Runs `ansible-playbook` with the selected tags.

### Local Scripts (`install_ansible.sh` / `install_ansible.py`)

*   Configures the **local machine**.
*   Inventory file defaults to `localhost` with `ansible_connection=local`.
*   Does not require SSH details.

### Remote Scripts (`deploy_ansible_remote.sh` / `deploy_ansible_remote.py`)

*   Configures a **remote server**.
*   Prompts for remote server details:
    *   Server Hostname/IP Address
    *   SSH Username
    *   SSH Port (defaults to 22)
    *   Path to SSH Private Key (optional; if left blank, Ansible will prompt for the SSH password)
*   Creates an inventory file for the remote server.
*   Uses `--ask-pass` for SSH password and `--ask-become-pass` for sudo privileges on the remote host.

## Usage Instructions

### 1. Local Setup (Bash)

```bash
# Navigate to the 'files' directory or ensure the script is executable
chmod +x files/install_ansible.sh

# Run the script
./files/install_ansible.sh
```

Follow the on-screen prompts to select roles for your local machine.

### 2. Remote Deployment (Bash)

```bash
# Navigate to the 'files' directory or ensure the script is executable
chmod +x files/deploy_ansible_remote.sh

# Run the script
./files/deploy_ansible_remote.sh
```

You will be prompted for remote server details and then the role selection menu.

### 3. Local Setup (Python)

Ensure you have Python 3 installed.

```bash
# Navigate to the 'files' directory
cd files

# Run the script with python3
python3 install_ansible.py
```

Follow the on-screen prompts.

### 4. Remote Deployment (Python)

Ensure you have Python 3 installed.

```bash
# Navigate to the 'files' directory
cd files

# Run the script with python3
python3 deploy_ansible_remote.py
```

You will be prompted for remote server details and then the role selection menu.

## Post-Execution Notes

*   **Local Changes**: For local configurations, especially those involving shell customization (e.g., changing default shell, updating `.bashrc`, `.zshrc`), you may need to log out and log back in for all changes to take full effect.
*   **Remote Changes**: Changes on the remote server will apply directly. You might need to log in and out of the remote server for shell changes.
*   **Review Output**: Carefully review the output of the `ansible-playbook` command for any errors or warnings. The scripts will indicate success or failure.

## Troubleshooting

*   **Script Truncation (Observed with Bash Scripts)**: If you encounter issues with the provided Bash scripts (`install_ansible.sh`, `deploy_ansible_remote.sh`) appearing truncated or not running correctly, it might be due to an environment-specific issue with how the scripts were saved or interpreted. In such cases, the Python versions (`install_ansible.py`, `deploy_ansible_remote.py`) are recommended as they are generally more robust across different environments and were created to address potential inconsistencies with shell script handling.
*   **Ansible Installation Fails**: Ensure your system's package manager lists are up-to-date. You might need to run `sudo apt-get update` (Debian/Ubuntu) or `sudo dnf check-update` (Fedora/RHEL) manually before running the script again.
*   **SSH Connection Issues (Remote Scripts)**:
    *   Verify the server IP/hostname, SSH username, and port.
    *   Ensure the SSH key path is correct and the key is properly set up on the remote server.
    *   Test the SSH connection manually: `ssh -i /path/to/your/key user@server_ip -p port`.
    *   Check firewall rules on both local and remote machines.
*   **Permission Denied**: Ensure the user running the script has `sudo` privileges if Ansible installation is required.
*   **Role Selection Issues**: If a role seems to be skipped or not applied as expected, check the `site.yml` file and the individual role tasks to understand its dependencies or conditions.

## Choosing Between Bash and Python Scripts

*   **Bash Scripts (`*.sh`)**:
    *   Pros: Lightweight, no need for a Python interpreter (if Bash is available).
    *   Cons: Can be less portable across different Unix-like environments, complex text parsing and user interaction can be trickier to implement robustly.
*   **Python Scripts (`*.py`)**:
    *   Pros: Generally more portable, easier to implement complex logic (like the interactive menu), better error handling, cross-platform (Windows with Python).
    *   Cons: Require a Python 3 interpreter.

For most users, especially those on diverse systems or preferring more robust tools, the **Python scripts are recommended**. The Bash scripts are provided as an alternative or for environments where Python might not be the primary scripting language.

## Security Considerations

*   **SSH Keys**: Using SSH keys is generally more secure than passwords. Ensure your private keys are stored securely and have appropriate permissions (e.g., `chmod 600 ~/.ssh/id_rsa`).
*   **`sudo` Password**: The scripts will prompt for `sudo` password (`--ask-become-pass`) only when roles require elevated privileges. Be mindful of when you are entering your password.
*   **Running Scripts**: Only run scripts from trusted sources. Review the script content if you have concerns about what it does.
