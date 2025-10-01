# User Guide for Ansible Dev Environment Automation

This guide explains how the project works, step-by-step execution flow, usage instructions, common use cases, and troubleshooting. It builds on architecture.md and readme.md for a complete understanding.

**Assisted by Cline (powered by xAI Grok model) on 2025-09-25.**

## How It Works
The project uses Ansible to automate dev env setup on Linux (Debian/Ubuntu, Fedora/Rocky, Arch) and macOS. The main playbook (site.yml) runs roles in sequence (or selectively via tags), using facts from os-detection to adapt to the target OS. Vars in group_vars/all.yml control behavior (e.g., enabled_roles, target_user='devuser').

### Execution Flow
1. **Pre-Tasks**: Loads vars, debugs target_user/enabled_roles.
2. **Roles (Dynamic Loop)**: Includes enabled_roles (default all phases):
   - **os-detection**: Gathers facts, sets package_mgr (nala for Debian, dnf for RedHat, pacman for Arch, brew for macOS).
   - **prerequisites**: Creates target_user (if enabled), adds to sudo/docker/wheel, PGP keys, repo tweaks (disable ISO on Debian, dnf.conf max_downloads=10 on Fedora, Nala/Brew install).
  - **base-installs**: Installs basic_apps (vim, zsh, tmux, curl, git, wget, htop, fzf, ncdu, aria2, neofetch, lolcat, wormhole, p7zip; + bat, btop, lsd, ghostty, alacritty) using package_mgr; Netdata monitoring (kickstart script, access :19999).
  - **docker-setup**: Installs Docker CE/Compose v2 (distro repos), starts service, adds user to docker group, deploys Portainer CE (-p 7770:9000, volumes sock/data); Syncthing container (ports 8384 GUI, 22000 sync, 21027 UDP; volumes .syncthing-data/config); templates docker-compose.yml and .env to ~/.docker-services/syncthing for manual up/down.
   - **shell-customize**: Installs Zsh/Tmux, clones Oh My Zsh/plugins (autosuggestions, syntax-highlighting, Powerlevel10k), TPM (powerline, resurrect); templates .zshrc.j2 (OS aliases, NVM/UV paths, Nvim aliases) and copies .tmux.conf to user home /etc/skel/; sets shell to zsh.
   - **nvim-setup**: Installs Bob (curl/unzip to /usr/local/bin), runs bob install stable; creates .config/nvim-{distro} dirs, clones NvChad/LazyVim, adds aliases to .zshrc/skel, copies init.lua to home/skel.
  - **dev-envs**: For 'python': python3/pip, standalone UV (Astral script to ~/.cargo/bin); for 'js': NVM (curl install, nvm install --lts/node, alias default node), Bun (curl install), PNPM (curl install); Nix (multi-user curl script, PATH addition); for 'go': go install via package/curl; for 'lua': lua/lua5.3/luajit via package; adds paths to .zshrc/skel.
  - **security-harden**: Installs fail2ban (start/enable); SSH (PermitRootLogin no, PasswordAuthentication no, AllowUsers target_user if full); firewall (ufw deny/allow SSH + service ports like 8384/22000/19999 on Debian, firewalld on RedHat with auto-loop via service_ports, no pf on macOS); auto-updates (unattended-upgrades on Debian, dnf-automatic on RedHat if enabled); disables avahi-daemon if full.
  - **fonts**: Installs Powerline fonts (Debian: fonts-powerline, Arch: ttf-nerd-fonts-symbols, macOS: brew install powerline-fonts) when font_enable is true.
  - **terminals**: Installs terminal emulators (Linux: ghostty, alacritty; macOS: brew install --cask ghostty alacritty).
  - **gui-installs**: Installs GUI apps (Linux: Firefox, VLC, Bitwarden, etc. via apt/dnf/pacman/yay; macOS: brew install --cask bitwarden, alacritty, etc.) when enable_gui is true.
  - **cloud-init**: (Local/delegate) Templates cloud-config.j2 to cloud_init_path (users/target_user with sudo/zsh/groups; packages: basics + docker-ce/netdata/zsh/tmux/nala/dnf-automatic; write_files setup.sh with git clone/ansible-galaxy/playbook --skip-tags cloud-init; runcmd chmod/setup.sh/rm; Nix/Netdata curl in setup.sh).
