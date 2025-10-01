# Comprehensive Implementation Guide for Ansible Dev Environment Automation

This document provides a complete overview of the Ansible Dev Environment project, including all roles, features, fixes, variables, implementation details, use cases, and extensibility. It consolidates information from architecture.md, guide.md, and tasks.md for a single reference.

## Overview
The project automates developer environment setup on Linux (Debian/Ubuntu, Fedora/Rocky, Arch) and macOS using Ansible. Key features:
- Multi-distro support (package_mgr auto-set: nala/dnf/pacman/brew).
- Modular roles (enabled via vars, tags for selective runs).
- User handling: Interactive prompt for target_user, creation, groups (sudo/docker/wheel), skel configs for new users.
- Core installs: Base apps (vim, zsh, tmux, curl, git, etc.), Docker/Portainer/Syncthing, Netdata monitoring, Neovim (Bob, NvChad/LazyVim distros), dev envs (Python/UV, JS/NVM/Bun/PNPM, Nix, Go, Lua).
- Security: Hardening (SSH, firewall auto-ports for services, fail2ban, auto-updates).
- Cloud-init: Bootstrap VM with user/packages, playbook run, Nix/Netdata curl.
- GUI & Terminals: Consolidated GUI app installs, dedicated terminal emulator installs, independent font installs.
- Nix GUI: Optional GUI app installs via Nix flakes.
- Idempotent, cross-platform, no secrets.

Assisted by Cline on 2025-09-25, updated 2025-09-30 with refined GUI/terminal/font roles, Nix GUI role, and Go/Lua support.

## Role Breakdown and Implementation Details
Roles run sequentially in site.yml via enabled_roles loop.

1.  **os-detection**: Gathers facts, sets package_mgr (nala for Debian, dnf for RedHat, pacman for Arch, brew for macOS).
2.  **prerequisites**: User prompt (pause if target_user unset), create target_user, add groups, PGP keys, repo tweaks (dnf.conf max_parallel=10, disable ISO, Nala install Debian), Fedora FFmpeg swap.
3.  **base-installs**: Installs basic_apps via package_mgr (does not include GUI apps or terminals); Netdata via kickstart script, start/enable, port 19999.
4.  **docker-setup**: OS-specific Docker CE/Compose install, service start, user to docker group, Portainer container (port 7770), Syncthing container (ports 8384/22000/21027, volumes .syncthing-data/config), template docker-compose.j2 to resolved .yml and .env in ~/.docker-services/syncthing for manual use.
5.  **shell-customize**: Zsh/Tmux install, Oh My Zsh/plugins (autosuggestions, syntax-highlighting, Powerlevel10k), TPM (powerline, resurrect), template .zshrc.j2 (OS aliases, NVM/UV/Nix/Go/Lua paths, nvim aliases), copy .tmux.conf to user home /etc/skel/, sets shell to zsh.
6.  **nvim-setup**: Dependencies (curl/git), Bob install (OS-specific zip), stable Nvim, clone distros (NvChad/LazyVim to .config/nvim-{distro}), aliases in .zshrc/skel (NVIM_APPNAME), distro defaults (no custom init.lua).
7.  **dev-envs**: For 'python': python3/pip, standalone UV (Astral script to ~/.cargo/bin); for 'js': NVM (curl install, nvm install --lts/node, alias default node), Bun (curl install), PNPM (curl install); Nix (multi-user curl script, PATH addition); for 'go': go install via package/curl; for 'lua': lua/lua5.3/luajit via package; adds paths to .zshrc/skel.
8.  **security-harden**: Installs fail2ban (start/enable); SSH (PermitRootLogin no, PasswordAuthentication no, AllowUsers target_user if full); firewall (ufw deny/allow SSH + service_ports loop for Portainer/Syncthing/Netdata on Debian, firewalld on RedHat with auto-loop via service_ports, no pf on macOS); auto-updates (unattended-upgrades on Debian, dnf-automatic on RedHat if enabled); disables avahi-daemon if full.
9.  **fonts**: Installs Powerline/Nerd Fonts (Debian: fonts-powerline, Arch: ttf-nerd-fonts-symbols, macOS: brew install powerline-fonts) independently of enable_gui, as they benefit terminal users. Copies to system dirs and /etc/skel/.local/share/fonts/.
10. **terminals**: Installs terminal emulators (Linux: ghostty, alacritty; macOS: brew install --cask ghostty) independently of enable_gui. Copies configs to user home and /etc/skel/.config/.
11. **gui-installs**: Installs GUI apps (Linux: Firefox, VLC, Bitwarden, obsidian, ferdium, floorp, postman, waterfox, zed, zen-browser, vscode, zerotier, tailscale, firefox-esr, brave-browser (AUR), ungoogled-chromium (AUR) via apt/dnf/pacman/yay; macOS: brew install --cask bitwarden, cheatsheet, discord, fig, hiddenbar, imageoptim, itsycal, karabiner-elements, keycastr, maccy, macfuse, obs, obsidian, orion, qbittorrent, raycast, rectangle, sublime-text, vlc, ferdium, floorp, postman, waterfox, zed, zen, vscode, zerotier, tailscale, firefox, firefox-developer-edition, ungoogled-chromium, brave-browser) when enable_gui is true. Consolidated list based on user feedback.
12. **nix-gui-installs**: Installs selected GUI apps (e.g., brave, zed, zen, postman, floorp, ferdium) via Nix flakes when enable_nix_gui is true. This role is separate for flexibility. Includes Nix installation if not present.
13. **cloud-init**: (Local/delegate) Templates cloud-config.j2 to cloud_init_path (users/target_user with sudo/zsh/groups; packages: basics + docker-ce/netdata/zsh/tmux/nala/dnf-automatic; write_files setup.sh with git clone/ansible-galaxy/playbook --skip-tags cloud-init; runcmd chmod/setup.sh/rm; Nix/Netdata curl in setup.sh).

