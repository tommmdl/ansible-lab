# O que aconteceu nos testes

[English](validation.en.md) · [Voltar ao projeto](../README.md)

Os **16 testes passaram localmente e no [GitHub Actions](https://github.com/tommmdl/ansible-lab/actions/runs/39079954027)**. A execução local terminou em 17/10/2026 20:45:37, no fuso America/Sao_Paulo. O CI executou o commit `a1f3b684e096c71ba6ec37932bdf82f7ac4a8ac0` e levou 1 minuto e 47 segundos.

## Comparando as execuções

A tabela mostra o campo `changed` do recap no CI. Os recaps completos das duas execuções estão nos arquivos de evidência.

| Etapa / Run | blue | green |
| --- | --- | --- |
| Primeira configuração / First apply | 6 | 6 |
| Segunda execução / Second apply | 0 | 0 |
| Staging com limit / Limited staging | 3 | — |
| Volta ao padrão / Restore defaults | 3 | 0 |
| Check mode com drift | 2 previstas / predicted | 0 |
| Correção de drift / Repair drift | 2 | 0 |
| Execução final / Final apply | 0 | 0 |
| Variável inválida / Invalid input | 0 (rejeitada / rejected) | 0 (rejeitada / rejected) |

A primeira execução instalou e configurou o serviço. A segunda não mudou nada e não chamou o handler. Ao usar `--limit blue`, apenas esse alvo recebeu o ambiente `staging`; o header HTTP de `green` continuou em `learning`.

Depois, o teste alterou manualmente `nginx.conf` em blue e recarregou o serviço. O modo check indicou as mudanças previstas sem corrigir o ambiente: o header ainda mostrava `manual`. O apply seguinte restaurou `learning`, recarregou Nginx e voltou a convergir para zero mudanças. O teste de variável inválida terminou com falha esperada, antes de alterar os alvos.

As verificações também confirmaram sintaxe, conectividade, páginas dos dois hosts e textos em português e inglês. As páginas foram verificadas por HTTP, sem automação visual de navegador.

## Duas coisas que os primeiros testes ensinaram

O cache apt pode parecer recente mesmo com as listas removidas na imagem. O role passou a procurar essas listas antes de usar o prazo do cache.

Outra tentativa usava a existência do PID file para decidir se Nginx já estava iniciado. A validação da configuração deixou esse arquivo vazio e expôs a fragilidade da checagem. A implementação final usa o módulo `service` com o script SysV do pacote, tanto para iniciar quanto para recarregar. A [primeira execução do CI](https://github.com/tommmdl/ansible-lab/actions/runs/39079848688) registrou a falha anterior à correção.

## Onde olhar

- [Recaps e checks locais](../evidence/local-results.json)
- [Recaps e checks no CI](../evidence/ci-results.json)
- [Etapas e metadados do workflow](../evidence/ci-run.json)
- [Versões do ambiente local](../evidence/runtime.json)
- [Teste completo](../tests/verify.py)

Foram usados Ansible Core 2.20.10, coleção community.docker 5.4.0 e Nginx 1.26.3. O controlador local usou Python 3.14.4; o CI, a série 3.13. Python remoto: 3.13.5. Os relatórios exportam recaps, nomes de handlers e resultados dos checks, sem facts completos ou dados de módulos. Logs detalhados ficam em `.local/` ou nos artefatos temporários do Actions.

## O que ficou rodando

Os alvos locais continuam disponíveis em http://localhost:8003 e http://localhost:8004, ambos em `learning`. No CI, a etapa de cleanup removeu os alvos depois de gerar os relatórios; o campo de estado final do teste descreve o momento anterior a essa limpeza. Os outros laboratórios não foram alterados.

## Até onde isso vai

Este teste cobre containers locais por conexão Docker, sem SSH, systemd, TLS, Ansible Vault ou configuração de máquinas de produção. As repetições ocorreram dentro do prazo do cache apt; atualizar metadados depois de uma hora pode contar como mudança. Pacotes Debian não estão fixados por snapshot. Check mode foi testado em alvos já configurados e não substitui uma execução real em qualquer cenário.

A execução técnica foi feita com ajuda do assistente e autorização do proprietário. Os arquivos registram o que aconteceu nesses testes, sem representar experiência de operação em produção.
