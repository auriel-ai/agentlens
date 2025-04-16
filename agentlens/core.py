import json
from functools import wraps

class AgentLens:
    def __init__(self, log_file="runs.jsonl"):
        self.log_file = log_file
        self.run_id = 0

    def record(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.run_id += 1
            result = func(*args, **kwargs)
            log = {
                "id": self.run_id,
                "timestamp": str(__import__("datetime").datetime.now()),
                "input": args,
                "output": result,
                "tools": [],  # Placeholder for tool calls
                "tokens": 0   # Placeholder for token count
            }
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log) + "\n")
            return result
        return wrapper

    def replay(self, run_id=None):
        with open(self.log_file, "r") as f:
            runs = [json.loads(line) for line in f]
        run = runs[run_id - 1 if run_id else -1]  # Default to last run
        print(f"Run #{run['id']} ({run['timestamp']}):\nInput: {run['input']}\nOutput: {run['output']}")

    def cli():
        print("AgentLens CLI placeholder")