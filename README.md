# Ansible: uma configuração, dois servidores

[English](README.en.md) · Português

Configurar um servidor à mão funciona. Repetir o processo em outro, lembrar cada ajuste e descobrir o que alguém mudou depois já é outra história. Este laboratório usa Ansible para explorar esse caminho com dois alvos pequenos, chamados `blue` e `green`.

O mesmo role instala Nginx, publica uma página e configura cada alvo a partir do inventário. A graça está em rodar de novo: entender o que mudou, o que ficou igual e como recuperar uma configuração alterada fora do playbook.

[![Testes](https://github.com/tommmdl/ansible-lab/actions/workflows/test.yml/badge.svg)](https://github.com/tommmdl/ansible-lab/actions/workflows/test.yml)

## Para começar

Você precisa de Linux/WSL, Docker acessível ao seu usuário, Python 3.12 ou superior com `venv`, Bash e curl. As portas 8003 e 8004 devem estar livres. O preparo instala as dependências Python em `.local/`; se faltar Compose, o instalador local atende Linux x86_64.

```bash
git clone https://github.com/tommmdl/ansible-lab.git
cd ansible-lab
bash scripts/prepare.sh
bash scripts/compose.sh up -d --build
bash scripts/ansible.sh playbook playbooks/site.yml
```

Abra [blue](http://localhost:8003) e [green](http://localhost:8004). As páginas têm textos em português e inglês, com o nome de cada alvo. Elas só ficam disponíveis depois que o playbook termina.

Os “servidores” são containers descartáveis. A conexão usa o plugin Docker do Ansible, sem SSH ou systemd. As tarefas alteram esses containers; não instalam Nginx no seu computador.

## Experimente

1. Rode o playbook outra vez e observe `changed=0` no recap.
2. Use `--limit blue -e lab_environment=staging` para mudar apenas um alvo.
3. Edite a configuração dentro de `blue` e rode `--check --diff` para ver o que o Ansible prevê corrigir.
4. Aplique o playbook e confira quando o handler de reload é chamado.

```bash
bash scripts/ansible.sh playbook playbooks/site.yml --check --diff
bash scripts/ansible.sh playbook playbooks/site.yml --limit blue -e lab_environment=staging
```

O [guia de uso](docs/guide.md) mostra onde ficam inventário, variáveis e templates, além de explicar os cuidados com o modo check e o cache de pacotes.

## Como conferir o projeto

O teste completo precisa de alvos novos e modifica apenas este laboratório. Se você já subiu os containers, termine seus experimentos e use `bash scripts/compose.sh down` antes de executar:

```bash
python3 tests/verify.py
```

Ele acompanha a primeira configuração, a repetição sem mudanças, uma alteração limitada a `blue`, o modo check e a correção de drift. Os alvos ficam configurados ao final para você explorar. Os [resultados registrados](docs/validation.md) dizem o que foi executado e quais são os limites do teste.

Os 16 testes passaram localmente e no GitHub Actions, incluindo repetição com `changed=0`, alteração limitada a um alvo e correção de drift.

## Quando terminar

```bash
bash scripts/compose.sh down
```

Isso remove os dois alvos e suas páginas. Não há banco nem volume persistente neste exercício. O ambiente Python, a coleção e os relatórios continuam em `.local/`, fora do Git.

O próximo passo é levar a mesma organização de inventário e roles para máquinas acessadas por SSH, com usuários e privilégios definidos para esse ambiente. Este primeiro laboratório fica só no Docker local.

[Ver os outros projetos do portfólio](https://github.com/tommmdl/devops-portfolio)
