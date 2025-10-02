#!/bin/bash

# Local Ansible Installation and Configuration Script
# This script installs Ansible (if not present) and then runs the Ansible playbook
# to configure the local machine based on user-selected features.
# Includes an interactive menu for role selection.
# Assisted by Cline on 2025-09-30.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PLAYBOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_FILE="$PLAYBOOK_DIR/inventory/hosts.ini"
# Default to localhost for local installation
DEFAULT_INVENTORY="[localhost]\nlocalhost ansible_connection=local\n"
PLAYBOOK_FILE="$PLAYBOOK_DIR/local_setup.yml"

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
    "cloud-init" # Typically not needed for local install unless you want to generate the config
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
        echo -e "${BOLD}Select roles/features to install on your local machine:${NC}"
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
    echo -e "$DEFAULT_INVENTORY" > "$INVENTORY_FILE"
    log_success "Inventory file created."
}

# --- Main Execution ---
main() {
    log_info "Starting local Ansible setup script..."
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

    # 3. Display interactive menu for role selection
    display_menu
    log_info "Selected roles: ${selected_role_names[*]}"

    # 4. Create inventory file
    create_inventory_file

    # 5. Run Ansible playbook
    log_info "Running Ansible playbook with selected roles..."
    cd "$PLAYBOOK_DIR"

    # Construct the tags argument for ansible-playbook
    TAGS_ARGUMENT=""
    if [ ${#selected_role_names[@]} -gt 0 ]; then
        TAGS_ARGUMENT="--tags ${selected_role_names[*]}"
    fi

    # Run the playbook
    # Using --ask-become-pass is good practice for roles that require sudo
    ansible-playbook -i "$INVENTORY_FILE" "$PLAYBOOK_FILE" $TAGS_ARGUMENT --ask-become-pass

    if [ $? -eq 0 ]; then
        log_success "Ansible playbook executed successfully."
        log_info "Your local machine should now be configured with the selected features."
        log_info "You might need to log out and log back in for all changes (e.g., shell changes) to take full effect."
    else
        log_error "Ansible playbook execution failed. Please check the output above for errors."
        exit 1
    fi
}

# Run main function
main "$@"
