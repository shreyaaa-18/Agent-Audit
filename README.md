# AgentAudit — Integrated Project

A common integration layer around four independently-built AI agents
(Refund, Travel, Loan Approval, Expense). Each agent keeps its own
tools, policies, and decision logic unchanged — AgentAudit only
standardizes how they're loaded, run, and traced.

```text
AgentAudit/
│
├── agents/
│   ├── refund/      → RefundAgent    (APPROVE / REJECT / ESCALATE)
│   ├── travel/       → TravelAgent    (APPROVE / REJECT / ESCALATE)
│   ├── loan/          → LoanApprovalAgent (APPROVE / REJECT / ESCALATE)
│   └── expense/     → ExpenseAgent   (APPROVE / REJECT / ESCALATE)
│       each containing: agent.py, tools.py, data.py, policy.py
│
├── core/
│   ├── agent_registry.py   # get_agent("refund") -> RefundAgent instance
│   └── tracer.py           # shared AgentTracer (identical across all 4 originals)
│
├── scripts/
│   └── expense_scenarios.py  # the 5 expense demo scenarios in one runner
│
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## How to run this project in VS Code

### 1. Open the folder

File → Open Folder → select this `AgentAudit` folder.

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows: `.venv\Scripts\activate`
macOS/Linux: `source .venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

Copy `.env.example` to `.env` and paste in your own OpenRouter key
(get one free at https://openrouter.ai/keys):

```bash
cp .env.example .env
```

```text
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> **Note:** the original four projects had real API keys committed
> directly in their `.env` files, and two of the four shared the same
> key. Those should be treated as compromised and rotated — this
> integrated project only ships a placeholder `.env.example`/`.env`.

### 5. Run it

```bash
python main.py
```

You'll get a menu:

```text
================================
       AGENTAUDIT SYSTEM
================================

Available Agents:

1. Refund Agent
2. Travel Agent
3. Loan Approval Agent
4. Expense Agent

Select an agent (number):
```

Pick a number, then type a request in plain English (see each
agent's original scenarios below). The agent runs its LLM + tool loop
exactly as it did standalone, then AgentAudit prints:

```text
Agent Name / Decision / Reason / Status / Run ID
```

followed by the full trace (every tool call, its input/output, and
execution time) and the final decision reason.

### 6. Run the Expense agent's scenario suite

```bash
python scripts/expense_scenarios.py
```

Runs all five expense demo scenarios (normal / late submission /
flagged employee / high-value / missing receipt) back-to-back.

## Test requests per agent

**Refund** — `Customer CUST001 wants a refund for order ORD001. The customer says the product arrived damaged.`

**Travel** — `Employee EMP001 wants to book a flight from BOM to DEL on 2026-09-20. Budget is 8000 rupees including taxes, morning departure preferred.`

**Loan Approval** — `Applicant APPL001 wants a loan approved for application LOAN001. The loan is for medical expenses.`

**Expense** — `Employee EMP001 submitted expense report EXP001. It is a travel expense for a client onsite visit.`

Each domain's `README`-equivalent scenarios (reject / escalate cases,
specific IDs, expected outcomes) are documented in the original
per-agent READMEs preserved under `docs/` — see `docs/refund.md`,
`docs/travel.md`, `docs/loan.md`, `docs/expense.md`.

## What's intentionally not built yet

Per the current project scope, this integration does **not** include:
Neo4j graph storage, anomaly detection, a dashboard, an explanation
layer, or multi-agent communication. Those are later phases.
