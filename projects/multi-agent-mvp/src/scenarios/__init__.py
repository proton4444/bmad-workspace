"""Real-world scenario validation module."""

from .real_world import (
    ScenarioResult,
    run_all_scenarios,
    run_product_launch_scenario,
    run_research_paper_scenario,
    run_software_project_scenario,
)

__all__ = [
    "ScenarioResult",
    "run_software_project_scenario",
    "run_research_paper_scenario",
    "run_product_launch_scenario",
    "run_all_scenarios",
]
