# tracer.py

import time
import uuid
from datetime import datetime


class AgentTracer:

    def __init__(self):
        self.current_run = None

    def start_run(self, agent_name, request):
        """
        Start a new agent run.
        """

        self.current_run = {
            "run_id": str(uuid.uuid4()),
            "agent_name": agent_name,
            "request": request,
            "start_time": datetime.now().isoformat(),
            "events": []
        }

        return self.current_run["run_id"]

    def log_tool_call(
        self,
        tool_name,
        input_data,
        output_data,
        duration
    ):
        """
        Record an observable tool execution.
        """

        if self.current_run is None:
            raise RuntimeError(
                "No active run. Call start_run() first."
            )

        event = {
            "event_type": "tool_call",
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "input": input_data,
            "output": output_data,
            "duration_seconds": round(duration, 4)
        }

        self.current_run["events"].append(event)

    def log_llm_call(
        self,
        model,
        content,
        tool_calls_requested,
        duration
    ):
        """
        Record one call to the underlying LLM: its own message content
        (reasoning/final text) and which tools it chose to call next,
        if any. This captures the agent's intermediate reasoning, not
        just the tool inputs/outputs — needed so the Explanation layer
        can reference what the model itself said, not only what tools
        returned.
        """

        if self.current_run is None:
            raise RuntimeError(
                "No active run. Call start_run() first."
            )

        event = {
            "event_type": "llm_call",
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "content": content,
            "tool_calls_requested": tool_calls_requested,
            "duration_seconds": round(duration, 4)
        }

        self.current_run["events"].append(event)

    def log_decision(self, decision, reason):
        """
        Record the final agent decision.
        """

        if self.current_run is None:
            raise RuntimeError(
                "No active run. Call start_run() first."
            )

        self.current_run["final_decision"] = {
            "decision": decision,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }

    def end_run(self):
        """
        Finish the current run.
        """

        if self.current_run is None:
            return None

        self.current_run["end_time"] = datetime.now().isoformat()

        completed_run = self.current_run

        self.current_run = None

        return completed_run