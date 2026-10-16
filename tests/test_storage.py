import pytest
from core import storage


def sample_trace():
    return {
        "run_id": "test-run-001",
        "agent_name": "refund",
        "request": "Refund request for damaged product",
        "start_time": "2026-09-18T10:00:00",
        "decision": "APPROVE",
        "events": [
            {
                "type": "tool_call",
                "tool": "check_order",
            }
        ],
    }


def test_save_and_load_run(tmp_path, monkeypatch):
    trace = sample_trace()

    monkeypatch.setattr(storage, "RUNS_DIR", str(tmp_path))

    storage.save_run(trace)

    loaded = storage.load_run(
        "refund",
        "test-run-001"
    )

    assert loaded is not None
    assert loaded["run_id"] == "test-run-001"
    assert loaded["agent_name"] == "refund"
    assert loaded["decision"] == "APPROVE"


def test_list_runs(tmp_path, monkeypatch):
    trace = sample_trace()

    monkeypatch.setattr(storage, "RUNS_DIR", str(tmp_path))

    storage.save_run(trace)

    runs = storage.list_runs("refund")

    assert len(runs) == 1
    assert runs[0]["run_id"] == "test-run-001"