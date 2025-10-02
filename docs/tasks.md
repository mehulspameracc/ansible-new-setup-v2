# Task Tracking for Ansible Dev Environment Project

This document tracks the development and implementation of the Ansible playbook. Tasks are categorized by creation, updates, and completion. Dates are in YYYY-MM-DD HH:MM format (IST).

**Assisted by Cline (powered by xAI Grok model) on 2025-09-25.**

## Created Tasks
These are new tasks added during planning/implementation.

- **Task: Create project structure and initial docs (architecture.md)**  
  Created: 2025-09-25 19:59  
  Description: Establish /docs/architecture.md with high-level design.

- **Task: Create additional docs (tasks.md, readme.md, fixes.md)**  
  Created: 2025-09-25 20:00  
  Description: Generate tracking and usage documents.

- **Task: Implement os-detection role**  
  Created: 2025-09-25 20:00  
  Description: Role to gather facts and set package_mgr var for multi-distro support.

- **Task: Implement prerequisites role**  
  Created: 2025-09-25 20:00  
  Description: Non-root user creation, sudo, PGP keys, repo tweaks (Nala, dnf.conf).

- **Task: Implement security-harden role**  
  Created: 2025-09-25 20:00  
  Description: Firewall, SSH hardening, auto-updates, fail2ban.

- **Task: Implement cloud-init role**  
  Created: 2025-09-25 20:00  
  Description: Generate cloud-config.yaml for bootstrapping.

- **Task: Create local Ansible installation script (files/install_ansible.sh)**  
  Created: 2025-09-30 02:45  
  Description: Develop a shell script in the `files` directory that installs Ansible on the local host system. The script should interactively prompt the user to select desired features from the Ansible project (e.g., specific roles, environments) and then execute the Ansible playbook to install the selected components to the local host system.

- **Task: Create remote Ansible deployment script (files/deploy_ansible_remote.sh)**  
  Created: 2025-09-30 02:45  
  Description: Develop a shell script in the `files` directory that interactively prompts the user for remote server details (e.g., IP addresses, SSH credentials) and the features to be installed on those remote servers. The script should then execute the Ansible playbook against the specified targets to configure them accordingly.

- **Task: Create multiple cloud-init config variants using group_vars (minimal, dev, full)**  
  Created: 2025-10-02 01:00  
  Description: Create separate group_vars files in files/cloud-init/ (minimal.yml, dev.yml, full.yml) to parameterize cloud-init generation for different profiles (basics, dev tools, full GUI/Nix).

- **Task: Create cloud-init generator script (files/cloud-init/generate.py)**  
  Created: 2025-10-02 01:00  
  Description: Develop a Python script that prompts for variant selection, sets vars, runs the cloud-init Ansible task, and outputs named configs (e.g., cloud-config-minimal.yaml).

- **Task: Update docs/ansible_scripts_guide.md with Cloud-Init Customization section**  
  Created: 2025-10-02 01:00  
  Description: Add section explaining variants, generator usage, and integration with provisioning tools.

- **Task: Update Python Ansible scripts (install_ansible.py, deploy_ansible_remote.py) with numbered menu input**  
  Created: 2025-10-02 15:30  
  Description: Replace raw key input (msvcrt/termios) with a numbered list and input() prompts for better cross-platform compatibility and reliability. Add 'q' for quit.

- **Task: Create inventory/ directory and hosts.ini file**  
  Created: 2025-10-02 15:30  
  Description: Ensure the inventory directory exists and a default hosts.ini file is present for Ansible.

- **Task: Ensure group_vars/all.yml exists**  
  Created: 2025-10-02 15:30  
  Description: Verify that group_vars/all.yml is present and correctly configured.

- **Task: Create proposed-tree.md directory structure documentation**  
  Created: 2025-10-02 15:30  
  Description: Document the expected Ansible project directory structure in proposed-tree.md.

- **Task: Refine playbook structure - os-detection first, separate playbooks**  
  Created: 2025-10-02 15:45  
  Description: Modify playbooks to ensure os-detection runs first to inform subsequent roles. Consider creating separate playbooks for different configurations (e.g., local_setup.yml, remote_setup.yml, minimal_setup.yml).

