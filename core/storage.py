# core/storage.py

"""
The Storage layer.

Every agent's trace already has the same shape (via AgentTracer), so
this module just needs to write it somewhere durable and read it back.

    runs/
      refund/
        <run_id>.json
      travel/
        <run_id>.json
      loan/
        <run_id>.json
      expense/
        <run_id>.json

Each run may also contain an "audit" section once AgentAudit has
analyzed it.

The Analysis layer can use this audit status to avoid allowing
previously flagged anomalous runs to contaminate historical baselines.
"""

import json
import os


RUNS_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "runs"
)


def save_run(trace):
    """
    Persist a completed trace to runs/<agent_name>/<run_id>.json.

    Returns the path it was written to.
    """

    agent_name = trace["agent_name"]
    run_id = trace["run_id"]

    agent_dir = os.path.join(
        RUNS_DIR,
        agent_name
    )

    os.makedirs(
        agent_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        agent_dir,
        f"{run_id}.json"
    )

    with open(file_path, "w") as f:

        json.dump(
            trace,
            f,
            indent=2
        )

    return file_path


def save_audit_result(
    agent_name,
    run_id,
    analysis
):
    """
    Store the result of an AgentAudit analysis inside
    the corresponding run file.

    The original trace is preserved. An "audit" section
    is added or updated.

    Example:

        "audit": {
            "is_anomalous": true,
            "analyzed_at": "...",
            "reasons": [...]
        }
    """

    trace = load_run(
        agent_name,
        run_id
    )

    trace["audit"] = {
        "is_anomalous": analysis.get(
            "is_anomalous",
            False
        ),
        "analyzed_at": __import__(
            "datetime"
        ).datetime.now().isoformat(),
        "reasons": analysis.get(
            "reasons",
            []
        )
    }

    return save_run(
        trace
    )


def list_runs(agent_name=None):
    """
    Return metadata for stored runs, most recent first.

    If agent_name is given, only that agent's runs are returned;
    otherwise runs from every agent are included.
    """

    if not os.path.isdir(RUNS_DIR):
        return []

    agent_dirs = (
        [agent_name]
        if agent_name
        else _list_agent_dirs()
    )

    summaries = []

    for name in agent_dirs:

        agent_dir = os.path.join(
            RUNS_DIR,
            name
        )

        if not os.path.isdir(agent_dir):
            continue

        for filename in os.listdir(agent_dir):

            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(
                agent_dir,
                filename
            )

            with open(file_path, "r") as f:

                trace = json.load(f)

            summaries.append({
                "run_id": trace["run_id"],
                "agent_name": trace["agent_name"],
                "request": trace["request"],
                "start_time": trace["start_time"],
                "decision": trace.get(
                    "final_decision",
                    {}
                ).get(
                    "decision",
                    "UNKNOWN"
                ),
                "is_anomalous": trace.get(
                    "audit",
                    {}
                ).get(
                    "is_anomalous"
                ),
                "file_path": file_path,
            })

    summaries.sort(
        key=lambda r: r["start_time"],
        reverse=True
    )

    return summaries


def load_run(
    agent_name,
    run_id
):
    """
    Load and return the full trace for one stored run.
    """

    file_path = os.path.join(
        RUNS_DIR,
        agent_name,
        f"{run_id}.json"
    )

    if not os.path.isfile(file_path):

        raise FileNotFoundError(
            f"No stored run {run_id} "
            f"for agent {agent_name}."
        )

    with open(file_path, "r") as f:

        return json.load(f)


def _list_agent_dirs():

    if not os.path.isdir(RUNS_DIR):
        return []

    return [
        name
        for name in os.listdir(RUNS_DIR)
        if os.path.isdir(
            os.path.join(
                RUNS_DIR,
                name
            )
        )
    ]