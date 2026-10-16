from core.explain import explain_run


def test_explain_run_returns_text():
    trace = {
        "run_id": "test-run-001",
        "agent_name": "refund",
        "final_decision": {
            "decision": "APPROVE",
            "reason": "Order is eligible for refund",
        },
        "events": [
            {
                "type": "tool_call",
                "tool": "check_order",
            },
        ],
    }

    analysis = {
        "is_anomalous": False,
        "reasons": [],
    }

    result = explain_run(trace, analysis)

    assert result is not None
    assert isinstance(result, str)