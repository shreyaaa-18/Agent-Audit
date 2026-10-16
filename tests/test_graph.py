from core.graph import build_graph


def test_build_graph():
    trace = {
        "run_id": "test-run-001",
        "agent_name": "refund",
        "decision": "APPROVE",
        "events": [
            {
                "type": "tool_call",
                "tool": "check_order",
            },
            {
                "type": "decision",
                "decision": "APPROVE",
            },
        ],
    }

    graph = build_graph(trace)

    assert graph is not None