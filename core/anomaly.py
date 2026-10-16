# core/anomaly.py

"""
The Analysis layer.

AgentAudit detects anomalous behavior by comparing a run with
historical behavior of the SAME agent and SAME decision.

Previously audited anomalous runs are excluded from the historical
baseline so anomalous behavior does not contaminate future analysis.

The analysis returns:
    1. A simple anomaly flag
    2. Structured evidence
    3. Typical tool usage
    4. Typical tool sequence
    5. Missing tools
    6. Unexpected tools

A rare decision by itself is NOT considered anomalous.

A sequence difference is recorded as evidence, but does not
automatically make a run anomalous.

Runs that have not yet been audited are still eligible as
historical data because AgentAudit has no evidence that they
are anomalous.
"""

from collections import Counter

from core.storage import list_runs, load_run


# Minimum historical examples required before establishing
# a decision-specific baseline.
MIN_HISTORY_FOR_BASELINE = 3


# A tool is considered typical when it appears in at least
# this fraction of historical runs with the same decision.
TYPICAL_TOOL_THRESHOLD = 0.75


def analyze_run(trace):
    """
    Compare a completed trace against historical runs for the
    same agent and same final decision.

    Previously audited anomalous runs are excluded from the
    baseline.
    """

    agent_name = trace["agent_name"]

    decision = trace.get(
        "final_decision",
        {}
    ).get(
        "decision"
    )

    # ---------------------------------------------------------
    # STEP 1: Find historical runs for this agent
    # ---------------------------------------------------------

    past_runs_meta = [
        run
        for run in list_runs(agent_name)
        if run["run_id"] != trace["run_id"]
    ]

    # ---------------------------------------------------------
    # STEP 2: Exclude previously audited anomalous runs
    # ---------------------------------------------------------

    clean_past_runs_meta = [
        run
        for run in past_runs_meta
        if run.get("is_anomalous") is not True
    ]

    if len(clean_past_runs_meta) < MIN_HISTORY_FOR_BASELINE:

        return {
            "is_anomalous": False,
            "decision": decision,
            "observed_tools": _get_called_tools(trace),
            "observed_sequence": _get_tool_sequence(trace),
            "typical_tools": [],
            "typical_sequence": [],
            "missing_tools": [],
            "unexpected_tools": [],
            "tool_frequencies": {},
            "reasons": [],
            "note": (
                f"Only {len(clean_past_runs_meta)} clean historical "
                f"run(s) for {agent_name} — need at least "
                f"{MIN_HISTORY_FOR_BASELINE} to establish a baseline."
            ),
        }

    # ---------------------------------------------------------
    # STEP 3: Load complete historical traces
    # ---------------------------------------------------------

    past_traces = [
        load_run(
            agent_name,
            run["run_id"]
        )
        for run in clean_past_runs_meta
    ]

    # ---------------------------------------------------------
    # STEP 4: Keep only runs with the same decision
    # ---------------------------------------------------------

    same_decision_runs = [
        run
        for run in past_traces
        if run.get(
            "final_decision",
            {}
        ).get(
            "decision"
        ) == decision
    ]

    if len(same_decision_runs) < MIN_HISTORY_FOR_BASELINE:

        return {
            "is_anomalous": False,
            "decision": decision,
            "observed_tools": _get_called_tools(trace),
            "observed_sequence": _get_tool_sequence(trace),
            "typical_tools": [],
            "typical_sequence": [],
            "missing_tools": [],
            "unexpected_tools": [],
            "tool_frequencies": {},
            "reasons": [],
            "note": (
                f"Compared against {len(past_traces)} clean historical "
                f"{agent_name} run(s), but only "
                f"{len(same_decision_runs)} had decision "
                f"'{decision}'. Need at least "
                f"{MIN_HISTORY_FOR_BASELINE} examples of this "
                f"decision for a decision-specific baseline."
            ),
        }

    # ---------------------------------------------------------
    # STEP 5: Determine typical tools
    # ---------------------------------------------------------

    typical_tools = _typical_tools(
        same_decision_runs
    )

    tool_frequencies = {
        tool: _tool_frequency(
            tool,
            same_decision_runs
        )
        for tool in sorted(typical_tools)
    }

    # ---------------------------------------------------------
    # STEP 6: Determine current run's behavior
    # ---------------------------------------------------------

    observed_tools = _get_called_tools(trace)

    observed_sequence = _get_tool_sequence(
        trace
    )

    # ---------------------------------------------------------
    # STEP 7: Determine typical sequence
    # ---------------------------------------------------------

    typical_sequence = _typical_sequence(
        same_decision_runs
    )

    # ---------------------------------------------------------
    # STEP 8: Identify missing and unexpected tools
    # ---------------------------------------------------------

    missing_tools = sorted(
        typical_tools - observed_tools
    )

    unexpected_tools = sorted(
        observed_tools - typical_tools
    )

    reasons = []

    # ---------------------------------------------------------
    # Missing typical tools
    # ---------------------------------------------------------

    for tool in missing_tools:

        frequency = tool_frequencies[tool]

        reasons.append(
            f"This run did not call {tool}, which appears in "
            f"{frequency:.0%} of historical {agent_name} runs "
            f"that resulted in '{decision}'."
        )

    # ---------------------------------------------------------
    # Unexpected tools
    # ---------------------------------------------------------

    for tool in unexpected_tools:

        reasons.append(
            f"This run called {tool}, which is not typical of "
            f"historical {agent_name} runs that resulted in "
            f"'{decision}'."
        )

    # ---------------------------------------------------------
    # STEP 9: Return structured analysis
    # ---------------------------------------------------------

    return {
        "is_anomalous": len(reasons) > 0,

        "decision": decision,

        "observed_tools": sorted(
            observed_tools
        ),

        "observed_sequence": observed_sequence,

        "typical_tools": sorted(
            typical_tools
        ),

        "typical_sequence": typical_sequence,

        "missing_tools": missing_tools,

        "unexpected_tools": unexpected_tools,

        "tool_frequencies": tool_frequencies,

        "reasons": reasons,

        "note": (
            f"Compared against {len(same_decision_runs)} "
            f"clean historical {agent_name} run(s) with decision "
            f"'{decision}'. Previously audited anomalous runs "
            f"were excluded from the baseline."
        ),
    }


