# core/sdk.py

"""
The AgentAudit SDK.

Before this, every agent hand-wrote its own execute_tool() method that
manually called tracer.log_tool_call() — meaning AgentAudit only worked
because each agent's author remembered to wire it in by hand, and only
tool calls were observed, never the LLM's own intermediate reasoning.

This is the actual "small wrapper/SDK that sits around your agent's
tool calls and LLM calls" — you instrument your tools and your LLM
client ONCE in __init__, and every call after that is observed
automatically. Nothing else in the agent changes, and business logic
(policy.py, tools.py, data.py) never needs to import the tracer at all.

Usage inside any agent's __init__:

    from core.sdk import instrument_tools, instrument_llm_client

    self.tracer = AgentTracer()
    self.client = instrument_llm_client(OpenRouter(api_key=...), self.tracer)
    self.tool_mapping = instrument_tools(
        {"check_order": check_order, ...},
        self.tracer
    )

From then on, self.client.chat.send(...) and
self.tool_mapping[name](**args) behave exactly as before — they just
also log themselves. This is also what makes AgentAudit usable on a
THIRD agent nobody on the team wrote: as long as it exposes a dict of
tool functions and an OpenRouter-style client, instrumenting it is two
function calls, no execute_tool boilerplate required.
"""

import functools
import time


def instrument_tools(tool_mapping, tracer):
    """
    Wrap a {tool_name: function} dict so every call is automatically
    timed and logged to `tracer`. Returns a new dict with the same
    keys — the agent calls it exactly like the original mapping.
    """

    return {
        tool_name: _wrap_tool(tool_name, fn, tracer)
        for tool_name, fn in tool_mapping.items()
    }


def _wrap_tool(tool_name, fn, tracer):

    @functools.wraps(fn)
    def wrapper(**kwargs):

        start_time = time.time()

        print()
        print(f"Tool selected: {tool_name}")
        print(f"Arguments: {kwargs}")

        try:
            result = fn(**kwargs)

        except Exception as e:
            result = {"error": str(e)}

        duration = time.time() - start_time

        print(f"Tool result: {result}")

        tracer.log_tool_call(
            tool_name=tool_name,
            input_data=kwargs,
            output_data=result,
            duration=duration,
        )

        return result

    return wrapper


def instrument_llm_client(client, tracer):
    """
    Wrap an OpenRouter-style client so every client.chat.send(...) call
    is automatically logged as an "llm_call" event — the model's own
    message content and which tools it chose to call, not just tool
    results. Mutates and returns the same client so it can be used as
    a drop-in replacement wherever the agent already had one.
    """

    original_send = client.chat.send

    @functools.wraps(original_send)
    def wrapped_send(**kwargs):

        start_time = time.time()

        response = original_send(**kwargs)

        duration = time.time() - start_time

        message = response.choices[0].message

        tool_calls_requested = [
            call.function.name for call in (message.tool_calls or [])
        ]

        tracer.log_llm_call(
            model=kwargs.get("model"),
            content=message.content,
            tool_calls_requested=tool_calls_requested,
            duration=duration,
        )

        return response

    client.chat.send = wrapped_send

    return client
