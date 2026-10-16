# scripts/visualize_graph.py

"""
Graphviz visualization for AgentAudit decision traces.

Loads a stored AgentAudit trace, converts it into the explicit
graph representation from core.graph, and renders the graph
as PNG and SVG files.
"""

import os
import subprocess
import html

from core.graph import build_graph
from core.storage import list_runs, load_run


OUTPUT_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "graphs"
)


def format_request(request):
    """
    Convert a request into readable key/value rows.
    """

    if isinstance(request, dict):

        return [
            (
                str(key),
                str(value)
            )
            for key, value in request.items()
        ]

    return [
        ("Request", str(request))
    ]


def escape_html(text):
    """
    Escape text for Graphviz HTML labels.
    """

    return html.escape(
        str(text)
    )


def html_table(rows, title):
    """
    Build a clean Graphviz HTML table.
    """

    cells = []

    cells.append(
        f"""
        <TR>
            <TD BGCOLOR="#E8E8E8">
                <B>{escape_html(title)}</B>
            </TD>
        </TR>
        """
    )

    for key, value in rows:

        cells.append(
            f"""
            <TR>
                <TD ALIGN="LEFT">
                    <B>{escape_html(key)}</B>
                    : {escape_html(value)}
                </TD>
            </TR>
            """
        )

    return (
        "<<TABLE BORDER=\"1\" "
        "CELLBORDER=\"0\" "
        "CELLSPACING=\"0\" "
        "CELLPADDING=\"8\">"
        + "".join(cells)
        + "</TABLE>>"
    )


def build_dot(graph):
    """
    Convert an AgentAudit graph into Graphviz DOT format.
    """

    lines = []

    lines.append(
        "digraph AgentAudit {"
    )

    lines.append(
        "    rankdir=TB;"
    )

    lines.append(
        '    graph [pad="0.5", nodesep="0.6", ranksep="0.8"];'
    )

    lines.append(
        '    node [shape=plain, fontname="Arial"];'
    )

    lines.append(
        '    edge [fontname="Arial", arrowsize="0.8"];'
    )

    # =========================================================
    # NODES
    # =========================================================

    for node in graph["nodes"]:

        node_id = node["id"]
        node_type = node["type"]
        label = node["label"]

        data = node.get(
            "data",
            {}
        )

        # -----------------------------------------------------
        # REQUEST
        # -----------------------------------------------------

        if node_type == "request":

            request_rows = format_request(
                data.get(
                    "request",
                    ""
                )
            )

            node_label = html_table(
                request_rows,
                "REQUEST"
            )

        # -----------------------------------------------------
        # LLM
        # -----------------------------------------------------

        elif node_type == "llm":

            model = data.get(
                "model",
                ""
            )

            tools = data.get(
                "tools_requested",
                []
            )

            tools_text = ", ".join(
                str(tool)
                for tool in tools
            )

            rows = [
                (
                    "Model",
                    model
                ),
                (
                    "Tools",
                    tools_text
                )
            ]

            node_label = html_table(
                rows,
                "LLM"
            )

        # -----------------------------------------------------
        # TOOL
        # -----------------------------------------------------

        elif node_type == "tool":

            tool_name = data.get(
                "tool_name",
                label
            )

            rows = [
                (
                    "Tool",
                    tool_name
                )
            ]

            node_label = html_table(
                rows,
                "TOOL"
            )

        # -----------------------------------------------------
        # DECISION
        # -----------------------------------------------------

        elif node_type == "decision":

            decision = data.get(
                "decision",
                "UNKNOWN"
            )

            reason = data.get(
                "reason",
                ""
            )

            rows = [
                (
                    "Decision",
                    decision
                ),
                (
                    "Reason",
                    reason
                )
            ]

            node_label = html_table(
                rows,
                "FINAL DECISION"
            )

        # -----------------------------------------------------
        # OTHER
        # -----------------------------------------------------

        else:

            rows = [
                (
                    "Type",
                    node_type
                ),
                (
                    "Label",
                    label
                )
            ]

            node_label = html_table(
                rows,
                "EVENT"
            )

        lines.append(
            f'    "{node_id}" [label={node_label}];'
        )

    # =========================================================
    # EDGES
    # =========================================================

    for edge in graph["edges"]:

        source = edge["source"]
        target = edge["target"]

        lines.append(
            f'    "{source}" -> "{target}";'
        )

    lines.append(
        "}"
    )

    return "\n".join(
        lines
    )


