# Ansible: one configuration, two servers

English · [Português](README.md)

Configuring one server by hand works. Repeating it on another, remembering every adjustment and finding out what someone changed afterward is a different story. This lab uses Ansible to explore that process with two small targets named `blue` and `green`.

The same role installs Nginx, publishes a page and configures each target from the inventory. The interesting part is running it again: understanding what changed, what stayed the same and how to recover configuration edited outside the playbook.

[![Tests](https://github.com/tommmdl/ansible-lab/actions/workflows/test.yml/badge.svg)](https://github.com/tommmdl/ansible-lab/actions/workflows/test.yml)

## Getting started

You need Linux/WSL, Docker accessible to your user, Python 3.12 or later with `venv`, Bash and curl. Ports 8003 and 8004 must be available. Preparation installs Python dependencies under `.local/`; if Compose is missing, automatic local installation supports Linux x86_64.

```bash
git clone https://github.com/tommmdl/ansible-lab.git
cd ansible-lab
bash scripts/prepare.sh
bash scripts/compose.sh up -d --build
bash scripts/ansible.sh playbook playbooks/site.yml
```

Open [blue](http://localhost:8003) and [green](http://localhost:8004). Both pages include Portuguese and English text and identify their target. They become available after the playbook finishes.

The “servers” are disposable containers. Ansible uses the Docker connection plugin, without SSH or systemd. Tasks change those containers; they do not install Nginx on your computer.

## Things to try

1. Run the playbook again and look for `changed=0` in the recap.
2. Use `--limit blue -e lab_environment=staging` to change one target only.
3. Edit the configuration inside `blue` and run `--check --diff` to see the predicted repair.
4. Apply the playbook and check when the reload handler runs.

```bash
bash scripts/ansible.sh playbook playbooks/site.yml --check --diff
bash scripts/ansible.sh playbook playbooks/site.yml --limit blue -e lab_environment=staging
```

The [usage guide](docs/guide.en.md) explains the inventory, variables and templates, along with check-mode and package-cache behavior.

## Checking the project

The full test needs fresh targets and changes only this lab. If containers are already running, finish your experiments and use `bash scripts/compose.sh down` first:

```bash
python3 tests/verify.py
```

It follows the initial configuration, an unchanged repeat, a change limited to `blue`, check mode and drift repair. Targets remain configured afterward so you can explore. The [recorded results](docs/validation.en.md) explain what actually ran and the limits of those checks.

All 16 checks passed locally and in GitHub Actions, including `changed=0` reruns, changes limited to one target and drift repair.

## When you are done

```bash
bash scripts/compose.sh down
```

This removes both targets and their pages. There is no database or persistent volume in this exercise. The Python environment, collection and reports remain under ignored `.local/`.

A next step is to take the same inventory/role structure to machines reached over SSH, with users and privileges chosen for that environment. This first lab stays on local Docker.

[See the other portfolio projects](https://github.com/tommmdl/devops-portfolio)