3. **Post-Tasks**: Debugs summary (setup complete, Portainer URL, tag usage).

The playbook is idempotent (safe reruns), uses become: true for privs, and tags for modularity (e.g., --tags shell-customize). For new users, /etc/skel/ pre-applies .zshrc/.tmux.conf/init.lua. Global: system packages/Docker; per-user: shell/Nvim/dev envs (become_user target_user).

### Usage Instructions
1. **Setup Host**: Install Ansible (`pip install ansible`), collections (`ansible-galaxy collection install -r requirements.yml`).
2. **Customize**:
   - group_vars/all.yml: Set target_user, enabled_roles (list, e.g., omit 'security-harden'), dev_envs (add 'go'), harden_level ('full'), enable_auto_updates: true.
   - files/dotfiles/: Add your .zshrc variants, tmux themes, nvim plugins (overrides samples).
   - inventory/hosts.ini: Add targets (e.g., [devhosts] server ansible_host=192.168.1.100 ansible_user=ubuntu).
3. **Test Connection**: `ansible all -i inventory/hosts.ini -m ping`.
4. **Dry Run**: `ansible-playbook -i inventory/hosts.ini site.yml --check --ask-become-pass`.
5. **Full Run**: `ansible-playbook -i inventory/hosts.ini site.yml --ask-become-pass --extra-vars "target_user=youruser"`.
6. **Selective**: `--tags base-installs,docker-setup` (install basics/Docker only); `--skip-tags security-harden` (skip hardening).
7. **Cloud/VM**: Run `--tags cloud-init` to generate cloud-config.yaml, then `multipass launch --cloud-init cloud-config.yaml` or AWS user-data. Set playbook_repo_url in vars for Git clone.
8. **Existing Users**: Run with target_user=existing; configs copy to home.
9. **Verify**: SSH to target, `docker ps` (Portainer), `nvim --version`, `zsh` (theme/plugins), `node --version` (NVM), `uv --version`.

### Use Cases
1. **New Linux Server Onboarding**: Run full playbook on fresh Ubuntu/Fedora VM via SSH inventory. Creates devuser, installs Docker/Portainer, shell/Nvim/dev envs, hardens security. Use case: Quick dev setup on AWS EC2.
2. **Multi-Host Dev Cluster**: Inventory with [devhosts] group (multiple servers); run `--limit devhosts --tags docker-setup` to install Docker on all. Use case: Team dev machines.
3. **Cloud Provisioning**: Generate cloud-config.yaml, deploy to cloud-init compatible VM (Multipass, Proxmox). Bootstraps user/packages, clones/runs playbook. Use case: Automated spin-up for CI/CD.
4. **Selective Dev Env**: `--tags dev-envs,shell-customize` for Python/JS + Zsh/Tmux only (skip Docker/security). Use case: Lightweight setup on existing server.
5. **macOS Laptop**: Inventory with mac host (ansible_python_interpreter=/usr/bin/python3); run full or --tags nvim-setup,dev-envs. Use case: Personal machine with Brew.
6. **Extending for New Env**: Add roles/go/tasks/main.yml (e.g., go install via package/curl), add 'go' to dev_envs in vars. Run --tags dev-envs. Use case: Add Rust/Cargo.
7. **Kubernetes Add-On**: Future role/kubernetes/tasks/main.yml (minikube install); toggle in enabled_roles. Use case: Local K8s dev.
8. **Rollback/Iterate**: Rerun with --check to verify idempotency; fixes.md for issues (e.g., add AUR helper for Arch).

