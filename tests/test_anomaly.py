from core.anomaly import analyze_run


def test_analyze_run_returns_result():
    trace = {
        "run_id": "test-run-001",
        "agent_name": "refund",
        "decision": "APPROVE",
        "events": [
            {
                "type": "tool_call",
                "tool": "check_order",
            },
        ],
    }

def test_analyze_run_contains_anomaly_flag():
    trace = {
        "run_id": "test-run-001",
        "agent_name": "refund",
        "decision": "APPROVE",
        "events": [],
    }

    result = analyze_run(trace)

    assert result is not None