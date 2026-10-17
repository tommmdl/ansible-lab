# What happened during testing

[Português](validation.md) · [Back to the project](../README.en.md)

All **16 checks passed locally and in [GitHub Actions](https://github.com/tommmdl/ansible-lab/actions/runs/39079954027)**. Local execution finished at 17/10/2026 20:45:37 America/Sao_Paulo. CI ran commit `a1f3b684e096c71ba6ec37932bdf82f7ac4a8ac0` and took 1 minute 47 seconds.

## Comparing the runs

The table shows CI recap `changed` counts. Complete recaps from both executions are in the evidence files.

| Stage / Run | blue | green |
| --- | --- | --- |
| Primeira configuração / First apply | 6 | 6 |
| Segunda execução / Second apply | 0 | 0 |
| Staging com limit / Limited staging | 3 | — |
| Volta ao padrão / Restore defaults | 3 | 0 |
| Check mode com drift | 2 previstas / predicted | 0 |
| Correção de drift / Repair drift | 2 | 0 |
| Execução final / Final apply | 0 | 0 |
| Variável inválida / Invalid input | 0 (rejeitada / rejected) | 0 (rejeitada / rejected) |

The first apply installed/configured the service. The second changed nothing and did not call the handler. With `--limit blue`, only that target received `staging`; green's HTTP header stayed `learning`.

The test then edited blue's `nginx.conf` outside Ansible and reloaded the service. Check mode predicted changes without repairing the environment: its header still showed `manual`. The next apply restored `learning`, reloaded Nginx and converged back to zero changes. Invalid-variable testing produced an expected failure before changing either target.

Checks also covered syntax, connectivity, both hosts' pages and Portuguese/English text. Pages were checked over HTTP without visual browser automation.

## Two things the early runs taught us

The apt cache can appear recent even after package lists were removed from an image. The role now checks that those lists exist before trusting cache age.

Another attempt used PID-file existence to decide whether Nginx was running. Configuration validation left an empty file and exposed that fragile check. The final implementation uses the `service` module with the package's SysV script for startup and reload. The [first CI run](https://github.com/tommmdl/ansible-lab/actions/runs/39079848688) records the failure before that fix.

## Where to look

- [Local recaps and checks](../evidence/local-results.json)
- [CI recaps and checks](../evidence/ci-results.json)
- [Workflow steps and metadata](../evidence/ci-run.json)
- [Local runtime versions](../evidence/runtime.json)
- [Complete test implementation](../tests/verify.py)

Ansible Core 2.20.10, community.docker 5.4.0 and Nginx 1.26.3 were used. The local controller ran Python 3.14.4; CI used the 3.13 series. Target Python was 3.13.5. Exported reports contain recaps, handler names and check results, not full facts or module payloads. Detailed logs stay under `.local/` or temporary Actions artifacts.

## What remains running

Local targets remain available at http://localhost:8003 and http://localhost:8004, both using `learning`. CI cleanup removed its targets after generating reports; the test's final-state field describes the moment before that cleanup. Other labs were not changed.

## How far this goes

These checks use local containers through a Docker connection, without SSH, systemd, TLS, Ansible Vault or production machine configuration. Repeated runs occurred within the apt cache window; refreshing metadata after one hour can count as a change. Debian packages are not snapshot-pinned. Check mode was exercised on already configured targets and is not a substitute for real execution in every situation.

Technical execution was assistant-assisted with owner authorization. The files describe these test runs, not production operations experience.
