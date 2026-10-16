# scripts/travel_scenarios.py

from core.simulator import AgentSimulator
from core.scenarios import TRAVEL_SCENARIOS


simulator = AgentSimulator("travel")


for scenario in TRAVEL_SCENARIOS:
    simulator.run(scenario)