def render_graph(graph):
    """
    Render the graph into PNG and SVG files.
    """

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    agent_name = graph.get(
        "agent_name",
        "agent"
    )

    run_id = graph.get(
        "run_id",
        "unknown"
    )

    dot_file = os.path.join(
        OUTPUT_DIR,
        f"{agent_name}_{run_id}.dot"
    )

    png_file = os.path.join(
        OUTPUT_DIR,
        f"{agent_name}_{run_id}.png"
    )

    svg_file = os.path.join(
        OUTPUT_DIR,
        f"{agent_name}_{run_id}.svg"
    )

    dot_content = build_dot(
        graph
    )

    with open(
        dot_file,
        "w"
    ) as f:

        f.write(
            dot_content
        )

    subprocess.run(
        [
            "dot",
            "-Tpng",
            dot_file,
            "-o",
            png_file
        ],
        check=True
    )

    subprocess.run(
        [
            "dot",
            "-Tsvg",
            dot_file,
            "-o",
            svg_file
        ],
        check=True
    )

    return {
        "dot": dot_file,
        "png": png_file,
        "svg": svg_file
    }


def choose_run():
    """
    Let the user choose an agent and stored run.
    """

    agents = [
        "refund",
        "travel",
        "loan",
        "expense"
    ]

    print()
    print("=" * 70)
    print("AGENTAUDIT GRAPHVIZ VISUALIZATION")
    print("=" * 70)

    print()
    print("Available Agents:")
    print()

    for index, agent in enumerate(
        agents,
        start=1
    ):

        print(
            f"{index}. {agent}"
        )

    print()

    while True:

        choice = input(
            "Select an agent (number): "
        ).strip()

        if choice.isdigit():

            number = int(
                choice
            )

            if 1 <= number <= len(agents):
                break

        print(
            "Invalid selection."
        )

    agent_name = agents[
        number - 1
    ]

    runs = list_runs(
        agent_name
    )

    if not runs:

        print()
        print(
            f"No stored runs found for {agent_name}."
        )

        return None

    print()
    print(
        f"Stored {agent_name} runs:"
    )
    print()

    for index, run in enumerate(
        runs,
        start=1
    ):

        print(
            f"{index}. "
            f"{run['run_id']} | "
            f"Decision: {run['decision']}"
        )

    print()

    while True:

        choice = input(
            "Select a run (number): "
        ).strip()

        if choice.isdigit():

            number = int(
                choice
            )

            if 1 <= number <= len(runs):
                break

        print(
            "Invalid selection."
        )

    selected_run = runs[
        number - 1
    ]

    return (
        agent_name,
        selected_run["run_id"]
    )


def main():

    selected = choose_run()

    if selected is None:
        return

    agent_name, run_id = selected

    trace = load_run(
        agent_name,
        run_id
    )

    graph = build_graph(
        trace
    )

    files = render_graph(
        graph
    )

    print()
    print("=" * 70)
    print("GRAPHVIZ RENDERING COMPLETE")
    print("=" * 70)

    print()
    print("Agent:")
    print(agent_name)

    print()
    print("Run ID:")
    print(run_id)

    print()
    print("PNG:")
    print(files["png"])

    print()
    print("SVG:")
    print(files["svg"])

    print()
    print("DOT:")
    print(files["dot"])

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()