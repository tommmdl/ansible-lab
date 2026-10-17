#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mkdir -p .local
if [ ! -x .local/venv/bin/python ]; then
  python3 -m venv .local/venv
fi
requirements=requirements.txt
if [ -f requirements.lock ]; then requirements=requirements.lock; fi
.local/venv/bin/python -m pip install --disable-pip-version-check -r "$requirements"
bash scripts/ansible.sh galaxy collection install -r requirements.yml --no-deps
if ! docker compose version >/dev/null 2>&1; then
  target="$PWD/.local/docker/cli-plugins"
  mkdir -p "$target"
  if [ ! -x "$target/docker-compose" ]; then
    test "$(uname -s)" = Linux
    test "$(uname -m)" = x86_64
    base=https://github.com/docker/compose/releases/download/v5.6.0
    curl --fail --location "$base/docker-compose-linux-x86_64" -o "$target/docker-compose"
    curl --fail --location "$base/docker-compose-linux-x86_64.sha256" -o .local/compose.sha256
    python3 - <<'PY'
from pathlib import Path
import hashlib
p = Path('.local/docker/cli-plugins/docker-compose')
if hashlib.sha256(p.read_bytes()).hexdigest() != Path('.local/compose.sha256').read_text().split()[0]:
    raise SystemExit('Compose checksum mismatch')
p.chmod(0o755)
PY
  fi
fi
bash scripts/ansible.sh --version
bash scripts/compose.sh version
