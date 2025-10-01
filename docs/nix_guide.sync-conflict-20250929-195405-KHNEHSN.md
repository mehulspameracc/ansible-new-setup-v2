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
