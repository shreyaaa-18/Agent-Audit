# core/simulator.py

import time

from core.tracer import AgentTracer
from core.storage import save_run


class AgentSimulator:
    """
    Generates deterministic agent traces without making external LLM calls.

    A scenario is defined compactly using:
        - request
        - expected_tools
        - steps
        - decision
        - reason

    The simulator converts those definitions into the same trace structure
    produced by real agents.
    """

    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.tracer = AgentTracer()

    def run(self, scenario):
        """
        Run one simulated scenario.

        Parameters
        ----------
        scenario : dict
            Compact scenario definition.
        """

        required_fields = [
            "request",
            "steps",
            "decision",
            "reason"
        ]

        for field in required_fields:
            if field not in scenario:
                raise ValueError(
                    f"Scenario is missing required field: '{field}'"
                )

        print("\n================================")
        print("STARTING SIMULATED AGENTAUDIT RUN")
        print("================================")

        if scenario.get("name"):
            print("Scenario:", scenario["name"])

        run_id = self.tracer.start_run(
            self.agent_name,
            scenario["request"]
        )

        # Store the expected workflow alongside the observed trace.
        # expected_tools is optional in the scenario definition — when
        # not given explicitly, derive it from the tool-type steps
        # already present, so scenario authors don't have to keep two
        # lists in sync by hand.
        self.tracer.current_run["expected_tools"] = scenario.get(
            "expected_tools",
            [s["name"] for s in scenario["steps"] if s.get("type") == "tool"]
        )

        print("Run ID:", run_id)

        for step in scenario["steps"]:
            self._execute_step(step)

        self.tracer.log_decision(
            scenario["decision"],
            scenario["reason"]
        )

        completed_run = self.tracer.end_run()

        file_path = save_run(completed_run)

        print("\nDecision:", scenario["decision"])
        print("Trace saved:", file_path)

        return completed_run

    def _execute_step(self, step):
        """
        Convert one compact scenario step into a tracer event.
        """

        step_type = step.get("type")

        if step_type == "llm":
            self._simulate_llm_call(step)

        elif step_type == "tool":
            self._simulate_tool_call(step)

        else:
            raise ValueError(
                f"Unknown scenario step type: {step_type}"
            )

    def _simulate_llm_call(self, step):
        """
        Simulate an LLM call.
        """

        start_time = time.time()

        time.sleep(0.01)

        duration = time.time() - start_time

        self.tracer.log_llm_call(
            model=step.get(
                "model",
                "simulated-agent-model"
            ),
            content=step.get(
                "content",
                ""
            ),
            tool_calls_requested=step.get(
                "tools",
                []
            ),
            duration=duration
        )

    def _simulate_tool_call(self, step):
        """
        Simulate a tool execution.
        """

        if "name" not in step:
            raise ValueError(
                "Tool step is missing 'name'."
            )

        start_time = time.time()

        time.sleep(0.01)

        duration = time.time() - start_time

        self.tracer.log_tool_call(
            tool_name=step["name"],
            input_data=step.get(
                "input",
                {}
            ),
            output_data=step.get(
                "output",
                {}
            ),
            duration=duration
        )