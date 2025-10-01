# Ansible Dev Environment Automation - README

## Introduction
This project automates the setup of a developer environment on Linux (Debian, Ubuntu, Fedora, Rocky, Arch) and macOS using Ansible. It installs base tools, Docker/Portainer/Syncthing, Netdata monitoring, shell customizations (Zsh, Tmux), Neovim (via Bob with multi-distro support), and dev environments (Python with standalone UV, JS/Node, Nix). The setup is modular, idempotent, and supports multi-user/global configs via `/etc/skel/`. Includes cloud-init for cloud/VM bootstrapping with enhanced bootstrap (Netdata/Docker/Nix).

**Assisted by Cline (powered by xAI Grok model) on 2025-09-25.**

See `architecture.md` for design details, `tasks.md` for progress.

## Prerequisites
- **Host (Control Machine)**: Ansible 2.10+ installed (`pip install ansible` or via package manager). Python 3.8+.
- **Target Machines**:
  - Linux: SSH access (port 22 open), sudo privileges (passwordless if possible via `ssh-copy-id`).
  - macOS: Ansible installed on target (or run remotely); SSH enabled.
  - Python on targets (usually pre-installed; use `raw` module if missing).
- **Collections**: Install via `ansible-galaxy install -r requirements.yml` (includes community.docker, homebrew).
- **Inventory**: SSH keys for passwordless auth recommended.
- **No Vault**: No secrets initially; add ansible-vault later if needed.

## Project Structure
Refer to `architecture.md` for full layout. Key files:
- `site.yml`: Main playbook.
- `roles/`: Modular components (os-detection, prerequisites, etc.).
- `files/dotfiles/`: Config templates (add your .zshrc, tmux.conf here).
- `group_vars/all.yml`: Customize vars (e.g., `target_user: yourusername`).
- `inventory/hosts.ini`: Example inventory.

## Setup
1. **Clone/Initialize Project**:
   ```
   git clone <your-repo>  # Or create dir and copy files
   cd ansible-dev-env
   ```

2. **Install Dependencies**:
   ```
   ansible-galaxy install -r requirements.yml
   ```

3. **Customize**:
   - Edit `group_vars/all.yml`: Set `target_user`, `enabled_roles`, `dev_envs: ['python', 'js']`, `portainer_port: 7770`, `service_ports` for firewall (e.g., Syncthing/Netdata ports), `enable_auto_updates: true`.
   - Add your dotfiles to `files/dotfiles/` (e.g., tmux.conf, .zshrc.j2 with OS conditionals).
   - For macOS targets: Create `host_vars/mac.yml` with `ansible_python_interpreter: /usr/bin/python3`.
   - Inventory: Edit `inventory/hosts.ini` (e.g., `[devhosts]\nserver ansible_host=192.168.1.100`).

4. **Test Connection**:
   ```
   ansible all -i inventory/hosts.ini -m ping
   ```

## Running the Playbook
Execute on targets via SSH. Runs all phases sequentially; idempotent (safe to rerun).

1. **Full Setup**:
   ```
   ansible-playbook -i inventory/hosts.ini site.yml --ask-become-pass
   ```
   - `--ask-become-pass`: If sudo password required.
   - `--extra-vars "target_user=youruser"`: Override user.

2. **Selective Runs** (Modular):
   - Specific roles: `--tags base-installs,docker-setup`.
   - Skip phases: `--skip-tags security-harden`.
   - Limit hosts: `--limit server1`.

3. **For Existing Users**: Set `target_user` to apply configs (Zsh shell, dotfiles copy).
4. **For New Users**: Run prerequisites (creates 'devuser'); future logins get /etc/skel/ configs.
5. **macOS**: `--limit mac-hosts` (group in inventory); ensures Brew install.

## Cloud-Init Integration
For automated VM/cloud provisioning:
1. Run cloud-init role: `ansible-playbook -i inventory/hosts.ini site.yml --tags cloud-init` (generates `cloud-config.yaml`).
2. Deploy to VM (e.g., AWS user-data, Multipass `--cloud-init cloud-config.yaml`).
3. Cloud-init creates user, installs basics, runs `ansible-playbook site.yml` locally.

Example `cloud-config.yaml` (generated):
```yaml
#cloud-config
users:
  - name: devuser
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/zsh
packages:
  - curl
  - git
runcmd:
  - ansible-playbook /path/to/site.yml
```

## Testing
- **Local VM**: Use Vagrant (add Vagrantfile in root):
  ```
  vagrant up ubuntu  # Or fedora
  ansible-playbook -i vagrant-hosts site.yml
  ```
- **Multipass** (Ubuntu/VMs): `multipass launch --name test --cloud-init cloud-config.yaml`.
- **Dry Run**: `ansible-playbook site.yml --check`.
- Verify: SSH to target, check `docker ps` (Portainer/Syncthing), `netdata` at :19999, `uv --version`, `nix --version`, `zsh --version`.

## Customization & Extensibility
- **Add Dev Env**: New sub-role in `dev-envs/tasks/` (e.g., go-install.yml); add to `dev_envs` list.
- **Dotfiles**: Use Jinja2 templates for OS-specific (e.g., alias for nala on Debian).
- **Auto-Updates**: Set `enable_auto_updates: true` in vars.
- **Security**: `harden_level: full` for advanced (firewalld rules, fail2ban); customize `service_ports` for additional auto-allowed ports.
- **Aliases for Nvim**: Added to .zshrc: `alias nvim-nvchad='NVIM_APPNAME=nvchad nvim'`.
- **Syncthing**: Customize ports in vars; manual compose in ~/.docker-services/syncthing with .env.
- **Netdata**: Access :19999; disable telemetry in vars if needed.
- **Nix**: Set nix_multi_user: false for single-user; add channels in .zshrc.

## Troubleshooting
- SSH Issues: Ensure `ansible_ssh_private_key_file` in inventory.
- Package Errors: Check distro support in roles (add conditionals).
- macOS Brew: Run `noninteractive: true` in homebrew tasks.
- Logs: `--verbose` for debug.
- Syncthing Compose: If vars unresolved, ensure .env in ~/.docker-services/syncthing; use docker-compose up -d.
- Firewall Ports: Auto-allowed for Portainer/Syncthing/Netdata; check ufw status or firewalld list-ports.
- Nix Install: If daemon fails, set nix_multi_user: false; source .zshrc for PATH.

See `fixes.md` for known issues. For contributions: Edit roles/tasks/main.yml.

## License
MIT (or specify your preference).
