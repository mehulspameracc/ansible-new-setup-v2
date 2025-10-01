# Fixes and Known Issues Tracking

This document tracks bugs, issues, and resolutions encountered during development and testing of the Ansible Dev Environment project. Issues are categorized as Open or Resolved. Include details like affected roles, distros, and fixes applied.

**Assisted by Cline (powered by xAI Grok model) on 2025-09-25.**

## Open Issues
These are unresolved problems or potential gotchas.

- **Issue: Arch Linux AUR Packages**  
  ID: ARCH-001  
  Description: Core apps like `fzf` or plugins may require AUR (e.g., yay/paru). Current roles use official pacman repos only.  
  Affected: base-installs, shell-customize roles.  
  Priority: Medium  
  Workaround: Manual AUR install post-playbook; or add conditional AUR helper task.  
  Reported: 2025-09-25 20:01  

- **Issue: macOS Ansible Requirement**  
  ID: MAC-001  
  Description: Targets need Ansible installed for remote execution; Brew install in prerequisites may fail if Python missing.  
  Affected: All roles on Darwin.  
  Priority: High  
  Workaround: Pre-install Ansible via Brew on macOS targets; use `raw` module for initial setup.  
  Reported: 2025-09-25 20:01  

- **Issue: Cloud-Init Path Assumptions**  
  ID: CLOUD-001  
  Description: Generated cloud-config.yaml assumes playbook path; needs dynamic path handling for VM mounts.  
  Affected: cloud-init role.  
  Priority: Low  
  Workaround: Customize runcmd with absolute paths.  
  Reported: 2025-09-25 20:01  

- **Issue: Portainer Port Conflicts**  
  ID: DOCKER-001  
  Description: If port 7770 in use, container fails; no auto-port detection.  
  Affected: docker-setup role.  
  Priority: Medium  
  Workaround: Pre-check with `netstat`; or var for custom port.  
  Reported: 2025-09-25 20:01  

## Resolved Fixes
These issues have been addressed.

- **UV Installation**: Switched to standalone Astral script (curl -LsSf https://astral.sh/uv/install.sh | sh) to ~/.cargo/bin for optimal performance without Python deps; PATH added in .zshrc.j2. Resolved: 2025-09-26.

- **Syncthing Docker-Compose Variables**: Templated .j2 to resolved .yml and created .env with ports/paths for manual use in ~/.docker-services/syncthing; removed static copy. Resolved: 2025-09-26.

- **Firewall Port Allowance**: Added service_ports var and looped rules for ufw/firewalld to auto-allow Syncthing/Netdata/Portainer ports; conditional on harden_level. Resolved: 2025-09-26.

- **Cloud-Init Bootstrap**: Enhanced cloud-config.j2 with Netdata/Docker/Nix packages and runcmd/setup.sh for curl installs/playbook --skip-tags cloud-init. Resolved: 2025-09-26.


## General Notes
- **Testing Focus**: Prioritize VM tests (Vagrant for Ubuntu/Fedora, Multipass for cloud-init) to catch distro-specific issues.
- **Debugging**: Use `--verbose` and check Ansible logs. For Docker, verify with `docker logs portainer`.
- **Updates**: After fixes, update `tasks.md` and test idempotency (`ansible-playbook --check`).

Refer to `architecture.md` for considerations that may lead to new issues. Report new ones here.
