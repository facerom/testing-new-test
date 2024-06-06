from typing import Dict

class OrchestrationTask:
    def __init__(self, task_type: str, params: Dict):
        self.task_type = task_type
        self.params = params