## Updated Tasks
- **Task: Refine playbook structure - os-detection first, separate playbooks**  
  Updated: 2025-10-02 16:16  
  Description: Created new playbooks: local_setup.yml (for localhost), remote_setup.yml (for remote_servers), and minimal_setup.yml (for all with a minimal role set). Updated install_ansible.py, deploy_ansible_remote.py, install_ansible.sh, and deploy_ansible_remote.sh to use these new playbooks. The site.yml playbook remains as a general-purpose playbook.

## Completed Tasks
These tasks have been finished.

- **Task: Create project structure and initial docs (architecture.md)**  
  Completed: 2025-09-25 20:00  
  Status: architecture.md created successfully.

- **Task: Create additional docs (tasks.md, readme.md, fixes.md)**  
  Completed: 2025-09-25 20:01  
  Status: All docs created successfully.

- **Task: Create group_vars/all.yml and requirements.yml**  
  Completed: 2025-09-25 20:02  
  Status: Files created with defaults and collections.

- **Task: Create site.yml main playbook**  
  Completed: 2025-09-25 20:05  
  Status: Main playbook created with dynamic role inclusion and fixes applied.

- **Task: Implement base-installs role**  
  Completed: 2025-09-25 20:07  
  Status: tasks/main.yml created with distro-specific package installs.

- **Task: Implement docker-setup role**  
  Completed: 2025-09-25 20:08  
  Status: tasks/main.yml created with multi-distro Docker and Portainer setup.

- **Task: Implement shell-customize role**  
  Completed: 2025-09-25 20:08  
  Status: tasks/main.yml created with Zsh/Tmux installs and configs.

- **Task: Implement nvim-setup role**  
  Completed: 2025-09-25 20:09  
  Status: tasks/main.yml created with Bob install, distros, and aliases.

- **Task: Implement dev-envs role**  
  Completed: 2025-09-25 20:09  
  Status: tasks/main.yml created with Python/JS setups and path additions.

- **Task: Create files/dotfiles/ with placeholders**  
  Completed: 2025-09-25 20:10  
  Status: Sample .zshrc.j2, .tmux.conf, init.lua created; add personal configs.

- **Task: Create guide.md**  
  Created: 2025-09-25 20:13  
  Description: Detailed user guide with flow, usage, use cases, troubleshooting.

- **Task: Test and finalize**  
  Completed: 2025-09-25 20:13  
  Status: Project complete; guide.md added, ready for VM testing as per readme.md.

- **Task: Implement Netdata monitoring in base-installs**  
  Completed: 2025-09-26 20:00  
  Status: Added kickstart script install, systemd start/enable; port 19999.

- **Task: Add Syncthing Docker container and compose files in docker-setup**  
  Completed: 2025-09-26 20:05  
  Status: Deployed container with ports/volumes; copied compose to home/skel.

- **Task: Integrate Nix package manager in dev-envs**  
  Completed: 2025-09-26 20:10  
  Status: Installed via curl script (multi-user option); added PATH to .zshrc/skel.

- **Task: Switch UV to standalone install in dev-envs**  
  Completed: 2025-09-26 20:15  
  Status: Replaced pip with official installer script; PATH via .cargo/bin.

- **Task: Resolve Syncthing docker-compose variables (template .j2 + .env)**  
  Completed: 2025-09-26 20:20  
  Status: Added template task for resolved .yml; created .env from vars for manual use.

- **Task: Add auto-ports allowance for services (Syncthing/Netdata) in security-harden**  
  Completed: 2025-09-26 20:25  
  Status: Defined service_ports var; looped firewall rules (ufw/firewalld/pf) conditional on harden_level.

- **Task: Update cloud-init for new features (Netdata, Docker, Nix bootstrap)**  
  Completed: 2025-09-26 20:30  
  Status: Enhanced cloud-config.j2 with packages/users; runcmd for installs/playbook.

- **Task: Update existing docs (architecture, guide, README, fixes) for new implementations**  
  Completed: 2025-09-26 20:35  
  Status: Added sections for Netdata/Syncthing/Nix/UV/auto-ports/cloud-init; troubleshooting for compose.

- **Task: Create comprehensive_implementation.md**  
  Completed: 2025-09-26 20:40  
  Status: New doc with full breakdown, vars table, use cases, extensibility.

- **Task: Implement system-wide fonts from files/list-mt25 with skel support**  
  Completed: 2025-09-28 15:00  
  Status: Added to base-installs: copy to /usr/share/fonts (Linux) /Library/Fonts (mac), fc-cache Linux, skel/.local/share/fonts.

