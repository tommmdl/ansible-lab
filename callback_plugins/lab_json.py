"""Write task names and recap counts for this lab, without module payloads."""
import json
import os
from pathlib import Path
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'lab_json'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super().__init__()
        self.handlers = []

    def v2_playbook_on_handler_task_start(self, task):
        self.handlers.append(task.get_name())

    def v2_playbook_on_stats(self, stats):
        output = os.environ.get('LAB_RUN_REPORT')
        if output:
            data = {'hosts': {host: stats.summarize(host) for host in sorted(stats.processed)},
                    'handlers': self.handlers}
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + '\n')