Skel Propagation: Configs ( .zshrc, .tmux.conf, .config/ghostty/config, .config/alacritty/alacritty.toml, .docker-services/syncthing/docker-compose.yml/.env, .config/nvim aliases in .zshrc) copied to /etc/skel for new users.

## Variables Table
Key vars from group_vars/all.yml (defaults):

| Var | Default | Description |
|-----|----------|-------------|
| target_user | devuser | Username for configs/user creation |
| create_new_user | true | Create target_user if not exists |
| enabled_roles | [os-detection, prerequisites, base-installs, docker-setup, shell-customize, nvim-setup, dev-envs, security-harden, fonts, terminals, gui-installs, nix-gui-installs, cloud-init] | Roles to run |
| dev_envs | ['python', 'js'] | Dev envs to install (add 'go', 'lua', 'nix') |
| portainer_port | 7770 | Portainer external port |
| service_ports | [{name: 'portainer', port: "{{ portainer_port }}", proto: 'tcp'}, {syncthing_gui: 8384, tcp}, {syncthing_sync: 22000, tcp}, {syncthing_udp: 21027, udp}, {netdata: 19999, tcp}] | Auto-firewall ports |
| enable_auto_updates | false | Enable auto-updates |
| harden_level | minimal | 'minimal' or 'full' for security |
| nvim_distros | ['nvchad', 'lazyvim'] | Nvim distros for NVIM_APPNAME aliases |
| basic_apps | [sudo, vim, nano, zsh, tmux, curl, git, wget, htop, fzf, ripgrep, fd-find, universal-ctags, ncdu, aria2, neofetch, lolcat, magic-wormhole, netdata, open-vm-tools, p7zip-full, p7zip-rar, zoxide, exa, bat, btop, lsd, jq, fastfetch, openvpn, wireguard, sqlite, telnet, nmap, tldr, yazi, zstd, figlet] | Core packages list |
| nix_multi_user | true | Nix install type |
| enable_gui | false | Enable GUI app installs (Linux/macOS) |
| font_enable | true | Enable system-wide font installation (Linux/macOS) - Recommended for terminal users |
| enable_nix_gui | false | Enable GUI app installs via Nix flakes (Linux) |
| user_docker_dir | '.docker-services' | Docker compose dir |
| user_syncthing_data | '.syncthing-data' | Syncthing data volume |
| playbook_repo_url | 'https://github.com/youruser/ansible-dev-env.git' | Git repo for cloud-init clone |

## Use Cases
1.  **Full Dev Onboarding**: Run on fresh VM; creates user, installs all (Docker/Syncthing for services, Netdata monitoring, shell/Nvim/dev envs, terminals, fonts, GUI apps if enabled, Nix GUI apps if enabled). Use case: Quick dev setup on AWS EC2.
2.  **Cloud Provisioning**: Generate cloud-init yaml, deploy to AWS/Multipass; auto-user + playbook (skel ensures new logins have Zsh/Nvim/Syncthing/terminals/fonts). Use case: Automated spin-up for CI/CD.
3.  **Multi-Machine Sync**: Deploy to cluster; Syncthing syncs code/dotfiles (use case: team dev with Netdata dashboards). Consistent terminal/font setup.
4.  **Lightweight Extensions**: `--tags dev-envs,shell-customize,fonts,terminals` for core dev tools only; Nix flakes for project-specific (e.g., rust with cargo).
5.  **Monitoring/Updates**: Netdata :19999 + enable_auto_updates for maintained envs.
6.  **Nvim Workflows**: Switch distros via aliases; skel for team consistency.
7.  **Selective GUI Setup**: `--tags gui-installs` for OS GUI apps; `--tags nix-gui-installs` for Nix GUI apps. Use case: Different GUI tool preferences or Nix-only environments.
8.  **Server vs. Desktop**: Fonts and terminals installed on all, as they benefit even remote server access. GUI apps only on desktops if `enable_gui` is true.

## Troubleshooting/Extensibility
-   **Compose vars**: Use templated .yml + .env.
-   **Firewall**: Auto-ports via service_ports; customize for new services.
-   **Nix**: Multi-user for shared, single for simple; flakes for reproducible.
-   **Add roles**: e.g., Kubernetes (minikube, k9s; future).
-   **Future**: Kubernetes role for local K8s dev with Syncthing/Nix integration.
-   **GUI Installs**: Consolidated role for Linux/macOS GUI apps when `enable_gui` is true. Comprehensive list.
-   **Terminal Installs**: Dedicated role for ghostty/alacritty, independent of GUI.
-   **Font Installs**: Dedicated role for Powerline/Nerd fonts, independent of GUI.
-   **Nix GUI Installs**: Separate role for GUI apps via Nix flakes when `enable_nix_gui` is true, for flexibility.

See tasks.md for progress.
