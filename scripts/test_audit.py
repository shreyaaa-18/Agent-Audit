from core.storage import load_run
from core.audit import audit_run, print_audit_report


agent_name = "refund"
run_id = "e6ac22fa-8b48-4067-a250-6f1449dd8974"


trace = load_run(agent_name, run_id)

report = audit_run(
    trace,
    use_llm=False
)

print_audit_report(report)