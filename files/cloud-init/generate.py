#!/usr/bin/env python3
"""
Cloud-Init Config Generator
This script generates multiple cloud-init configurations based on user selection.
It runs the Ansible cloud-init task with variant-specific variables.
Assisted by Cline on 2025-10-02.
"""

import os
import sys
import subprocess
import shutil

PLAYBOOK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root

def log_info(message):
    print(f"[INFO] {message}")

def log_success(message):
    print(f"[SUCCESS] {message}")

def log_error(message):
    print(f"[ERROR] {message}", file=sys.stderr)

def run_ansible_generate(variant, extra_vars_file, output_path):
    """Run Ansible to generate cloud-config for a variant."""
    inventory = "localhost,"  # Local connection for generation
    command = [
        "ansible-playbook",
        "-i", inventory,
        "site.yml",
        "--tags", "cloud-init",
        "--connection", "local",
        "--batch",  # Suppress interactive prompts for Windows compatibility
        "--extra-vars", f"cloud_init_path={output_path} @{extra_vars_file}"
    ]
    log_info(f"Generating {variant} config...")
    try:
        result = subprocess.run(command, cwd=PLAYBOOK_DIR, check=True, text=True, capture_output=True)
        log_success(f"Generated {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to generate {variant}: {e.stderr}")
        return False

def prompt_for_variant():
    """Prompt user for variant or custom selection."""
    variants = {
        "minimal": "Basic setup (essentials only)",
        "dev": "Dev setup ( + dev-envs, fonts, terminals)",
        "full": "Full setup ( + GUI, Nix GUI)"
    }
    print("Select a cloud-init variant:")
    for key, desc in variants.items():
        print(f"  {key}: {desc}")
    print("  custom: Custom selection")
    
    choice = input("Enter choice (minimal/dev/full/custom): ").strip().lower()
    if choice not in variants and choice != "custom":
        log_error("Invalid choice. Defaulting to minimal.")
        choice = "minimal"
    
    if choice == "custom":
        # Simple prompts for major features
        enable_gui = input("Enable GUI apps (VSCode, etc.)? (y/n): ").strip().lower().startswith('y')
        enable_nix_gui = input("Enable Nix GUI apps? (y/n): ").strip().lower().startswith('y')
        dev_envs_input = input("Dev environments (comma-separated: python,js,go,lua or 'all'): ").strip()
        dev_envs = dev_envs_input.split(',') if dev_envs_input != 'all' else ['python', 'js', 'go', 'lua']
        harden_level = input("Harden level (basic/standard/full): ").strip() or "standard"
        return {
            "variant": "custom",
            "enable_gui": enable_gui,
            "enable_nix_gui": enable_nix_gui,
            "dev_envs": dev_envs,
            "harden_level": harden_level
        }
    else:
        return {"variant": choice}

def main():
    if not shutil.which("ansible-playbook"):
        log_error("Ansible not found. Install Ansible first.")
        sys.exit(1)
    
    selection = prompt_for_variant()
    variant = selection["variant"]
    output_base = f"files/cloud-init/cloud-config-{variant}"
    
    if variant == "minimal":
        vars_file = "files/cloud-init/minimal.yml"
        output_path = f"{output_base}.yaml"
        run_ansible_generate("minimal", vars_file, output_path)
    elif variant == "dev":
        vars_file = "files/cloud-init/dev.yml"
        output_path = f"{output_base}.yaml"
        run_ansible_generate("dev", vars_file, output_path)
    elif variant == "full":
        vars_file = "files/cloud-init/full.yml"
        output_path = f"{output_base}.yaml"
        run_ansible_generate("full", vars_file, output_path)
    else:  # custom
        # Create temp vars file for custom
        temp_vars = f"{output_base}-custom-vars.yml"
        with open(temp_vars, "w") as f:
            f.write("---\n")
            f.write(f"enable_gui: {selection['enable_gui']}\n")
            f.write(f"enable_nix_gui: {selection['enable_nix_gui']}\n")
            f.write(f"dev_envs: ['{','.join(selection['dev_envs'])}']\n")
            f.write(f"harden_level: {selection['harden_level']}\n")
        output_path = f"{output_base}-custom.yaml"
        run_ansible_generate("custom", temp_vars, output_path)
        os.remove(temp_vars)  # Cleanup
    
    log_success(f"Cloud-init config ready at {output_path}. Use for VM/cloud provisioning.")

if __name__ == "__main__":
    main()
