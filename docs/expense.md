# ExpenseAudit - Expense Approval Agent

## How to Run the Project in VS Code

### 1. Extract the ZIP file

Extract the ZIP file to your computer.

Open **VS Code**.

Go to:

**File → Open Folder**

Select the extracted `ExpenseAudit` folder.

---

### 2. Open the VS Code Terminal

In VS Code, open:

**Terminal → New Terminal**

Make sure the terminal is opened inside the `ExpenseAudit` project folder.

---

### 3. Create a Virtual Environment

In the VS Code terminal, run:

```bash
python -m venv .venv
```

---

### 4. Activate the Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

After activation, you should see something similar to:

```text
(.venv)
```

at the beginning of the terminal line.

---

### 5. Select the Python Interpreter in VS Code

In VS Code:

1. Press `Ctrl + Shift + P` on Windows or `Cmd + Shift + P` on macOS.
2. Search for **Python: Select Interpreter**.
3. Select the Python interpreter from the `.venv` environment.

It should look similar to:

```text
.venv/bin/python
```

or on Windows:

```text
.venv\Scripts\python.exe
```

---

### 6. Install the Required Packages

Make sure the `.venv` environment is activated.

Run:

```bash
pip install -r requirements.txt
```

Wait for all packages to finish installing.

---

### 7. Add Your API Key

Open the `.env` file and replace the placeholder with your own OpenRouter API key:

```text
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

### 8. Run the Expense Agent

Open `main.py` in VS Code.

You can either:

- Click the **Run Python File** ▶ button in the top-right corner, or
- Run the following command in the VS Code terminal:

```bash
python main.py
```

The terminal will display:

- Tools selected by the agent
- Tool inputs and outputs
- Final agent decision
- AgentAudit trace
- Execution time for each tool call

---

# Testing Different Scenarios

The test request is written in `main.py`.

Find:

```python
request = """
Employee EMP001 submitted expense report EXP001.
It is a travel expense for a client onsite visit.
"""
```

Replace the request with one of the scenarios below and run `main.py` again.

---

## Scenario 1: Normal Reimbursement

Use:

```python
request = """
Employee EMP001 submitted expense report EXP001.
It is a travel expense for a client onsite visit.
"""
```

Expected result:

```text
APPROVE
```

The expense is eligible, the employee is not flagged, and the amount is below the high-value threshold.

---

## Scenario 2: Expense Submitted Too Late

Use:

```python
request = """
Employee EMP002 submitted expense report EXP002.
It is a meal expense from a team dinner.
"""
```

Expected result:

```text
REJECT
```

The expense was incurred 45 days ago, while meal expenses can only be claimed within 30 days.

---

## Scenario 3: Flagged Employee

Use:

```python
request = """
Employee EMP003 submitted expense report EXP003.
It is a client entertainment expense.
"""
```

Expected result:

```text
ESCALATE
```

The employee has a flagged history with an unusually high number of previous claims.

---

## Scenario 4: High-Value Eligible Expense

To test high-value escalation, first add the following report to `data.py`:

```python
"EXP005": {
    "employee_id": "EMP002",
    "category": "travel",
    "description": "Flight and hotel for regional conference",
    "days_since_expense": 10,
    "amount": 25000,
    "has_receipt": True
}
```

Then change the request in `main.py` to:

```python
request = """
Employee EMP002 submitted expense report EXP005.
It is a travel expense for a regional conference.
"""
```

Run `main.py`.

Expected result:

```text
ESCALATE
```

The expense is eligible for reimbursement, but its amount is above the ₹10,000 high-value threshold.

---

## Scenario 5: Missing Receipt

To test the missing-receipt rejection path, use:

```python
request = """
Employee EMP004 submitted expense report EXP004.
It is an office supplies purchase.
"""
```

Expected result:

```text
REJECT
```

No receipt was submitted with the expense, so it does not satisfy the reimbursement policy, regardless of the submission window.

---

# Checking the AgentAudit Trace

After each run, look at the:

```text
AGENTAUDIT TRACE
```

section in the VS Code terminal.

The trace records the observable actions performed by the agent, including:

- Tool name
- Tool input
- Tool output
- Tool execution time
- Final decision
- Decision reason

You should see steps similar to:

```text
Step 1
Tool: check_expense_report

Step 2
Tool: check_expense_policy

Step 3
Tool: check_employee_history

Step 4
Tool: check_expense_value
```

The exact order of tool calls may vary because the LLM decides which tool to use at each step.

At the end, check:

```text
Final Decision:
...

Decision Reason:
...
```

---

# Quick Run After Initial Setup

Once the virtual environment and dependencies have already been set up, open the project in VS Code and simply run:

```bash
python main.py
```

Or open `main.py` and click the **Run Python File** ▶ button.
