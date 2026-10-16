# refund.py

import json
import os

from dotenv import load_dotenv
from openrouter import OpenRouter

from .tools import (
    check_order,
    check_customer_history,
    check_order_value,
    process_refund
)

from .policy import check_refund_policy

from core.tracer import AgentTracer
from core.sdk import instrument_tools, instrument_llm_client


load_dotenv()


class RefundAgent:

    def __init__(self):

        self.client = OpenRouter(
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

        self.model = "openrouter/free"

        # AgentAudit tracer
        self.tracer = AgentTracer()

        # Wrap the LLM client so every call is observed automatically
        self.client = instrument_llm_client(self.client, self.tracer)

        # ---------------------------------------------------------
        # Tools available to the LLM
        # ---------------------------------------------------------

        self.tools = [

            {
                "type": "function",
                "function": {
                    "name": "check_order",
                    "description": "Check an order using its order ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The customer's order ID."
                            }
                        },
                        "required": ["order_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_customer_history",
                    "description": "Check the customer's previous refund history and whether the account is suspicious.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "The customer's ID."
                            }
                        },
                        "required": ["customer_id"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_refund_policy",
                    "description": "Check whether an order is eligible for a refund based on the refund reason and number of days since purchase.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Reason for the refund."
                            },
                            "days_since_purchase": {
                                "type": "integer",
                                "description": "Number of days since the order was purchased."
                            }
                        },
                        "required": [
                            "reason",
                            "days_since_purchase"
                        ]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_order_value",
                    "description": "Check whether an order is high-value. Orders above 50000 INR require escalation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {
                                "type": "number",
                                "description": "The order value in INR."
                            }
                        },
                        "required": ["value"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "process_refund",
                    "description": "Process a refund after the agent has determined that the refund should be approved.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The order ID."
                            }
                        },
                        "required": ["order_id"]
                    }
                }
            }
        ]

        # ---------------------------------------------------------
        # Map tool names to Python functions, instrumented by the SDK
        # ---------------------------------------------------------

        raw_tools = {

            "check_order": check_order,

            "check_customer_history": check_customer_history,

            "check_refund_policy": check_refund_policy,

            "check_order_value": check_order_value,

            "process_refund": process_refund
        }

        self.tool_mapping = instrument_tools(raw_tools, self.tracer)

    # -------------------------------------------------------------
    # Main agent function
    # -------------------------------------------------------------

    def process_request(self, request):

        # ---------------------------------------------------------
        # Start a new AgentAudit run
        # ---------------------------------------------------------

        run_id = self.tracer.start_run(
            agent_name="refund",
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
You are a refund-processing AI agent.

Your job is to evaluate refund requests using the available tools.

IMPORTANT RULES:

1. You must use the available tools instead of guessing information.

2. Always check the order before making a decision.

3. Always check the refund policy.

4. Check customer history when customer information is available.

5. You must use check_order_value to determine whether the order is high-value.

6. An order above ₹50,000 is considered high-value and must be escalated.

7. Do not decide whether an order is high-value based on your own judgment.
   Use the check_order_value tool.

8. Suspicious customers must be escalated.

9. Never process a refund unless the refund policy says the order is eligible.

10. If the refund is not eligible, reject the request.

11. If the refund is eligible but the order is high-value, escalate it.

12. If the refund is eligible but the customer is suspicious, escalate it.

13. If the refund is eligible, the order is not high-value,
    and the customer is not suspicious, approve the refund.

14. Only call process_refund when the final decision is APPROVE.

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

                # Record final decision in AgentAudit

                self.tracer.log_decision(
                    decision=decision,
                    reason=content
                )

                # Finish run

                trace = self.tracer.end_run()

                return {
                    "agent_name": "refund",
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

                # Execute through the SDK-instrumented tool mapping —
                # logging happens automatically inside the wrapper

                if tool_name in self.tool_mapping:
                    tool_result = self.tool_mapping[tool_name](**arguments)
                else:
                    tool_result = {"error": f"Unknown tool: {tool_name}"}

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

        return {

            "agent_name": "refund",

            "decision": decision,

            "reason": reason,

            "status": "completed",

            "run_id": run_id,

            "trace": trace
        }