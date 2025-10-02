#!/bin/bash

# Remote Ansible Deployment Script
# This script installs Ansible (if not present) and then runs the Ansible playbook
# to configure a remote machine based on user-selected features.
# Includes an interactive menu for role selection.
# Assisted by Cline on 2025-09-30.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PLAYBOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_FILE="$PLAYBOOK_DIR/inventory/remote_hosts.ini"
# Default inventory template for a single remote server
DEFAULT_INVENTORY_TEMPLATE="[remote_servers]\n{server_hostname} ansible_host={server_ip} ansible_user={ssh_user} ansible_port={ssh_port} {ssh_key_option}\n"
PLAYBOOK_FILE="$PLAYBOOK_DIR/remote_setup.yml"

# --- Color Codes for Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# --- Helper Functions ---
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# --- Function to Install Ansible ---
install_ansible() {
    log_info "Ansible not found. Installing based on your OS..."
    if command -v apt-get &> /dev/null; then
        log_info "Using apt-get (Debian/Ubuntu)..."
        sudo apt-get update
        sudo apt-get install -y ansible
    elif command -v dnf &> /dev/null; then
        log_info "Using dnf (Fedora/RHEL)..."
        sudo dnf install -y ansible
    elif command -v pacman &> /dev/null; then
        log_info "Using pacman (Arch Linux)..."
        sudo pacman -Sy --noconfirm ansible
    elif command -v brew &> /dev/null; then
        log_info "Using brew (macOS)..."
        brew install ansible
    else
        log_error "Unsupported package manager. Please install Ansible manually and re-run this script."
        exit 1
    fi
    log_success "Ansible installed successfully."
}

# --- Function to Prompt for Server Details ---
prompt_for_server_details() {
    log_info "Please enter details for the remote server:"
    read -rp "Server Hostname/IP Address: " SERVER_IP
    read -rp "SSH Username (e.g., 'ubuntu', 'ec2-user'): " SSH_USER
    read -rp "SSH Port (default 22): " SSH_PORT
    SSH_PORT=${SSH_PORT:-22}
    read -rp "Path to SSH Private Key (leave blank if using password): " SSH_KEY_PATH

    if [ -z "$SSH_KEY_PATH" ]; then
        SSH_KEY_OPTION="" # Will rely on SSH agent or password prompt
        log_info "SSH key path not provided. Ansible will prompt for SSH password if key is not available or agent is not running."
    else
        SSH_KEY_OPTION="ansible_ssh_private_key_file=$SSH_KEY_PATH"
        if [ ! -f "$SSH_KEY_PATH" ]; then
            log_error "SSH key file not found at $SSH_KEY_PATH. Please check the path."
            exit 1
        fi
    fi
}

# --- Function to Display Interactive Menu ---
# Available roles for selection
AVAILABLE_ROLES=(
    "os-detection"
    "prerequisites"
    "base-installs"
    "docker-setup"
    "shell-customize"
    "nvim-setup"
    "dev-envs"
    "security-harden"
    "fonts"
    "terminals"
    "gui-installs"
    "nix-gui-installs"
    "cloud-init"
)

# Predefined selections for 'all' and 'full'
ALL_ROLES_SELECTION=() # Excludes cloud-init by default for 'all'
FULL_ROLES_SELECTION=() # Includes all roles

for role in "${AVAILABLE_ROLES[@]}"; do
    if [[ "$role" != "cloud-init" ]]; then
        ALL_ROLES_SELECTION+=("$role")
    fi
    FULL_ROLES_SELECTION+=("$role")
done

