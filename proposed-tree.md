# Proposed Ansible Project Directory Structure

This document outlines the expected directory structure for an Ansible project, based on the current setup and best practices. The structure ensures that Ansible can correctly locate playbooks, roles, inventory, variables, and other necessary files.

```
ansible-project/
├── inventory/                  # Inventory directory
│   ├── hosts.ini              # Main inventory file (for local/remote hosts)
│   ├── production/            # Inventory files for specific environments (optional)
│   │   └── hosts.yml
│   └── staging/               # Another environment (optional)
│       └── hosts.yml
│
├── group_vars/                # Group-specific variables
│   ├── all.yml                # Variables for all groups
│   ├── webservers.yml         # Variables for webservers group (if any)
│   └── dbservers.yml          # Variables for dbservers group (if any)
│
├── host_vars/                 # Host-specific variables (optional)
│   ├── hostname1.yml          # Variables for hostname1
│   └── hostname2.yml          # Variables for hostname2
│
├── roles/                     # Reusable roles
│   ├── common/                # Example role (not in current project)
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── handlers/
│   │   │   └── main.yml
│   │   ├── files/
│   │   ├── templates/
│   │   ├── vars/
│   │   │   └── main.yml
│   │   └── defaults/
│   │       └── main.yml
│   │
│   ├── os-detection/          # Project role: Detects OS
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── prerequisites/         # Project role: Installs prerequisites
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── base-installs/         # Project role: Installs base apps
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── docker-setup/          # Project role: Sets up Docker
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── shell-customize/       # Project role: Customizes shell (zsh, tmux)
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── nvim-setup/            # Project role: Sets up Neovim
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── dev-envs/              # Project role: Sets up dev environments
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── security-harden/       # Project role: Security hardening
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── fonts/                 # Project role: Installs fonts
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── terminals/             # Project role: Terminal setup (e.g., alacritty)
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── gui-installs/          # Project role: Installs GUI apps
│   │   └── tasks/
│   │       └── main.yml
│   │
│   ├── nix-gui-installs/     # Project role: Installs Nix GUI apps
│   │   └── tasks/
│   │       └── main.yml
│   │
│   └── cloud-init/            # Project role: Cloud-init specific tasks
│       └── tasks/
│           └── main.yml
│
├── files/                     # Static files used by roles
│   ├── cloud-config.j2        # Cloud-init config template
│   ├── cloud-init/            # Cloud-init related files
│   │   ├── generate.py        # Script to generate cloud-init configs
│   │   ├── minimal.yml        # Minimal cloud-init config
│   │   ├── dev.yml            # Development cloud-init config
│   │   └── full.yml           # Full cloud-init config
│   │
│   ├── docker-services/       # Docker compose files and configs
│   │   └── syncthing/
│   │       ├── docker-compose.yml
│   │       ├── docker-compose.j2
│   │       └── .env.j2
│   │
│   ├── dotfiles/              # Dotfiles (zshrc, tmux.conf, etc.)
│   │   ├── .zshrc.j2
│   │   ├── .tmux.conf
│   │   ├── default-powerline.sh
│   │   ├── alacritty.toml
│   │   └── ghostty-config
│   │
│   ├── list-mt25/             # Font files (e.g., Nerd Fonts)
│   │   ├── CascadiaCode/
│   │   ├── DankMono Nerd Font/
│   │   ├── GeistMono/
│   │   ├── JetBrainsMono/
│   │   └── VictorMono/
│   │
│   └── init-scripts/          # Installation scripts (if moved here)
│       ├── install_ansible.py
│       ├── deploy_ansible_remote.py
│       ├── generate_cloud_config.py
│       ├── install_ansible.sh
│       └── deploy_ansible_remote.sh
│
├── docs/                      # Documentation
│   ├── README.md
│   ├── guide.md
│   ├── architecture.md
│   ├── tasks.md
│   ├── fixes.md
│   ├── ansible_scripts_guide.md
│   ├── nix_guide.md
│   └── comprehensive_implementation.md
│
├── requirements.yml           # Ansible Galaxy collections requirements
├── site.yml                   # Main playbook
├── install_ansible.py         # Local setup script (at root)
├── deploy_ansible_remote.py   # Remote setup script (at root)
├── generate_cloud_config.py   # Cloud-init config generator (at root)
├── install_ansible.sh         # Local setup script (Bash) (at root)
├── deploy_ansible_remote.sh   # Remote setup script (Bash) (at root)
└── .gitignore                 # Git ignore file
```

## Key Directories and Files

- **`inventory/`**: Contains inventory files. `hosts.ini` is used by the scripts for local/remote hosts.
- **`group_vars/all.yml`**: Defines variables applicable to all hosts/groups. Crucial for role configurations.
- **`roles/`**: Each directory under `roles/` is an Ansible role. Roles are self-contained units of automation.
- **`files/`**: Contains static files that roles might copy or template (e.g., `cloud-config.j2`, dotfiles, fonts).
- **`docs/`**: Project documentation.
- **`site.yml`**: The main playbook that orchestrates the execution of roles.
- **`requirements.yml`**: Lists Ansible collections to be installed.
- **Root-level scripts**: Python and Bash scripts for setting up Ansible and running playbooks locally or remotely.

## Notes

- The current project structure largely follows this, with scripts at the root.
- `host_vars` is optional but can be used for host-specific variables if needed.
- The `files/init-scripts/` directory is shown as a suggestion if scripts are moved; currently, they are at the project root.
- Cloud-init specific configurations are under `files/cloud-init/`.
- Docker service definitions are under `files/docker-services/`.
- Dotfiles and fonts are organized under `files/dotfiles/` and `files/list-mt25/` respectively.
