# travel.py

import json
import os

from dotenv import load_dotenv
from openrouter import OpenRouter

from .tools import (
    search_flights,
    check_blackout_date,
    check_traveler_profile,
    book_flight
)

from .policy import check_travel_policy

from core.tracer import AgentTracer
from core.sdk import instrument_tools, instrument_llm_client


load_dotenv()


class TravelAgent:

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
                    "name": "search_flights",
                    "description": "Search available flights between two airport codes on a given date.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {
                                "type": "string",
                                "description": "Origin airport code, e.g. BOM."
                            },
                            "destination": {
                                "type": "string",
                                "description": "Destination airport code, e.g. DEL."
                            },
                            "date": {
                                "type": "string",
                                "description": "Travel date in YYYY-MM-DD format."
                            }
                        },
                        "required": ["origin", "destination", "date"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_travel_policy",
                    "description": "Check whether a flight's total fare (base fare plus taxes) is within the company travel budget.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base_fare": {
                                "type": "number",
                                "description": "The flight's base fare."
                            },
                            "taxes": {
                                "type": "number",
                                "description": "The flight's taxes and fees."
                            }
                        },
                        "required": ["base_fare", "taxes"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_blackout_date",
                    "description": "Check whether a travel date falls within a company blackout period.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Travel date in YYYY-MM-DD format."
                            }
                        },
                        "required": ["date"]
                    }
                }
            },

            {
                "type": "function",
                "function": {
                    "name": "check_traveler_profile",
                    "description": "Check the traveler's profile and whether they are flagged for review.",
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
                    "name": "book_flight",
                    "description": "Book a flight after the agent has determined that the booking should be approved.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "flight_id": {
                                "type": "string",
                                "description": "The flight ID to book."
                            }
                        },
                        "required": ["flight_id"]
                    }
                }
            }
        ]

        # ---------------------------------------------------------
        # Map tool names to Python functions, instrumented by the SDK
        # ---------------------------------------------------------

        raw_tools = {

            "search_flights": search_flights,

            "check_travel_policy": check_travel_policy,

            "check_blackout_date": check_blackout_date,

            "check_traveler_profile": check_traveler_profile,

            "book_flight": book_flight
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
            agent_name="travel",
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
You are a corporate travel-booking AI agent.

Your job is to evaluate flight booking requests using the available tools.

IMPORTANT RULES:

1. You must use the available tools instead of guessing information.

2. Always use search_flights to find matching flights before choosing one.

3. Always check the travel policy for the flight's base fare and taxes together.

4. Always check whether the travel date is a blackout date.

5. You must use check_traveler_profile to determine whether the traveler is flagged.

6. Do not decide whether a traveler is flagged based on your own judgment.
   Use the check_traveler_profile tool.

7. Flagged travelers must be escalated regardless of policy or blackout status.

8. Never book a flight unless the travel policy says the fare is eligible.

9. Never book a flight on a blackout date.

10. If the fare is not eligible, reject the request.

11. If the fare is eligible but the date is a blackout date, escalate it.

12. If the fare is eligible, the date is not a blackout date, but the
    traveler is flagged, escalate it.

13. If the fare is eligible, the date is not a blackout date, and the
    traveler is not flagged, approve and book the flight.

14. Only call book_flight when the final decision is APPROVE.

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
                    "agent_name": "travel",
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

            "agent_name": "travel",

            "decision": decision,

            "reason": reason,

            "status": "completed",

            "run_id": run_id,

            "trace": trace
        }
