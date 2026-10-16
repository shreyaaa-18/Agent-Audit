# scripts/refund_scenarios.py

from core.simulator import AgentSimulator
from core.scenarios import REFUND_SCENARIOS


simulator = AgentSimulator("refund")


for scenario in REFUND_SCENARIOS:
    simulator.run(scenario)