# Nix Package Manager Guide

Nix is a powerful package manager for Linux and macOS that enables reproducible builds and declarative system configuration. It uses a purely functional approach, ensuring that every package is built in isolation and cached immutably in `/nix/store`.

## Why Use Nix?

- **Reproducibility**: Same build inputs always produce the same output.
- **Atomic Upgrades**: Roll back to any previous state instantly.
- **Multi-User**: Multiple users can install packages without conflicts.
- **Cross-System**: Share configurations across different Linux distributions and macOS.
- **Development Environments**: Create isolated, disposable environments with flakes.

## Basic Concepts

### `/nix/store`
Every package is installed to `/nix/store` with a unique hash, ensuring no conflicts. Example: `/nix/store/abc123-firefox-115.0`.

### Channels
Nix Channels are repositories of packages. You can add channels with `nix-channel --add` and update with `nix-channel --update`.

### Flakes
Flakes are a newer way to manage Nix configurations. They provide:
- Lockfiles for reproducibility.
- Easy sharing of configurations.
- Development environments (`devShells`).

## Installation

The playbook installs Nix automatically (multi-user) if `nix_multi_user` is true in `group_vars/all.yml`.

## Usage

### Installing Packages
```bash
# Via nix-env (legacy)
nix-env -iA nixpkgs.packagename

# Via flakes (recommended)
nix profile install nixpkgs#packagename
```

### Using Flakes
1. **Create a flake**:
   ```bash
   nix flake new ~/my-flake
   ```
   Edit `flake.nix` to define inputs and outputs.

2. **Update flake lock**:
   ```bash
   nix flake update
   ```

3. **Enter development shell**:
   ```bash
   nix develop
   ```

### Example: Brave Browser Flake
```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      packages = [ nixpkgs.legacyPackages.x86_64-linux.brave ];
    };
  };
}
```
Usage: `nix develop` in the directory with this flake.

## Storage

- **Derivations**: `/nix/store` (immutable)
- **Build Cache**: `~/.cache/nix` (temporary build artifacts)
- **User Config**: `~/.config/nixpkgs/config.nix` (for overlays, settings)
- **Flakes**: `~/.config/nix/flake.nix` (flake registry)

## Missing GUI Apps

For GUI apps not available in distro repos, use Nix flakes:

1. **Brave Browser**:
   ```nix
   # flake.nix
   {
     inputs = { nixpkgs.url = "github:NixOS/nixpkgs"; };
     outputs = { self, nixpkgs }: {
       devShells.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
         packages = [ nixpkgs.legacyPackages.x86_64-linux.brave ];
       };
     };
   }
   ```
   Run: `nix develop`

2. **Zed Editor**:
   ```nix
   # flake.nix
   {
     inputs = { nixpkgs.url = "github:NixOS/nixpkgs"; };
     outputs = { self, nixpkgs }: {
