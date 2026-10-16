# expense_agent.py

import json
import os

from dotenv import load_dotenv
from openrouter import OpenRouter

from .tools import (
    check_expense_report,
    check_employee_history,
    check_expense_value,
    reimburse_expense
)

from .policy import check_expense_policy

from core.tracer import AgentTracer
from core.sdk import instrument_tools, instrument_llm_client
from core.storage import save_run


load_dotenv()


class ExpenseAgent:

    def __init__(self):

        self.client = OpenRouter(
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

        self.model = "openrouter/free"

        # AgentAudit tracer
        self.tracer = AgentTracer()

        # Wrap the LLM client so every call is observed automatically
        self.client = instrument_llm_client(
            self.client,
            self.tracer
        )

        # ---------------------------------------------------------
        # Tools available to the LLM
        # ---------------------------------------------------------

        self.tools = [

            {
                "type": "function",
                "function": {
                    "name": "check_expense_report",
                    "description": "Check an expense report using its report ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {
                                "type": "string",
                                "description": "The expense report ID."
                            }
                        },
                        "required": ["report_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_employee_history",
                    "description": "Check the employee's previous expense claim history and whether the account is flagged.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "string",
                                "description": "The employee's ID."
                            }
                        },
                        "required": ["employee_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_expense_policy",
                    "description": "Check whether an expense is eligible for reimbursement based on category, days since the expense was incurred, and whether a receipt was provided.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Expense category, e.g. travel, meals, office_supplies, client_entertainment."
                            },
                            "days_since_expense": {
                                "type": "integer",
                                "description": "Number of days since the expense was incurred."
                            },
                            "has_receipt": {
                                "type": "boolean",
                                "description": "Whether a receipt was submitted with the expense."
                            }
                        },
                        "required": [
                            "category",
                            "days_since_expense",
                            "has_receipt"
                        ]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_expense_value",
                    "description": "Check whether an expense is high-value. Expenses above 10000 INR require escalation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "The expense amount in INR."
                            }
                        },
                        "required": ["amount"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "reimburse_expense",
                    "description": "Process reimbursement after the agent has determined that the expense should be approved.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_id": {
                                "type": "string",
                                "description": "The expense report ID."
                            }
                        },
                        "required": ["report_id"]
                    }
                }
            }
        ]

        # ---------------------------------------------------------
        # Map tool names to Python functions, instrumented by SDK
        # ---------------------------------------------------------

        raw_tools = {

            "check_expense_report": check_expense_report,

            "check_employee_history": check_employee_history,

            "check_expense_policy": check_expense_policy,

            "check_expense_value": check_expense_value,

            "reimburse_expense": reimburse_expense
        }

        self.tool_mapping = instrument_tools(
            raw_tools,
            self.tracer
        )

    # -------------------------------------------------------------
    # Main agent function
    # -------------------------------------------------------------

    def process_request(self, request):

        # ---------------------------------------------------------
        # Start a new AgentAudit run
        # ---------------------------------------------------------

        run_id = self.tracer.start_run(
            agent_name="expense",
            request=request
        )

        print()
        print("================================")
        print("STARTING AGENTAUDIT RUN")
        print("================================")
        print(f"Run ID: {run_id}")

        messages = [

            {
                "role": "system",

                "content": """
You are an expense-report approval AI agent.

Your job is to evaluate employee expense reports using the available tools.

IMPORTANT RULES:

1. You must use the available tools instead of guessing information.

2. Always check the expense report before making a decision.

3. Always check the reimbursement policy.

4. Check employee history when employee information is available.

5. You must use check_expense_value to determine whether the expense is high-value.

6. An expense above ₹10,000 is considered high-value and must be escalated.

7. Do not decide whether an expense is high-value based on your own judgment.
   Use the check_expense_value tool.

8. Flagged employees must be escalated.

9. Never reimburse an expense unless the reimbursement policy says it is eligible.

10. If the expense is not eligible, reject the request.

11. If the expense is eligible but the amount is high-value, escalate it.

12. If the expense is eligible but the employee is flagged, escalate it.

13. If the expense is eligible, the amount is not high-value,
    and the employee is not flagged, approve the reimbursement.

14. Only call reimburse_expense when the final decision is APPROVE.

15. If required information is missing, escalate the request.

Your final decision must be exactly one of:

APPROVE
REJECT
ESCALATE

Explain the decision briefly using the evidence returned by the tools.
"""
            },

            {
                "role": "user",
                "content": request
            }
        ]

        max_iterations = 10

        for _ in range(max_iterations):

            response = self.client.chat.send(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                stream=False
            )

            message = response.choices[0].message

            # Add assistant message to conversation

            messages.append(message)

            # -----------------------------------------------------
            # Final response
            # -----------------------------------------------------

            if not message.tool_calls:

                content = message.content

                if "APPROVE" in content.upper():

                    decision = "APPROVE"

                elif "REJECT" in content.upper():

                    decision = "REJECT"

                elif "ESCALATE" in content.upper():

                    decision = "ESCALATE"

                else:

                    decision = "UNKNOWN"

                # Record final decision

                self.tracer.log_decision(
                    decision=decision,
                    reason=content
                )

                # Finish run

                trace = self.tracer.end_run()

                # Persist trace

                save_run(trace)

                return {
                    "agent_name": "expense",
                    "decision": decision,
                    "reason": content,
                    "status": "completed",
                    "run_id": run_id,
                    "trace": trace
                }

            # -----------------------------------------------------
            # Execute tools requested by LLM
            # -----------------------------------------------------

            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                # Execute through the SDK-instrumented tool mapping

                if tool_name in self.tool_mapping:

                    tool_result = self.tool_mapping[
                        tool_name
                    ](**arguments)

                else:

                    tool_result = {
                        "error": f"Unknown tool: {tool_name}"
                    }

                # Send result back to LLM

                messages.append({

                    "role": "tool",

                    "tool_call_id": tool_call.id,

                    "content": json.dumps(tool_result)
                })

        # ---------------------------------------------------------
        # Maximum iterations reached
        # ---------------------------------------------------------

        decision = "ESCALATE"

        reason = "Maximum agent iterations reached."

        self.tracer.log_decision(
            decision=decision,
            reason=reason
        )

        trace = self.tracer.end_run()

        # Persist trace

        save_run(trace)

        return {

            "agent_name": "expense",

            "decision": decision,

            "reason": reason,

            "status": "completed",

            "run_id": run_id,

            "trace": trace
        }