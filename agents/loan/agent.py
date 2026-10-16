# loan_agent.py

import json
import os

from dotenv import load_dotenv
from openrouter import OpenRouter

from .tools import (
    check_loan_application,
    check_applicant_history,
    check_loan_amount,
    process_loan_approval
)

from .policy import check_loan_policy

from core.tracer import AgentTracer
from core.sdk import instrument_tools, instrument_llm_client
from core.storage import save_run


load_dotenv()


class LoanApprovalAgent:

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
                    "name": "check_loan_application",
                    "description": "Check a loan application using its loan ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "loan_id": {
                                "type": "string",
                                "description": "The loan application ID."
                            }
                        },
                        "required": ["loan_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_applicant_history",
                    "description": "Check the applicant's previous loan history and whether the account is suspicious.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "applicant_id": {
                                "type": "string",
                                "description": "The applicant's ID."
                            }
                        },
                        "required": ["applicant_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_loan_policy",
                    "description": "Check whether a loan application is eligible for approval based on the loan purpose and the applicant's credit score.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "purpose": {
                                "type": "string",
                                "description": "Purpose of the loan."
                            },
                            "credit_score": {
                                "type": "integer",
                                "description": "The applicant's credit score."
                            }
                        },
                        "required": [
                            "purpose",
                            "credit_score"
                        ]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_loan_amount",
                    "description": "Check whether a loan amount is high-value. Amounts above 1,000,000 INR require escalation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "The loan amount in INR."
                            }
                        },
                        "required": ["amount"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "process_loan_approval",
                    "description": "Process a loan approval after the agent has determined that the loan should be approved.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "loan_id": {
                                "type": "string",
                                "description": "The loan application ID."
                            }
                        },
                        "required": ["loan_id"]
                    }
                }
            }
        ]

        # ---------------------------------------------------------
        # Map tool names to Python functions, instrumented by SDK
        # ---------------------------------------------------------

        raw_tools = {

            "check_loan_application": check_loan_application,

            "check_applicant_history": check_applicant_history,

            "check_loan_policy": check_loan_policy,

            "check_loan_amount": check_loan_amount,

            "process_loan_approval": process_loan_approval
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
            agent_name="loan",
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
You are a loan-approval AI agent.

Your job is to evaluate loan applications using the available tools.

IMPORTANT RULES:

1. You must use the available tools instead of guessing information.

2. Always check the loan application before making a decision.

3. Always check the loan policy.

4. Check applicant history when applicant information is available.

5. You must use check_loan_amount to determine whether the loan is high-value.

6. A loan above ₹10,00,000 is considered high-value and must be escalated.

7. Do not decide whether a loan is high-value based on your own judgment.
   Use the check_loan_amount tool.

8. Suspicious applicants must be escalated.

9. Never process a loan approval unless the loan policy says the application is eligible.

10. If the application is not eligible, reject the request.

11. If the application is eligible but the loan is high-value, escalate it.

12. If the application is eligible but the applicant is suspicious, escalate it.

13. If the application is eligible, the loan is not high-value,
    and the applicant is not suspicious, approve the loan.

14. Only call process_loan_approval when the final decision is APPROVE.

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
                    "agent_name": "loan",
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

            "agent_name": "loan",

            "decision": decision,

            "reason": reason,

            "status": "completed",

            "run_id": run_id,

            "trace": trace
        }