display_menu() {
    local selected_role_names=()
    while true; do
        # Clear screen (works for most terminals)
        printf "\033c"
        echo -e "${BOLD}Select roles/features to install on the remote server:${NC}"
        echo "Enter numbers to toggle (comma-separated), 'a' for all, 'f' for full, 'q' to quit."
        echo "--------------------------------------------------------------------------------"
        for i in "${!AVAILABLE_ROLES[@]}"; do
            status="[ ]"
            if [[ " ${selected_role_names[*]} " =~ " ${AVAILABLE_ROLES[$i]} " ]]; then
                status="[x]"
            fi
            echo "$((i+1)). $status ${AVAILABLE_ROLES[$i]}"
        done
        echo "$(( ${#AVAILABLE_ROLES[@]} + 1 )). [ ] all (all except cloud-init)"
        echo "$(( ${#AVAILABLE_ROLES[@]} + 2 )). [ ] full (all roles including cloud-init)"
        echo "--------------------------------------------------------------------------------"

        read -rp "Your choice (e.g., '1,3,5', 'a', 'f', 'q'): " user_input

        case "$user_input" in
            q)
                log_info "Exiting without changes."
                exit 0
                ;;
            a)
                selected_role_names=("${ALL_ROLES_SELECTION[@]}")
                ;;
            f)
                selected_role_names=("${FULL_ROLES_SELECTION[@]}")
                ;;
            *)
                # Process comma-separated input
                IFS=',' read -ra parts <<< "$user_input"
                local new_selections=()
                for part in "${parts[@]}"; do
                    part=$(echo "$part" | xargs) # trim whitespace
                    if [[ "$part" =~ ^[0-9]+$ ]]; then
                        local idx=$((part - 1))
                        if [ "$idx" -ge 0 ] && [ "$idx" -lt "${#AVAILABLE_ROLES[@]}" ]; then
                            new_selections+=("${AVAILABLE_ROLES[$idx]}")
                        fi
                    elif [ "$part" = "a" ]; then
                        new_selections+=("${ALL_ROLES_SELECTION[@]}")
                    elif [ "$part" = "f" ]; then
                        new_selections+=("${FULL_ROLES_SELECTION[@]}")
                    fi
                done
                # Add new selections and remove duplicates
                selected_role_names+=("${new_selections[@]}")
                while IFS= read -r -d $'\0' line; do selected_role_names+=("$line"); done < <(printf "%s\n" "${selected_role_names[@]}" | sort -u)
                ;;
        esac

        if [ ${#selected_role_names[@]} -eq 0 ] && [[ "$user_input" != "q" && "$user_input" != "a" && "$user_input" != "f" ]]; then
            log_warning "Please select at least one role or 'a'/'f'."
            sleep 2
            continue
        fi

        read -rp "Selected: ${selected_role_names[*]:-None}. Confirm? (y/N): " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            break
        fi
    done
}

# --- Function to Create Inventory File ---
create_inventory_file() {
    log_info "Creating inventory file at: $INVENTORY_FILE"
    mkdir -p "$(dirname "$INVENTORY_FILE")"
    
    # Use a simple hostname based on IP for the inventory
    SERVER_HOSTNAME="remote-server-$(echo "$SERVER_IP" | tr '.' '-')"
    
    # Substitute variables into the template
    # Note: SSH_KEY_OPTION might be empty
    local inventory_content
    if [ -n "$SSH_KEY_OPTION" ]; then
        inventory_content=$(printf "$DEFAULT_INVENTORY_TEMPLATE" "$SERVER_HOSTNAME" "$SERVER_IP" "$SSH_USER" "$SSH_PORT" "$SSH_KEY_OPTION")
    else # If no key, don't add the ansible_ssh_private_key_file line
        inventory_content="[remote_servers]\n${SERVER_HOSTNAME} ansible_host=${SERVER_IP} ansible_user=${SSH_USER} ansible_port=${SSH_PORT}\n"
    fi
    
    echo -e "$inventory_content" > "$INVENTORY_FILE"
    log_success "Inventory file created."
}

# --- Main Execution ---
main() {
    log_info "Starting remote Ansible deployment script..."
    log_info "Playbook directory: $PLAYBOOK_DIR"

    # 1. Check for Ansible
    if ! command -v ansible-playbook &> /dev/null; then
        install_ansible
    else
        log_success "Ansible is already installed."
    fi

    # 2. Check for Ansible Galaxy collections
    if [ -f "$PLAYBOOK_DIR/requirements.yml" ]; then
        log_info "Installing/updating Ansible collections from requirements.yml..."
        ansible-galaxy collection install -r "$PLAYBOOK_DIR/requirements.yml"
        log_success "Ansible collections processed."
    else
        log_warning "requirements.yml not found in $PLAYBOOK_DIR. Skipping collection installation."
    fi

    # 3. Prompt for server details
    prompt_for_server_details

    # 4. Display interactive menu for role selection
    display_menu
    log_info "Selected roles: ${selected_role_names[*]}"

    # 5. Create inventory file
    create_inventory_file

    # 6. Run Ansible playbook
    log_info "Running Ansible playbook with selected roles against $SERVER_IP..."
    cd "$PLAYBOOK_DIR"

    # Construct the tags argument for ansible-playbook
    TAGS_ARGUMENT=""
    if [ ${#selected_role_names[@]} -gt 0 ]; then
        # Quote each role name to handle spaces or special characters if any were present
        TAGS_ARGUMENT="--tags ${selected_role_names[*]}"
    fi

    # Run the playbook
    # Using --ask-become-pass is good practice for roles that require sudo
    # --ask-pass will prompt for SSH password if not using a key or agent
    ansible-playbook -i "$INVENTORY_FILE" "$PLAYBOOK_FILE" $TAGS_ARGUMENT --ask-become-pass --ask-pass

    if [ $? -eq 0 ]; then
        log_success "Ansible playbook executed successfully on $SERVER_IP."
        log_info "The remote server should now be configured with the selected features."
    else
        log_error "Ansible playbook execution failed on $SERVER_IP. Please check the output above for errors."
        exit 1
    fi
}

# Run main function
main "$@"
