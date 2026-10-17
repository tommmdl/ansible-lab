#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
export ANSIBLE_CONFIG="$PWD/ansible.cfg"
export ANSIBLE_COLLECTIONS_PATH="$PWD/.local/collections"
export ANSIBLE_HOME="$PWD/.local/ansible-home"
export ANSIBLE_LOCAL_TEMP="$PWD/.local/tmp"
export ANSIBLE_GALAXY_CACHE_DIR="$PWD/.local/galaxy-cache"
case "${1:-}" in
  playbook|inventory|galaxy|doc)
    tool="ansible-$1"
    shift
    ;;
  *) tool=ansible ;;
esac
exec ".local/venv/bin/$tool" "$@"
