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
    echo -e "${RED}[ERROR]${NC} $1
