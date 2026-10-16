# server.py

"""
FastAPI backend for the AgentAudit dashboard.

This is a thin read/API layer over the existing core/ modules —
no business logic lives here. It reuses core.storage, core.anomaly,
core.explain, core.graph, and core.agent_registry exactly as they are.

NOTE ON A REAL GAP THIS FIXES: main.py analyzes each run
(analyze_run) and prints the result, but never calls
save_audit_result() — so the "audit" section (is_anomalous, reasons)
was never actually being persisted to the run's JSON file. This
backend backfills that on read (see ensure_all_audited), so the
dashboard's anomaly counts are correct even for runs generated before
this fix existed. It only computes a run's audit once and caches it
on disk — see the module docstring note below on what that trades off.
"""

import os
from collections import Counter
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from core.agent_registry import list_agents
from core.storage import list_runs, load_run, save_audit_result
from core.anomaly import analyze_run
from core.explain import explain_run
from core.graph import build_graph

app = FastAPI(title="AgentAudit API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ---------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------

def prettify_agent_name(raw_name):
    base = raw_name.replace("_agent", "").replace("_", " ").strip()
    return f"{base.title()} Agent" if base else raw_name


def relative_time(iso_timestamp):
    try:
        then = datetime.fromisoformat(iso_timestamp)
    except (ValueError, TypeError):
        return iso_timestamp
    seconds = (datetime.now() - then).total_seconds()
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        return f"{int(seconds // 60)} mins ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    return f"{int(seconds // 86400)} days ago"


def run_duration_seconds(trace):
    try:
        start = datetime.fromisoformat(trace["start_time"])
        end = datetime.fromisoformat(trace["end_time"])
        return (end - start).total_seconds()
    except Exception:
        return sum(e.get("duration_seconds", 0) or 0 for e in trace.get("events", []))


def request_display(request_value):
    """
    Simulator-generated runs (core/simulator.py + core/scenarios.py)
    store `request` as a structured dict; real-agent runs store it as
    a plain natural-language string. The frontend only ever wants a
    displayable/searchable string, so normalize both shapes here once
    instead of type-checking it on every page.
    """
    import json as _json
    if isinstance(request_value, str):
        return request_value
    return _json.dumps(request_value)


def ensure_all_audited():
    """
    Backfill an "audit" section for any stored run that doesn't have
    one yet (see the module docstring for why this is needed). Once a
    run has an audit section it's not recomputed automatically — a new
    run added later could technically shift what "typical" looks like
    for older runs, but re-scanning everything on every request doesn't
    scale, so this trades a small amount of staleness for real
    performance at larger run counts (worth revisiting if/when the
    project's NFR load testing covers this specifically).
    """
    for r in list_runs():
        trace = load_run(r["agent_name"], r["run_id"])
        if "audit" not in trace:
            analysis = analyze_run(trace)
            save_audit_result(r["agent_name"], r["run_id"], analysis)


def status_label(run_meta):
    if run_meta.get("is_anomalous"):
        return "Flagged"
    decision = run_meta["decision"]
    if decision == "REJECT":
        return "Rejected"
    if decision == "ESCALATE":
        return "Escalated"
    return "Completed"


def risk_label(run_meta):
    if run_meta.get("is_anomalous"):
        return "High"
    if run_meta["decision"] in ("REJECT", "ESCALATE"):
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------

@app.get("/api/fleet-stats")
def fleet_stats():
    ensure_all_audited()
    all_runs = list_runs()
    total = len(all_runs)
    decision_counts = Counter(r["decision"] for r in all_runs)
    approved = decision_counts.get("APPROVE", 0)
    escalated = decision_counts.get("ESCALATE", 0)
    anomalies = sum(1 for r in all_runs if r.get("is_anomalous"))
    success_rate = round(approved / total * 100, 2) if total else 0.0
    return {
        "total_active_agents": len(list_agents()),
        "total_executions": total,
        "system_success_rate": success_rate,
        "escalated_runs": escalated,
        "anomalies_detected": anomalies,
    }


@app.get("/api/agents")
def agents_overview():
    ensure_all_audited()
    all_runs = list_runs()
    by_agent = {}
    for r in all_runs:
        by_agent.setdefault(r["agent_name"], []).append(r)

    result = []
    for name, runs in by_agent.items():
        anomalies = sum(1 for r in runs if r.get("is_anomalous"))
        audit_accuracy = round((1 - anomalies / len(runs)) * 100, 1) if runs else 100.0
        result.append({
            "agent_key": name,
            "display_name": prettify_agent_name(name),
            "status": "ACTIVE" if runs else "IDLE",
            "total_runs": len(runs),
            "audit_accuracy": audit_accuracy,
        })
    result.sort(key=lambda a: a["total_runs"], reverse=True)
    return result


@app.get("/api/recent-activity")
def recent_activity(limit: int = 6):
    ensure_all_audited()
    all_runs = list_runs()[:limit]
    out = []
    for r in all_runs:
        out.append({
            "title": f"{r['decision'].title()} — {prettify_agent_name(r['agent_name'])}",
            "agent_name": prettify_agent_name(r["agent_name"]),
            "decision": r["decision"],
            "is_anomalous": bool(r.get("is_anomalous")),
            "when": relative_time(r["start_time"]),
        })
    return out


@app.get("/api/runs")
def runs_list(agent: str = None, status: str = None, search: str = None):
    ensure_all_audited()
    all_runs = list_runs(agent)
    rows = []
    for r in all_runs:
        s_label = status_label(r)
        if status and status.lower() != s_label.lower():
            continue

        request_str = request_display(r["request"])
        if search and search.lower() not in request_str.lower():
            continue

        trace = load_run(r["agent_name"], r["run_id"])
        tool_calls = sum(1 for e in trace["events"] if e["event_type"] == "tool_call")

        rows.append({
            "run_id": r["run_id"],
            "agent_key": r["agent_name"],
            "agent_name": prettify_agent_name(r["agent_name"]),
            "task": request_str,
            "status": s_label,
            "risk_level": risk_label(r),
            "tool_calls": tool_calls,
            "duration": round(run_duration_seconds(trace), 2),
            "timestamp": r["start_time"],
        })
    return rows


@app.get("/api/runs/{agent_name}/{run_id}")
def run_detail(agent_name: str, run_id: str):
    try:
        trace = load_run(agent_name, run_id)
    except FileNotFoundError:
        raise HTTPException(404, "Run not found")

    if "audit" not in trace:
        analysis = analyze_run(trace)
        save_audit_result(agent_name, run_id, analysis)
        trace = load_run(agent_name, run_id)
    else:
        analysis = analyze_run(trace)

    return {
        "run_id": trace["run_id"],
        "agent_key": agent_name,
        "agent_name": prettify_agent_name(agent_name),
        "request": request_display(trace["request"]),
        "final_decision": trace["final_decision"],
        "events": trace["events"],
        "analysis": analysis,
        "duration": round(run_duration_seconds(trace), 2),
        "start_time": trace["start_time"],
        "end_time": trace.get("end_time"),
    }


@app.get("/api/runs/{agent_name}/{run_id}/graph")
def run_graph(agent_name: str, run_id: str):
    try:
        trace = load_run(agent_name, run_id)
    except FileNotFoundError:
        raise HTTPException(404, "Run not found")
    return build_graph(trace)


@app.post("/api/runs/{agent_name}/{run_id}/explain")
def run_explain(agent_name: str, run_id: str):
    try:
        trace = load_run(agent_name, run_id)
    except FileNotFoundError:
        raise HTTPException(404, "Run not found")
    analysis = analyze_run(trace)
    explanation = explain_run(trace, analysis)
    return {"explanation": explanation, "analysis": analysis}


@app.get("/api/analytics")
def analytics():
    ensure_all_audited()
    all_runs = list_runs()
    decision_counts = Counter(r["decision"] for r in all_runs)

    anomaly_logs = []
    for r in all_runs:
        if r.get("is_anomalous"):
            trace = load_run(r["agent_name"], r["run_id"])
            reasons = trace.get("audit", {}).get("reasons", [])
            anomaly_logs.append({
                "run_id": r["run_id"][:8],
                "agent_name": prettify_agent_name(r["agent_name"]),
                "decision": r["decision"],
                "reasons": reasons,
                "severity": "High" if len(reasons) > 1 else "Medium",
            })

    total = len(all_runs)
    anomaly_count = len(anomaly_logs)
    risk_score = round((anomaly_count / total) * 100) if total else 0

    return {
        "decision_distribution": dict(decision_counts),
        "anomaly_logs": anomaly_logs,
        "risk_score": risk_score,
        "risk_level": "High" if risk_score > 30 else ("Medium" if risk_score > 10 else "Low"),
        "total_runs_analyzed": total,
        "anomalies_detected": anomaly_count,
    }


# ---------------------------------------------------------------------
# Serve the static frontend (must be mounted last)
# ---------------------------------------------------------------------

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
