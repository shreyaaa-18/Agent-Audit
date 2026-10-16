# AgentAudit - Loan Approval Agent

## How to Run the Project in VS Code

### 1. Extract the ZIP file

Extract the ZIP file to your computer.

Open **VS Code**.

Go to:

**File → Open Folder**

Select the extracted `AgentAudit` folder.

---

### 2. Open the VS Code Terminal

In VS Code, open:

**Terminal → New Terminal**

Make sure the terminal is opened inside the `AgentAudit` project folder.

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

### 7. Run the Loan Approval Agent

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
Applicant APPL001 wants a loan approved for application LOAN001.
The loan is for medical expenses.
"""
```

Replace the request with one of the scenarios below and run `main.py` again.

---

## Scenario 1: Normal Loan Approval

Use:

```python
request = """
Applicant APPL001 wants a loan approved for application LOAN001.
The loan is for medical expenses.
"""
```

Expected result:

```text
APPROVE
```

The application is eligible, the applicant is not suspicious, and the loan amount is below the high-value threshold.

---

## Scenario 2: Application Outside Policy

Use:

```python
request = """
Applicant APPL002 wants a loan approved for application LOAN002.
The loan is for debt consolidation.
"""
```

Expected result:

```text
REJECT
```

Debt-consolidation loans require a credit score of 700 or higher, and this applicant's credit score is only 680.

---

## Scenario 3: Suspicious Applicant

Use:

```python
request = """
Applicant APPL003 wants a loan approved for application LOAN003.
The loan is for medical expenses.
"""
```

Expected result:

```text
ESCALATE
```

The applicant has a suspicious history with multiple previous loans.

---

## Scenario 4: High-Value Eligible Application

To test high-value escalation, first add the following application to `data.py`:

```python
"LOAN005": {
    "applicant_id": "APPL002",
    "loan_type": "personal",
    "purpose": "medical_expenses",
    "credit_score": 680,
    "amount": 1500000
}
```

Then change the request in `main.py` to:

```python
request = """
Applicant APPL002 wants a loan approved for application LOAN005.
The loan is for medical expenses.
"""
```

Run `main.py`.

Expected result:

```text
ESCALATE
```

The application is eligible for approval, but its amount is above the ₹10,00,000 high-value threshold.

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
Tool: check_loan_application

Step 2
Tool: check_loan_policy

Step 3
Tool: check_applicant_history

Step 4
Tool: check_loan_amount
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
