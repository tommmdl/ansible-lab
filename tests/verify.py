#!/usr/bin/env python3
"""Exercise the dedicated blue/green lab; leave configured targets running."""
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / '.local'
checks = []
runs = {}


def run(args, label, expected=0, extra_env=None):
    env = os.environ.copy()
    env.update(extra_env or {})
    result = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
    (LOCAL / (label + '.log')).write_text(result.stdout + result.stderr)
    if result.returncode != expected:
        raise RuntimeError(label + ': ' + (result.stdout + result.stderr)[-4000:])
    return result


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
    print('PASS: ' + name, flush=True)


def play(label, *args, expected=0):
    report = LOCAL / (label + '.json')
    run(['bash', 'scripts/ansible.sh', 'playbook', 'playbooks/site.yml', *args], label,
        expected=expected, extra_env={'LAB_RUN_REPORT': str(report)})
    result = json.loads(report.read_text())
    runs[label] = result
    return result


def page(port):
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=5) as response:
        return response.status, response.headers.get('X-Lab-Environment'), response.read().decode()


def wait_header(port, value):
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            result = page(port)
            if result[1] == value:
                return result
        except OSError:
            pass
        time.sleep(.5)
    raise RuntimeError('Header timeout: ' + str(port) + ' ' + value)


LOCAL.mkdir(exist_ok=True)
for target in ['ansible-lab-blue', 'ansible-lab-green']:
    exists = subprocess.run(['docker', 'container', 'inspect', target], capture_output=True)
    if exists.returncode == 0:
        raise SystemExit('Fresh targets required. Review and remove only this lab with compose down first.')
run(['bash', 'scripts/compose.sh', 'up', '-d', '--build'], 'bootstrap')
run(['bash', 'scripts/ansible.sh', 'playbook', 'playbooks/site.yml', '--syntax-check'], 'syntax')
check('Playbook syntax valid', True)
run(['bash', 'scripts/ansible.sh', 'web', '-m', 'ansible.builtin.ping'], 'ping')
check('Both inventory targets reachable through Docker connection', True)
first = play('first-apply')
check('First apply changes both targets', set(first['hosts']) == {'blue', 'green'} and all(h['changed'] > 0 for h in first['hosts'].values()))
blue = wait_header(8003, 'learning')
green = wait_header(8004, 'learning')
check('Both pages served with distinct host variables', 'BLUE' in blue[2] and 'GREEN' in green[2])
check('Pages include Portuguese and English text', all('Esta página' in p[2] and 'This page' in p[2] for p in [blue, green]))
second = play('second-apply')
check('Second apply reports changed=0 on both hosts', all(h['changed'] == 0 for h in second['hosts'].values()))
check('Unchanged configuration does not call reload handler', not second['handlers'])
changed = play('limited-staging', '--limit', 'blue', '-e', 'lab_environment=staging')
check('Limit changes blue only and runs reload handler', set(changed['hosts']) == {'blue'} and changed['hosts']['blue']['changed'] > 0 and bool(changed['handlers']))
wait_header(8003, 'staging')
check('Green remains learning while blue becomes staging', page(8004)[1] == 'learning')
play('restore-defaults')
wait_header(8003, 'learning')
check('Default variables restore learning environment', True)
# Deliberate drift only in this disposable target, not on the host machine.
run(['docker', 'exec', 'ansible-lab-blue', 'python', '-c',
     'from pathlib import Path; p=Path("/etc/nginx/nginx.conf"); p.write_text(p.read_text().replace(\'X-Lab-Environment "learning"\', \'X-Lab-Environment "manual"\'))'], 'inject-drift')
run(['docker', 'exec', 'ansible-lab-blue', 'nginx', '-s', 'reload'], 'reload-drift')
wait_header(8003, 'manual')
predicted = play('check-diff', '--check', '--diff')
check('Check mode predicts blue drift while green stays unchanged', predicted['hosts']['blue']['changed'] > 0 and predicted['hosts']['green']['changed'] == 0)
check('Check mode does not repair the live manual change', page(8003)[1] == 'manual')
repair = play('repair-drift')
wait_header(8003, 'learning')
check('Apply repairs drift and reloads Nginx', repair['hosts']['blue']['changed'] > 0 and bool(repair['handlers']))
final = play('final-apply')
check('After repair both hosts converge to changed=0', all(h['changed'] == 0 for h in final['hosts'].values()))
invalid = play('invalid-environment', '-e', 'lab_environment=production', expected=2)
check('Invalid variables fail before changing targets', all(h['failures'] == 1 and h['changed'] == 0 for h in invalid['hosts'].values()))
check('Invalid run leaves both HTTP environments unchanged', page(8003)[1] == page(8004)[1] == 'learning')
result = {'executed_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
          'checks_passed': len(checks), 'checks': checks, 'runs': runs,
          'targets': {'blue': 'http://127.0.0.1:8003', 'green': 'http://127.0.0.1:8004'},
          'final_state': 'Both configured targets running; environment learning'}
(LOCAL / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2), flush=True)