- **Task: Add Ghostty and Alacritty terminals in base-installs**  
  Completed: 2025-09-28 15:05  
  Status: OS-specific installs (brew cask mac, apt/dnf/pacman/yay Linux).

- **Task: Copy Ghostty/Alacritty configs to .config/skel**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-30 01:30  
  Status: Handled by the dedicated 'terminals' role, which copies configs to user home and /etc/skel/.config/.

- **Task: Add Go and Lua to dev-envs role**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-30 01:30  
  Description: Update dev_envs var and add install tasks for Go (package/curl) and Lua (lua5.4 luarocks) with PATH in .zshrc/skel.

- **Task: Add Fedora FFmpeg swap in prerequisites**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-30 01:30  
  Description: Conditional dnf swap ffmpeg-free ffmpeg --allowerasing for Fedora.

- **Task: Add Mac Homebrew CLI and Cask installs in base-installs**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-30 01:30  
  Description: Install CLI tools (bc, cjson, etc.) and GUI casks (bitwarden, alacritty, etc.) on macOS.

- **Task: Add Linux GUI app installs in base-installs**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-30 01:30  
  Description: Install Firefox, VLC, qbittorrent, etc. via OS package managers (apt/dnf/pacman/yay) for all distros; fallback to Nix flakes for missing.

- **Task: Create Nix package manager guide and sample flakes**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-29 23:56  
  Description: Write docs/nix_guide.md with explanation, usage, storage; create files/nix/ with sample flake.nix for each missing GUI app (brave, zed, etc.).

- **Task: Expand Kubernetes note in architecture.md**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-29 23:27  
  Description: Add detailed future section with stub task for minikube/k9s and use cases.

- **Task: Create comprehensive_implementation.md**  
  Created: 2025-09-25 20:40  
  Completed: 2025-09-29 23:28  
  Status: New doc with full breakdown, vars table, use cases, extensibility.

- **Task: Update docs for new roles and variables (fonts, gui-installs, terminals, enable_gui, font_enable, Go/Lua in dev-envs)**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-30 01:30  
  Description: Update architecture.md, comprehensive_implementation.md, guide.md with new roles, variables, and functionalities.

- **Task: Create new gui-installs role**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-29 19:47  
  Description: Create roles/gui-installs/tasks/main.yml for installing GUI apps on Linux (Firefox, VLC, Bitwarden, etc.) and macOS (via Homebrew Cask) when enable_gui is true.

- **Task: Add gui-installs to site.yml enabled_roles default**  
  Created: 2025-09-29 16:00  
 ansible-playbook -i inventory/hosts-old.ini site.yml --ask-become-pass --ask-pass --tags os-detection,base-installs,docker-setup,fonts,nvim-setup,shell-customize,terminals,prerequisite -vvvv
ansible-playbook [core 2.14.18]
  config file = None
  configured module search path = ['/home/docker/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python3/dist-packages/ansible
  ansible collection location = /home/docker/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/bin/ansible-playbook
  python version = 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] (/usr/bin/python3)
  jinja version = 3.1.2
  libyaml = True
No config file found; using defaults
SSH password:
BECOME password[defaults to SSH password]:
setting up inventory plugins
host_list declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
script declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
auto declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
yaml declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
Parsed /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini inventory source with ini plugin
Loading callback plugin default of type stdout, v2.0 from /usr/lib/python3/dist-packages/ansible/plugins/callback/default.py
Skipping callback 'default', as we already have a stdout callback.
Skipping callback 'minimal', as we already have a stdout callback.
Skipping callback 'oneline', as we already have a stdout callback.

PLAYBOOK: site.yml *****************************************************************************
Positional arguments: site.yml
verbosity: 4
connection: smart
timeout: 10
ask_pass: True
become_method: sudo
become_ask_pass: True
tags: ('os-detection', 'fonts', 'shell-customize', 'docker-setup', 'prerequisite', 'terminals', 'nvim-setup', 'base-installs')
inventory: ('/home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini',)
forks: 5
1 plays in site.yml
Read vars_file 'group_vars/all.yml'
Read vars_file 'group_vars/all.yml'
Read vars_file 'group_vars/all.yml'

PLAY [Ansible Dev Environment Setup] ***********************************************************
ERROR! 'item' is undefined. 'item' is undefined
 ansible-playbook -i inventory/hosts-old.ini site.yml --ask-become-pass --ask-pass --tags os-detection,base-installs,docker-setup,fonts,nvim-setup,shell-customize,terminals,prerequisite -vvvv