### Use Cases (Expanded)
1. **New Linux Server Onboarding**: Run full playbook on fresh Ubuntu/Fedora VM via SSH inventory. Creates devuser, installs Docker/Portainer/Syncthing for services, Netdata for monitoring, shell/Nvim/dev envs (UV/Nix for tools), hardens security. Optionally installs GUI apps (Firefox, VLC, Bitwarden) and Powerline fonts if enable_gui/font_enable are true. Use case: Quick dev setup on AWS EC2 with file sync via Syncthing.
2. **Multi-Host Dev Cluster**: Inventory with [devhosts] group (multiple servers); run `--limit devhosts --tags docker-setup` to install Docker on all. Use case: Team dev machines with Netdata dashboards and Syncthing for code sharing.
3. **Cloud Provisioning**: Generate cloud-config.yaml, deploy to cloud-init compatible VM (Multipass, Proxmox). Bootstraps user/packages (docker/netdata/Nix), clones/runs playbook. Use case: Automated spin-up for CI/CD with monitoring and reproducible envs via Nix.
4. **Selective Dev Env**: `--tags dev-envs,shell-customize` for Python/JS/Nix + Zsh/Tmux only (skip Docker/security). Use case: Lightweight setup on existing server; use UV for fast pip, Nix for isolated packages.
5. **macOS Laptop**: Inventory with mac host (ansible_python_interpreter=/usr/bin/python3); run full or --tags nvim-setup,dev-envs. Installs GUI apps (Firefox, VLC, Bitwarden, etc.) and Powerline fonts via Brew Cask if enable_gui/font_enable are true. Use case: Personal machine with Brew; Nix for cross-platform tools.
6. **Extending for New Env**: Add roles/go/tasks/main.yml (e.g., go install via package/curl), add 'go' to dev_envs in vars. Run --tags dev-envs. Use case: Add Rust/Cargo via Nix flake.
7. **Monitoring/Sync Workflow**: Enable auto-updates; access Netdata :19999 for metrics, Syncthing :8384 for file sync. Use case: Self-maintained dev env with real-time monitoring and team file sharing.
8. **Kubernetes Add-On**: Future role/kubernetes/tasks/main.yml (minikube install); toggle in enabled_roles. Use case: Local K8s dev with Syncthing for config sync.

### Troubleshooting
- **Syntax Errors**: `ansible-playbook --syntax-check site.yml`.
- **Package Failures**: Check package_mgr in debug output; ensure repos updated in prerequisites.
- **SSH Issues**: Use --ask-become-pass; copy SSH keys for passwordless.
- **macOS**: Pre-install Ansible/Brew if needed; use raw module for initial tasks if Python missing.
- **Cloud-Init**: Verify generated yaml with cloud-init schema tools; test with Multipass.
- **Dotfiles**: If custom configs fail, check permissions (0644); Jinja2 in .zshrc.j2 uses vars like ansible_os_family.
- **Portainer**: Access http://target-ip:7770; initial setup prompts for admin user.
- **Syncthing**: Access GUI http://target-ip:8384; manual compose: cd ~/.docker-services/syncthing && docker-compose up (uses templated .yml + .env with resolved ports).
- **Netdata**: Dashboard http://target-ip:19999; auto-allowed in firewall.
- **Nix**: nix-env -iA nixpkgs.hello to test; multi-user for shared.
- **UV**: uv --version; standalone install to ~/.cargo/bin, PATH in .zshrc.
- **NVM/Bob**: Source .zshrc after run; Bob may need PATH update if not in /usr/local/bin.
- **Firewall Ports**: Auto-allowed for services (Syncthing/Netdata); customize service_ports var.

For bugs, add to fixes.md. Contribute: Edit roles/tasks/main.yml, test on VM, update tasks.md.

See readme.md for quick start, architecture.md for internals.
