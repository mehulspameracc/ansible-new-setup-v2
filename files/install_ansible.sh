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
    local selected_indices=()
    local current_index=0
    local num_options=${#AVAILABLE_ROLES[@]}
    local special_options_count=2 # "all" and "full"
    local total_options=$((num_options + special_options_count))

    while true; do
        # Clear screen (works for most terminals)
        printf "\033c"
        echo -e "${BOLD}Select roles/features to install on your local machine:${NC}"
        echo "Use ${CYAN}UP/DOWN${NC} arrows to navigate, ${CYAN}SPACE${NC} to select/deselect, ${CYAN}Enter${NC} to confirm."
        echo "--------------------------------------------------------------------------------"

        for ((i=0; i < total_options; i++)); do
            if [ $i -eq $current_index ]; then
                printf "▶ "
            else
                printf "  "
            fi

            if [ $i -lt $num_options ]; then
                role_name="${AVAILABLE_ROLES[$i]}"
                if [[ " ${selected_indices[*]} " =~ " $i " ]]; then
                    echo -e "${GREEN}[x] ${role_name}${NC}"
                else
                    echo -e "[ ] ${role_name}"
                fi
            else
                # Special options
                local special_idx=$((i - num_options))
                if [ $special_idx -eq 0 ]; then # "all"
                    if [[ " ${selected_indices[*]} " =~ " all_selected " ]]; then
                        echo -e "${GREEN}[x] all (all except cloud-init)${NC}"
                    else
                        echo -e "[ ] all (all except cloud-init)"
                    fi
                elif [ $special_idx -eq 1 ]; then # "full"
                    if [[ " ${selected_indices[*]} " =~ " full_selected " ]]; then
                        echo -e "${GREEN}[x] full (all roles including cloud-init)${NC}"
                    else
                        echo -e "[ ] full (all roles including cloud-init)"
                    fi
                fi
            fi
        done
        echo "--------------------------------------------------------------------------------"

        # Read a single character
        read -rsn1 key
        case "$key" in
            $'\x1b') # ESC sequence
                read -rsn2 -t 0.1 key # Read the next 2 characters of the escape sequence
                case "$key" in
                    '[A') # Up arrow
                        ((current_index--))
                        if [ $current_index -lt 0 ]; then
                            current_index=$((total_options - 1))
                        fi
                        ;;
                    '[B') # Down arrow
                        ((current_index++))
                        if [ $current_index -ge $total_options ]; then
                            current_index=0
                        fi
                        ;;
                esac
                ;;
            '') # Enter key
                # Validate at least one selection
                if [ ${#selected_indices[@]} -eq 0 ] && [[ ! " ${selected_indices[*]} " =~ " all_selected " ]] && [[ ! " ${selected_indices[*]} " =~ " full_selected " ]]; then
                    log_warning "Please select at least one role or 'all'/'full'."
                    sleep 2
                    continue
                fi
                break
                ;;
            ' ') # Space key
                if [ $current_index -lt $num_options ]; then
                    # Regular role selection
                    local role_idx_to_toggle=$current_index
                    if [[ " ${selected_indices[*]} " =~ " $role_idx_to_toggle " ]]; then
                        # Deselect
                        selected_indices=("${selected_indices[@]/$role_idx_to_toggle}")
                        # Remove special selection markers if they conflict
                        selected_indices=("${selected_indices[@]/all_selected}")
                        selected_indices=("${selected_indices[@]/full_selected}")
                    else
                        # Select
                        selected_indices+=("$role_idx_to_toggle")
                        # Remove special selection markers if they conflict
                        selected_indices=("${selected_indices[@]/all_selected}")
                        selected_indices=("${selected_indices[@]/full_selected}")
                    fi
                else
                    # Special option selection
                    local special_idx=$((current_index - num_options))
                    if [ $special_idx -eq 0 ]; then # "all"
                        if [[ " ${selected_indices[*]} " =~ " all_selected " ]]; then
                            selected_indices=("${selected_indices[@]/all_selected}")
                        else
                            selected_indices=("${ALL_ROLES_SELECTION[@]}") # Replace with all roles
                            selected_indices+=("all_selected") # Mark special selection
                            # Remove any conflicting full_selection
                            selected_indices=("${selected_indices[@]/full_selected}")
                        fi
                    elif [ $special_idx -eq 1 ]; then # "full"
                        if [[ " ${selected_indices[*]} " =~ " full_selected " ]]; then
                            selected_indices=("${selected_indices[@]/full_selected}")
                        else
                            selected_indices=("${FULL_ROLES_SELECTION[@]}") # Replace with all roles
                            selected_indices+=("full_selected") # Mark special selection
                            # Remove any conflicting all_selected
                            selected_indices=("${selected_indices[@]/all_selected}")
                        fi
                    fi
                fi
                ;;
        esac
    done

    # Process selected indices into role names
    SELECTED_ROLES=()
    for idx in "${selected_indices[@]}"; do
        # Check if it's a special marker
        if [[ "$idx" == "all_selected" ]]; then
            SELECTED_ROLES+=("${ALL_ROLES_SELECTION[@]}")
        elif [[ "$idx" == "full_selected" ]]; then
            SELECTED_ROLES+=("${FULL_ROLES_SELECTION[@]}")
        elif [[ "$idx" =~ ^[0-9]+$ ]] && [ $idx -lt $num_options ]; then
            SELECTED_ROLES+=("${AVAILABLE_ROLES[$idx]}")
        fi
    done

    # Remove duplicates that might arise from special selections
    IFS=" " read -r -a SELECTED_ROLES <<< "$(echo "${SELECTED_ROLES[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' ')"
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
    log_info "Selected roles: ${SELECTED_ROLES[*]}"

    # 4. Create inventory file
    create_inventory_file

    # 5. Run Ansible playbook
    log_info "Running Ansible playbook with selected roles..."
    cd "$PLAYBOOK_DIR"

    # Construct the tags argument for ansible-playbook
    TAGS_ARGUMENT=""
    if [ ${#SELECTED_ROLES[@]} -gt 0 ]; then
        TAGS_ARGUMENT="--tags ${SELECTED_ROLES[*]}"
    fi

    # Run the playbook
    # Using --ask-become-pass is good practice for roles that require sudo
    ansible-playbook -i "$INVENTORY_FILE" site.yml $TAGS_ARGUMENT --ask-become-pass

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
