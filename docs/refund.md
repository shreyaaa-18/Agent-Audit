# AgentAudit - Refund Agent

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

### 7. Run the Refund Agent

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
Customer CUST001 wants a refund for order ORD001.
The customer says the product arrived damaged.
"""
```

Replace the request with one of the scenarios below and run `main.py` again.

---

## Scenario 1: Normal Refund

Use:

```python
request = """
Customer CUST001 wants a refund for order ORD001.
The customer says the product arrived damaged.
"""
```

Expected result:

```text
APPROVE
```

The order is eligible, the customer is not suspicious, and the order value is below the high-value threshold.

---

## Scenario 2: Refund Outside Policy

Use:

```python
request = """
Customer CUST002 wants a refund for order ORD002.
The customer says they changed their mind.
"""
```

Expected result:

```text
REJECT
```

The order is 10 days old, while changed-mind refunds are allowed only within 7 days.

---

## Scenario 3: Suspicious Customer

Use:

```python
request = """
Customer CUST003 wants a refund for order ORD003.
The customer says the product arrived damaged.
"""
```

Expected result:

```text
ESCALATE
```

The customer has a suspicious history with multiple previous refunds.

---

## Scenario 4: High-Value Eligible Order

To test high-value escalation, first add the following order to `data.py`:

```python
"ORD005": {
    "customer_id": "CUST002",
    "product": "Laptop",
    "reason": "damaged",
    "days_since_purchase": 10,
    "value": 75000
}
```

Then change the request in `main.py` to:

```python
request = """
Customer CUST002 wants a refund for order ORD005.
The customer says the product arrived damaged.
"""
```

Run `main.py`.

Expected result:

```text
ESCALATE
```

The order is eligible for a refund, but its value is above the ₹50,000 high-value threshold.

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
Tool: check_order

Step 2
Tool: check_refund_policy

Step 3
Tool: check_customer_history

Step 4
Tool: check_order_value
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