def _get_called_tools(trace):
    """
    Return the unique tools called during a run.
    """

    return {
        event["tool_name"]
        for event in trace.get("events", [])
        if event.get("event_type") == "tool_call"
    }


def _get_tool_sequence(trace):
    """
    Return tools in the exact order they were called.
    """

    return [
        event["tool_name"]
        for event in trace.get("events", [])
        if event.get("event_type") == "tool_call"
    ]


def _typical_tools(past_traces):
    """
    Return tools that appear in at least
    TYPICAL_TOOL_THRESHOLD fraction of the supplied runs.
    """

    tool_presence = Counter()

    for trace in past_traces:

        tools_in_run = _get_called_tools(
            trace
        )

        for tool in tools_in_run:
            tool_presence[tool] += 1

    total = len(past_traces)

    if total == 0:
        return set()

    return {
        tool
        for tool, count in tool_presence.items()
        if count / total >= TYPICAL_TOOL_THRESHOLD
    }


def _typical_sequence(past_traces):
    """
    Determine the most common tool sequence among historical runs.

    The sequence is based on the exact order of tool calls.

    Example:

        check_order → check_refund_policy
    """

    if not past_traces:
        return []

    sequences = []

    for trace in past_traces:

        sequence = tuple(
            _get_tool_sequence(trace)
        )

        sequences.append(
            sequence
        )

    sequence_counts = Counter(
        sequences
    )

    most_common_sequence, _ = sequence_counts.most_common(
        1
    )[0]

    return list(
        most_common_sequence
    )


def _tool_frequency(tool, past_traces):
    """
    Calculate how frequently a tool appears across
    the supplied historical traces.
    """

    if not past_traces:
        return 0

    count = 0

    for trace in past_traces:

        tools_in_run = _get_called_tools(
            trace
        )

        if tool in tools_in_run:
            count += 1

    return count / len(past_traces)