# core/graph.py

"""
Graph representation for AgentAudit traces.

The tracer stores an agent execution as an ordered list of events.
This module converts that trace into an explicit decision graph.

The original trace is never modified.

Graph structure:

    Request
       ↓
    LLM / Tool
       ↓
    LLM / Tool
       ↓
    Final Decision

The graph contains both:
    1. Execution structure
    2. Run-level metadata

This allows a future UI to consume a single graph object without
having to separately understand the raw trace.
"""


def build_graph(trace):
    """
    Convert an AgentAudit trace into an explicit graph.

    Parameters
    ----------
    trace : dict
        A completed AgentAudit trace.

    Returns
    -------
    dict
        Graph containing run metadata, nodes and edges.
    """

    nodes = []
    edges = []

    # =========================================================
    # REQUEST
    # =========================================================

    request = trace.get(
        "request",
        ""
    )

    request_node = {
        "id": "request",
        "type": "request",
        "label": "Request",
        "data": {
            "request": request
        }
    }

    nodes.append(request_node)

    previous_node_id = "request"

    # =========================================================
    # EVENTS
    # =========================================================

    events = trace.get(
        "events",
        []
    )

    for index, event in enumerate(events, start=1):

        event_type = event.get(
            "event_type"
        )

        # -----------------------------------------------------
        # LLM CALL
        # -----------------------------------------------------

        if event_type == "llm_call":

            node_id = f"llm_{index}"

            node = {
                "id": node_id,
                "type": "llm",
                "label": "LLM",
                "data": {
                    "step": index,
                    "model": event.get(
                        "model"
                    ),
                    "content": event.get(
                        "content",
                        ""
                    ),
                    "tools_requested": event.get(
                        "tool_calls_requested",
                        []
                    ),
                    "duration_seconds": event.get(
                        "duration_seconds"
                    )
                }
            }

        # -----------------------------------------------------
        # TOOL CALL
        # -----------------------------------------------------

        elif event_type == "tool_call":

            tool_name = event.get(
                "tool_name",
                "Unknown Tool"
            )

            node_id = f"tool_{index}"

            node = {
                "id": node_id,
                "type": "tool",
                "label": tool_name,
                "data": {
                    "step": index,
                    "tool_name": tool_name,
                    "input": event.get(
                        "input",
                        {}
                    ),
                    "output": event.get(
                        "output",
                        {}
                    ),
                    "duration_seconds": event.get(
                        "duration_seconds"
                    )
                }
            }

        # -----------------------------------------------------
        # UNKNOWN EVENT
        # -----------------------------------------------------

        else:

            node_id = f"event_{index}"

            node = {
                "id": node_id,
                "type": "event",
                "label": event_type or "Unknown Event",
                "data": {
                    "step": index,
                    "event": event
                }
            }

        nodes.append(node)

        # -----------------------------------------------------
        # EDGE
        # -----------------------------------------------------

        edges.append({
            "id": f"edge_{index}",
            "source": previous_node_id,
            "target": node_id
        })

        previous_node_id = node_id

    # =========================================================
    # FINAL DECISION
    # =========================================================

    final_decision = trace.get(
        "final_decision",
        {}
    )

    decision = final_decision.get(
        "decision",
        "UNKNOWN"
    )

    decision_node = {
        "id": "decision",
        "type": "decision",
        "label": f"Decision: {decision}",
        "data": {
            "decision": decision,
            "reason": final_decision.get(
                "reason",
                ""
            ),
            "timestamp": final_decision.get(
                "timestamp"
            )
        }
    }

    nodes.append(decision_node)

    edges.append({
        "id": "edge_decision",
        "source": previous_node_id,
        "target": "decision"
    })

    # =========================================================
    # GRAPH
    # =========================================================

    return {
        "run_id": trace.get(
            "run_id"
        ),
        "agent_name": trace.get(
            "agent_name"
        ),
        "request": request,
        "final_decision": {
            "decision": decision,
            "reason": final_decision.get(
                "reason",
                ""
            ),
            "timestamp": final_decision.get(
                "timestamp"
            )
        },
        "nodes": nodes,
        "edges": edges
    }


def print_graph(graph):
    """
    Print the graph structure in a readable format.
    """

    print()
    print("=" * 70)
    print("AGENTAUDIT DECISION GRAPH")
    print("=" * 70)

    print()
    print("Run ID:")
    print(graph.get("run_id"))

    print()
    print("Agent:")
    print(graph.get("agent_name"))

    print()
    print("Decision:")
    print(
        graph.get(
            "final_decision",
            {}
        ).get(
            "decision",
            "UNKNOWN"
        )
    )

    print()
    print("NODES")
    print("-" * 70)

    for node in graph["nodes"]:

        print(
            f"{node['id']:<12} | "
            f"{node['type']:<10} | "
            f"{node['label']}"
        )

    print()
    print("EDGES")
    print("-" * 70)

    for edge in graph["edges"]:

        print(
            f"{edge['source']} "
            f"→ "
            f"{edge['target']}"
        )

    print()
    print("=" * 70)


def print_graph_details(graph):
    """
    Print the complete information contained in every node.
    """

    print()
    print("=" * 70)
    print("AGENTAUDIT GRAPH DETAILS")
    print("=" * 70)

    print()
    print("RUN")
    print("-" * 70)
    print("Run ID:", graph.get("run_id"))
    print("Agent:", graph.get("agent_name"))
    print("Decision:", graph.get("final_decision", {}).get("decision"))

    print()
    print("REQUEST")
    print("-" * 70)
    print(graph.get("request", ""))

    for node in graph["nodes"]:

        print()
        print(f"[{node['label']}]")
        print("-" * 70)

        data = node.get(
            "data",
            {}
        )

        for key, value in data.items():

            print(
                f"{key}: {value}"
            )

    print()
    print("=" * 70)