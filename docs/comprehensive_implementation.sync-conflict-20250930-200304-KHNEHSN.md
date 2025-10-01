# Comprehensive Implementation Guide for Ansible Dev Environment Automation

This document provides a complete overview of the Ansible Dev Environment project, including all roles, features, fixes, variables, implementation details, use cases, and extensibility. It consolidates information from architecture.md, guide.md, and tasks.md for a single reference.

## Overview
The project automates developer environment setup on Linux (Debian/Ubuntu, Fedora/Rocky, Arch) and macOS using Ansible. Key features:
- Multi-distro support (package_mgr auto-set: nala/dnf/pacman/brew).
- Modular roles (enabled via vars, tags for selective runs).
- User handling: Interactive prompt for target_user, creation, groups (sudo/docker/wheel), skel configs for new users.
- Core installs: Base apps (vim, zsh, tmux, curl, git, etc.), Docker/Portainer/Syncthing, Netdata monitoring, Neovim (Bob, NvChad/LazyVim distros), dev envs (Python/UV, JS/NVM/Bun/PNPM, Nix).
- Security: Hardening (SSH, firewall auto-ports for services, fail2ban, auto-updates).
- Cloud-init: Bootstrap VM with user/packages, playbook run, Nix/Netdata curl.
- Idempotent, cross-platform, no secrets.

Assisted by Cline on 2025-09-25, updated 2025-09-26 with Netdata, Syncthing, Nix, UV standalone, auto-ports.

## Role Breakdown and Implementation Details
Roles run sequentially in site.yml via enabled_roles loop.

1. **os-detection**: Gathers facts, sets package_mgr (nala for Debian, dnf for RedHat, pacman for Arch, brew for macOS).

2. **prerequisites**: User prompt (pause if target_user unset), create target_user, add groups, PGP keys, repo tweaks (dnf.conf max_parallel=10, disable ISO, Nala install Debian).

3. **base-installs**: Installs basic_apps via package_mgr (includes netdata); Netdata via kickstart script, start/enable, port 19999.

4. **docker-setup**: OS-specific Docker CE/Compose install, service start, user to docker group, Portainer container (port 7770), Syncthing container (ports 8384/22000/21027, volumes .syncthing-data/config), template docker-compose.j2 to resolved .yml and .env in ~/.docker-services/syncthing for manual use.

5. **shell-customize**: Zsh install, Oh My Zsh/plugins (autosuggestions, syntax-highlighting, Powerlevel10k), template .zshrc.j2 (OS aliases, NVM/UV/Nix paths, nvim aliases), copy .tmux.conf, TPM/powerline/resurrect to home/skel.

6. **nvim-setup**: Dependencies (curl/git), Bob install (OS-specific zip), stable Nvim, clone distros (NvChad/LazyVim to .config/nvim-{distro}), aliases in .zshrc/skel (NVIM_APPNAME), distro defaults (no custom init.lua).

7. **dev-envs**: Python3/pip, standalone UV (Astral script ~/.cargo/bin), NVM (LTS/stable Node), Bun/PNPM curl, Nix (multi-user curl, PATH); paths in .zshrc/skel.

8. **security-harden**: Fail2ban, SSH hardening (PermitRootLogin no, PasswordAuth no, AllowUsers target_user), firewall (ufw deny/allow SSH + service_ports loop for Portainer/Syncthing/Netdata on Debian, firewalld on RedHat), auto-updates (unattended-upgrades/dnf-automatic if enabled), disable avahi-daemon.

9. **cloud-init**: Template cloud-config.j2 (users target_user sudo/zsh/groups, packages basics + docker-ce/netdata/zsh/tmux/nala/dnf-automatic, write_files setup.sh git clone/ansible-galaxy/playbook --skip-tags cloud-init + Nix/Netdata curl, runcmd chmod/setup/rm).

Skel Propagation: Configs ( .zshrc, .tmux.conf, .docker-services/syncthing/docker-compose.yml/.env, .config/nvim aliases in .zshrc) copied to /etc/skel for new users.

## Variables Table
Key vars from group_vars/all.yml (defaults):

| Var | Default | Description |
|-----|----------|-------------|
| target_user | devuser | Username for configs/user creation |
| create_new_user | true | Create target_user if not exists |
| enabled_roles | [os-detection, prerequisites, base-installs, docker-setup, shell-customize, nvim-setup, dev-envs, security-harden, cloud-init] | Roles to run |
| dev_envs | ['python', 'js'] | Dev envs to install (add 'go', 'lua', 'nix') |
| portainer_port | 7770 | Portainer external port |
| service_ports | [{name: 'portainer', port: "{{ portainer_port }}", proto: 'tcp'}, {syncthing_gui: 8384, tcp}, {syncthing_sync: 22000, tcp}, {syncthing_udp: 21027, udp}, {netdata: 19999, tcp}] | Auto-firewall ports |
| enable_auto_updates | false | Enable auto-updates |
| harden_level | minimal | 'minimal' or 'full' for security |
| nvim_distros | ['nvchad', 'lazyvim'] | Nvim distros for NVIM_APPNAME aliases |
| basic_apps | [sudo, vim, ... , netdata, ...] | Core packages list |
| nix_multi_user | true | Nix install type |
| enable_gui | false | Enable GUI app installs (Linux/macOS) |
| font_enable | false | Enable font installs (Linux/macOS) |
| user_docker_dir | '.docker-services' | Docker compose dir |
| user_syncthing_data | '.syncthing-data' | Syncthing data volume |
| playbook_repo_url | 'https://github.com/youruser/ansible-dev-env.git' | Git repo for cloud-init clone |

## Use Cases
1. **Full Dev Onboarding**: Run on fresh VM; creates user, installs all (Docker/Syncthing for services, Netdata monitoring, Nix for tools, UV for fast Python).
2. **Cloud Provisioning**: Generate cloud-init yaml, deploy to AWS/Multipass; auto-user + playbook (skel ensures new logins have Zsh/Nvim/Syncthing).
3. **Multi-Machine Sync**: Deploy to cluster; Syncthing syncs code/dotfiles (use case: team dev with Netdata dashboards).
4. **Lightweight Extensions**: --tags dev-envs for Nix/Python/JS only; Nix flakes for project-specific (e.g., rust with cargo).
5. **Monitoring/Updates**: Netdata :19999 + enable_auto_updates for maintained envs.
6. **Nvim Workflows**: Switch distros via aliases; skel for team consistency.

## Troubleshooting/Extensibility
- Compose vars: Use templated .yml + .env.
- Firewall: Auto-ports via service_ports; customize for new services.
- Nix: Multi-user for shared, single for simple; flakes for reproducible.
- Add roles: e.g., Kubernetes (minikube, k9s; future).
- Future: Kubernetes role for local K8s dev with Syncthing/Nix integration.
- GUI Installs: Role for Linux/macOS GUI apps (Firefox, VLC, Bitwarden, etc.) when enable_gui is true.
- Font Installs: Role for Powerline fonts when font_enable is true.

See tasks.md for progress.