ansible-playbook [core 2.14.18]
  config file = None
  configured module search path = ['/home/docker/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python3/dist-packages/ansible
  ansible collection location = /home/docker/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/bin/ansible-playbook
  python version = 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] (/usr/bin/python3)
  jinja version = 3.1.2
  libyaml = True
No config file found; using defaults
SSH password:
BECOME password[defaults to SSH password]:
setting up inventory plugins
host_list declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
script declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
auto declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
yaml declined parsing /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini as it did not pass its verify_file() method
Parsed /home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini inventory source with ini plugin
Loading callback plugin default of type stdout, v2.0 from /usr/lib/python3/dist-packages/ansible/plugins/callback/default.py
Skipping callback 'default', as we already have a stdout callback.
Skipping callback 'minimal', as we already have a stdout callback.
Skipping callback 'oneline', as we already have a stdout callback.

PLAYBOOK: site.yml *****************************************************************************
Positional arguments: site.yml
verbosity: 4
connection: smart
timeout: 10
ask_pass: True
become_method: sudo
become_ask_pass: True
tags: ('os-detection', 'fonts', 'shell-customize', 'docker-setup', 'prerequisite', 'terminals', 'nvim-setup', 'base-installs')
inventory: ('/home/docker/repos/ansible-new-setup-v2/inventory/hosts-old.ini',)
forks: 5
1 plays in site.yml
Read vars_file 'group_vars/all.yml'
Read vars_file 'group_vars/all.yml'
Read vars_file 'group_vars/all.yml'

PLAY [Ansible Dev Environment Setup] ***********************************************************
ERROR! 'item' is undefined. 'item' is undefined
  Completed: 2025-09-29 19:49  
  Description: Update site.yml to include 'gui-installs' in the default enabled_roles list.

- **Task: Create Nix sample flakes in files/nix_guide/samples/**  
  Created: 2025-09-29 16:00  
  Completed: 2025-09-29 23:02  
  Description: Create individual flake.nix files for brave, zed, zen, postman, floorp, ferdium in docs/nix_guide/samples/.

- **Task: Refine GUI application installation strategy**  
  Created: 2025-09-29 23:41  
  Completed: 2025-09-30 01:30  
  Description: Consolidated all GUI app installs (Linux/macOS) into the gui-installs role, ensuring a consistent set is installed when enable_gui is true. Moved GUI-specific apps like ghostty, alacritty out of base-installs.

- **Task: Refine terminal emulator installation strategy**  
  Created: 2025-09-29 23:41  
  Completed: 2025-09-30 01:30  
  Description: Moved terminal emulator installs (ghostty, alacritty) to a dedicated 'terminals' role, independent of enable_gui.

- **Task: Refine font installation strategy**  
  Created: 2025-09-29 23:41  
  Completed: 2025-09-30 01:30  
  Description: Installed Powerline/Nerd Fonts via the 'fonts' role, independent of enable_gui, as they benefit terminal users even on remote servers.

- **Task: Update GUI application lists for macOS and Linux**  
  Created: 2025-09-29 23:41  
  Completed: 2025-09-30 01:30  
  Description: Used the comprehensive GUI app list provided for macOS (CLI tools: bc, cjson, etc.; Casks: bitwarden, alacritty, etc.) and ensured a comparable set is available for Linux, including ferdium, floorp, waterfox, zed, zen, vscode, zerotier, tailscale, firefox-dev, ungoogled-chromium, brave-browser.

- **Task: Create dedicated nix-gui-installs role**  
  Created: 2025-09-30 01:33  
  Completed: 2025-09-30 01:33  
  Description: Create a new role `roles/nix-gui-installs/tasks/main.yml` to install GUI applications via Nix flakes (e.g., brave, zed, zen, postman, floorp, ferdium) when a new variable `enable_nix_gui` is true. This role will be independent of the main `gui-installs` role. Role and variable added.

- **Task: Add nix-gui-installs to site.yml enabled_roles default**  
  Created: 2025-09-30 01:33  
  Completed: 2025-09-30 01:33  
  Description: Update site.yml to include 'nix-gui-installs' in the default enabled_roles list.

- **Task: Create multiple cloud-init config variants using group_vars (minimal, dev, full)**  
  Created: 2025-10-02 01:00  
  Description: Create separate group_vars files in files/cloud-init/ (minimal.yml, dev.yml, full.yml) to parameterize cloud-init
