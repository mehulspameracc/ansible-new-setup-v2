# Ansible Dev Environment Automation Project

## Overview
This project provides a modular Ansible playbook to automate the setup of a comprehensive developer environment on various Linux distributions (Debian, Ubuntu, Fedora, Rocky Linux, Arch) and macOS. The setup is idempotent, cross-platform, and extensible, allowing selective installation of components like shell customizations, Docker, Neovim, and dev environments (Python, JavaScript/Node.js). It supports multi-user configurations via `/etc/skel/` for new users and targeted tasks for existing users. Cloud-init integration enables automated provisioning on cloud/VM instances.

The playbook is structured into roles corresponding to setup phases, with conditionals for OS-specific handling (e.g., Nala on Debian-based, DNF optimizations on Fedora, Homebrew on macOS). Configurations (dotfiles, themes) are stored locally in `files/dotfiles/` for portability—no external repos required initially.

**Assisted by Cline (powered by xAI Grok model) on 2025-09-25.**

## Key Features
- **Multi-Distro Support**: Uses Ansible facts (`ansible_os_family`, `ansible_os`) to detect and adapt (e.g., apt/nala for Debian, dnf for Fedora/Rocky, pacman for Arch, brew for macOS).
- **Modularity**: Roles can be enabled/disabled via variables (e.g., `enabled_roles: ['base-installs', 'docker-setup']`). Use tags for selective runs (e.g., `--tags shell`).
- **User Handling**:
  - Global: System-wide installs (packages, Docker).
  - Per-User: Copy configs to home dirs for existing users (via `target_user` var).
  - New Users: Populate `/etc/skel/` with dotfiles (Zsh, Tmux, Nvim); create non-root user with sudo.
  - Cloud-Init: Bootstrap script generates user-data YAML to create users and trigger playbook.
- **Phases**: Sequential execution in `site.yml`:
  1. **OS Detection**: Gather facts; set `package_mgr` var (nala/dnf/pacman/brew).
  2. **Prerequisites**: Create non-root user, add to sudo, PGP keys, repo updates (disable ISO on Debian, dnf.conf tweaks on Fedora).
  3. **Base Installs**: Core apps (vim, nano, zsh, tmux, curl, git, wget, htop, fzf, ncdu, aria2, neofetch, lolcat, wormhole, p7zip-full/rar).
  4. **Docker Setup**: Install Docker CE, Compose v2; deploy Portainer CE on port 7770; Syncthing container (GUI 8384, sync 22000/tcp, UDP 21027, volumes .syncthing-data/config); templated docker-compose.yml and .env for manual management in ~/.docker-services/syncthing.
  5. **Shell Customization**: Oh My Zsh, zsh-autosuggestions, zsh-syntax-highlighting, Powerlevel10k; Tmux with powerline, resurrect, TPM; OS-specific aliases in configs.
  6. **Neovim Setup**: Install latest Nvim via Bob; Support multiple distros (NvChad, LazyVim) via `NVIM_APPNAME` and aliases (e.g., `nvim-nvchad`); copy user configs.
  7. **Dev Environments**: Python (UV, Pip); JS/Node (NVM for LTS/stable, Bun, PNPM).
  8. **Security Hardening**: Firewall (ufw/firewalld; auto-allow service ports like Syncthing/Netdata via service_ports loop), SSH hardening, auto-updates (unattended-upgrades/dnf-automatic if enabled), fail2ban; disable unnecessary services (e.g., avahi-daemon).
- **Extensibility**: Add new roles (e.g., Go, .NET) in `roles/`; toggle in `group_vars/all.yml`. Future: Kubernetes (Minikube role).

  - **Future: Kubernetes (Minikube role)**: Stub task for local K8s dev:
    ```yaml
    - name: Install minikube
      shell: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && install -o root -g root -m 755 minikube-linux-amd64 /usr/local/bin/minikube
      when: false  # Enable when ready
    ```
├── group_vars/
│   └── all.yml                # Defaults: enabled_roles, target_user, portainer_port: 7770, dev_envs: ['python', 'js'], etc.
├── host_vars/                 # Per-host overrides (e.g., mac.yml for Darwin)
├── roles/
│   ├── os-detection/          # tasks/main.yml: Set facts/vars for package_mgr
│   ├── prerequisites/         # User creation, repo tweaks (Nala install, dnf.conf)
│   ├── base-installs/         # Package installs via package_mgr
│   ├── shell-customize/       # Zsh/Tmux installs & configs from files/dotfiles/
│   ├── docker-setup/          # Docker install, Portainer container
│   ├── nvim-setup/            # Bob script, distro clones, aliases
│   ├── dev-envs/              # Sub-tasks for python/js
│   ├── security-harden/       # Firewall, SSH, updates
│   └── cloud-init/            # Generate cloud-config.yaml
├── files/
│   └── dotfiles/              # .zshrc, tmux.conf, themes; OS variants (e.g., .zshrc.debian.j2)
├── docs/                      # This file, tasks.md, readme.md, etc.
├── site.yml                   # Main playbook: Include roles in phase order
├── requirements.yml           # Galaxy: community.docker, homebrew, etc.
└── Vagrantfile                # Optional VM testing
```

## Variables & Customization
- `package_mgr`: Auto-set (nala for Debian, dnf for Fedora, etc.).
- `target_user`: Default 'devuser'; for existing users.
- `enable_auto_updates`: Bool for unattended-upgrades/dnf-automatic.
- `harden_level`: 'minimal'/'full' for security.
- OS-Specific: Templates (e.g., `.zshrc.j2` with `{% if ansible_os_family == 'Debian' %}` for aliases).

## Execution Flow
1. Run: `ansible-playbook -i inventory/hosts site.yml --extra-vars "target_user=youruser"`.
2. For cloud: Generate `cloud-config.yaml` via role, deploy to VM.
3. Idempotency: Handlers for restarts; ignore_errors on non-critical.

## Known Considerations
- macOS: Requires Ansible on target (or run from host); Brew Cask for GUI apps if needed.
- Arch: AUR support? (Keep to official repos initially).
- Multi-Host: Inventory groups for distro-specific vars.

See `tasks.md` for progress, `readme.md` for setup/running.
