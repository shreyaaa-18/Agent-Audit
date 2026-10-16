# AgentAudit - Travel Agent

## How to Run the Project in VS Code

### 1. Extract the ZIP file

Extract the ZIP file to your computer.

Open **VS Code**.

Go to:

**File → Open Folder**

Select the extracted `AgentAudit-Travel` folder.

---

### 2. Open the VS Code Terminal

In VS Code, open:

**Terminal → New Terminal**

Make sure the terminal is opened inside the project folder.

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

### 7. Add Your OpenRouter API Key

Open the `.env` file and replace the placeholder with your own free
OpenRouter API key (get one at https://openrouter.ai/keys):

```text
OPENROUTER_API_KEY=your-openrouter-api-key-here
```

---

### 8. Run the Travel Agent

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
Employee EMP001 wants to book a flight from BOM to DEL on 2026-09-20.
Budget is 8000 rupees including taxes, morning departure preferred.
"""
```

Replace the request with one of the scenarios below and run `main.py` again.

---

## Scenario 1: Normal Booking

Use:

```python
request = """
Employee EMP001 wants to book a flight from BOM to DEL on 2026-09-20.
Budget is 8000 rupees including taxes, morning departure preferred.
"""
```

Expected result:

```text
APPROVE
```

The UK955 (Vistara) flight has a total fare of 8150 which is actually over
budget once taxes are included — watch the trace to see whether the agent
correctly rejects it in favor of the SG412 (SpiceJet) flight at 6500 total,
or whether it mistakenly approves a flight by comparing base fare alone
against the cap. This is the scenario worth watching closely for
AgentAudit's explanation layer later.

---

## Scenario 2: Over-Budget Request

Use:

```python
request = """
Employee EMP002 wants to book a flight from BOM to DEL on 2026-09-20 on Air India.
Budget is 8000 rupees including taxes.
"""
```

Expected result:

```text
REJECT
```

AI803's total fare (base fare + taxes) is 9650, which exceeds the 8000 cap.

---

## Scenario 3: Blackout Date

Use:

```python
request = """
Employee EMP002 wants to book a flight from BOM to DEL on 2026-09-25.
Budget is 8000 rupees including taxes.
"""
```

Expected result:

```text
ESCALATE
```

2026-09-25 falls inside the company blackout period, even though the
6E890 flight itself is within budget.

---

## Scenario 4: Flagged Traveler

Use:

```python
request = """
Employee EMP003 wants to book a flight from BOM to DEL on 2026-09-20.
Budget is 8000 rupees including taxes.
"""
```

Expected result:

```text
ESCALATE
```

EMP003 is flagged in the traveler profile, so the request must be
escalated regardless of fare or date.

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
Tool: search_flights

Step 2
Tool: check_travel_policy

Step 3
Tool: check_blackout_date

Step 4
Tool: check_traveler_profile
```

The exact order of tool calls may vary because the LLM decides which tool
to use at each step.

At the end, check:

```text
Final Decision:
...

Decision Reason:
...
```

---

# Quick Run After Initial Setup

Once the virtual environment and dependencies have already been set up,
open the project in VS Code and simply run:

```bash
python main.py
```

Or open `main.py` and click the **Run Python File** ▶ button.
