"""
Performance benchmarking for multi-agent workflows.

Measures execution time, throughput, agent utilization, and memory usage
across different workflow scales and configurations.

Story 4.2: Performance Benchmarking
Acceptance Criteria:
- AC1: Benchmark suite measures workflow execution time across scales
- AC2: Track task throughput, agent utilization, memory usage
- AC3: Compare performance across configurations
- AC4: Generate performance report with visualizations
- AC5: Validate performance targets (<1s for 10 tasks, <5s for 50 tasks)
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from src.orchestration.workflow import create_workflow_from_tasks


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    benchmark_name: str
    task_count: int
    agent_count: int
    workflow_config: str
    execution_time_ms: float
    tasks_completed: int
    tasks_per_second: float
    agent_utilization: Dict[str, float]  # Agent -> tasks completed
    memory_usage_mb: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Serialize benchmark result."""
        return {
            "benchmark_name": self.benchmark_name,
            "task_count": self.task_count,
            "agent_count": self.agent_count,
            "workflow_config": self.workflow_config,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "execution_time_s": round(self.execution_time_ms / 1000, 3),
            "tasks_completed": self.tasks_completed,
            "tasks_per_second": round(self.tasks_per_second, 2),
            "agent_utilization": {
                k: round(v, 2) for k, v in self.agent_utilization.items()
            },
            "memory_usage_mb": round(self.memory_usage_mb, 2),
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class BenchmarkSuite:
    """Suite of performance benchmarks."""

    suite_name: str = "Multi-Agent Workflow Performance"
    results: List[BenchmarkResult] = field(default_factory=list)
    performance_targets: Dict = field(
        default_factory=lambda: {
            "10_tasks_max_ms": 1000,  # <1s for 10 tasks
            "50_tasks_max_ms": 5000,  # <5s for 50 tasks
            "100_tasks_max_ms": 10000,  # <10s for 100 tasks
            "min_throughput_tasks_per_sec": 50,  # At least 50 tasks/sec
        }
    )
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def run_benchmark(
        self,
        benchmark_name: str,
        task_count: int,
        agent_names: List[str],
        workflow_config: str = "default",
        metadata: Optional[Dict] = None,
    ) -> BenchmarkResult:
        """
        AC1 & AC2: Run single benchmark and collect metrics.

        Args:
            benchmark_name: Name of benchmark
            task_count: Number of tasks to execute
            agent_names: List of agent names
            workflow_config: Configuration description
            metadata: Optional metadata

        Returns:
            BenchmarkResult with all metrics
        """
        # Create workflow
        task_ids = [f"task_{i}" for i in range(task_count)]
        orchestrator = create_workflow_from_tasks(
            workflow_id=f"bench_{benchmark_name}_{task_count}",
            task_ids=task_ids,
            agent_names=agent_names,
            problem_statement=f"Benchmark: {benchmark_name} with {task_count} tasks",
        )

        # Measure execution time
        start_time = time.time()
        result = orchestrator.complete_workflow()
        end_time = time.time()

        execution_time_ms = (end_time - start_time) * 1000
        tasks_completed = result["tasks_completed"]

        # Calculate throughput
        tasks_per_second = (
            tasks_completed / (execution_time_ms / 1000) if execution_time_ms > 0 else 0
        )

        # Calculate agent utilization (tasks per agent)
        agent_assignments = result["execution_results"]["agent_assignments"]
        total_assignments = sum(agent_assignments.values())
        agent_utilization = {
            agent: (count / total_assignments * 100 if total_assignments > 0 else 0)
            for agent, count in agent_assignments.items()
        }

        # Estimate memory usage (simplified - in real system would use tracemalloc)
        memory_usage_mb = self._estimate_memory_usage(orchestrator)

        benchmark_result = BenchmarkResult(
            benchmark_name=benchmark_name,
            task_count=task_count,
            agent_count=len(agent_names),
            workflow_config=workflow_config,
            execution_time_ms=execution_time_ms,
            tasks_completed=tasks_completed,
            tasks_per_second=tasks_per_second,
            agent_utilization=agent_utilization,
            memory_usage_mb=memory_usage_mb,
            metadata=metadata or {},
        )

        self.results.append(benchmark_result)
        return benchmark_result

    def _estimate_memory_usage(self, orchestrator) -> float:
        """Estimate memory usage of workflow (simplified)."""
        # Simplified estimation based on workflow components
        base_size = 0.5  # 0.5 MB base
        task_size = len(orchestrator.tasks) * 0.001  # ~1KB per task
        agent_size = len(orchestrator.agents) * 0.01  # ~10KB per agent
        idea_size = len(orchestrator.context.ideas) * 0.002  # ~2KB per idea

        return base_size + task_size + agent_size + idea_size

    def run_scale_benchmarks(
        self, task_counts: Optional[List[int]] = None
    ) -> List[BenchmarkResult]:
        """
        AC1: Run benchmarks across different scales.

        Args:
            task_counts: List of task counts to benchmark (default: [10, 25, 50, 100])

        Returns:
            List of benchmark results
        """
        if task_counts is None:
            task_counts = [10, 25, 50, 100]

        results = []
        for task_count in task_counts:
            result = self.run_benchmark(
                benchmark_name=f"scale_{task_count}",
                task_count=task_count,
                agent_names=["Athena", "Cato", "Zephyr"],
                workflow_config="3_agents_balanced",
                metadata={"scale_test": True},
            )
            results.append(result)

        return results

    def run_agent_count_benchmarks(
        self, agent_configs: Optional[List[List[str]]] = None
    ) -> List[BenchmarkResult]:
        """
        AC3: Compare performance across different agent counts.

        Args:
            agent_configs: List of agent name lists to test

        Returns:
            List of benchmark results
        """
        if agent_configs is None:
            agent_configs = [
                ["Athena"],
                ["Athena", "Cato"],
                ["Athena", "Cato", "Zephyr"],
            ]

        results = []
        task_count = 30  # Fixed task count for comparison

        for agents in agent_configs:
            result = self.run_benchmark(
                benchmark_name=f"agents_{len(agents)}",
                task_count=task_count,
                agent_names=agents,
                workflow_config=f"{len(agents)}_agents",
                metadata={"agent_count_test": True, "agents": agents},
            )
            results.append(result)

        return results

    def validate_performance_targets(self) -> Dict:
        """
        AC5: Validate system meets performance targets.

        Returns:
            Dict with validation results
        """
        validation_results = {
            "all_passed": True,
            "targets": {},
            "violations": [],
        }

        # Find relevant benchmarks
        bench_10 = next((r for r in self.results if r.task_count == 10), None)
        bench_50 = next((r for r in self.results if r.task_count == 50), None)
        bench_100 = next((r for r in self.results if r.task_count == 100), None)

        # Check 10 tasks target
        if bench_10:
            target_ms = self.performance_targets["10_tasks_max_ms"]
            passed = bench_10.execution_time_ms <= target_ms
            validation_results["targets"]["10_tasks"] = {
                "target_ms": target_ms,
                "actual_ms": round(bench_10.execution_time_ms, 2),
                "passed": passed,
            }
            if not passed:
                validation_results["all_passed"] = False
                validation_results["violations"].append(
                    f"10 tasks took {bench_10.execution_time_ms:.2f}ms, target is {target_ms}ms"
                )

        # Check 50 tasks target
        if bench_50:
            target_ms = self.performance_targets["50_tasks_max_ms"]
            passed = bench_50.execution_time_ms <= target_ms
            validation_results["targets"]["50_tasks"] = {
                "target_ms": target_ms,
                "actual_ms": round(bench_50.execution_time_ms, 2),
                "passed": passed,
            }
            if not passed:
                validation_results["all_passed"] = False
                validation_results["violations"].append(
                    f"50 tasks took {bench_50.execution_time_ms:.2f}ms, target is {target_ms}ms"
                )

        # Check throughput target
        if self.results:
            max_throughput = max(r.tasks_per_second for r in self.results)
            min_target = self.performance_targets["min_throughput_tasks_per_sec"]
            passed = max_throughput >= min_target
            validation_results["targets"]["throughput"] = {
                "target_tasks_per_sec": min_target,
                "actual_tasks_per_sec": round(max_throughput, 2),
                "passed": passed,
            }
            if not passed:
                validation_results["all_passed"] = False
                validation_results["violations"].append(
                    f"Max throughput {max_throughput:.2f} tasks/sec, target is {min_target}"
                )

        return validation_results

    def generate_report(self) -> Dict:
        """
        AC4: Generate comprehensive performance report.

        Returns:
            Dict with report data suitable for visualization
        """
        self.completed_at = datetime.now().isoformat()

        report = {
            "suite_name": self.suite_name,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_benchmarks": len(self.results),
            "performance_targets": self.performance_targets,
            "validation": self.validate_performance_targets(),
            "results": [r.to_dict() for r in self.results],
            "summary": self._generate_summary(),
            "visualizations": self._generate_visualization_data(),
        }

        return report

    def _generate_summary(self) -> Dict:
        """Generate summary statistics."""
        if not self.results:
            return {}

        return {
            "total_tasks_executed": sum(r.tasks_completed for r in self.results),
            "avg_execution_time_ms": round(
                sum(r.execution_time_ms for r in self.results) / len(self.results), 2
            ),
            "max_throughput_tasks_per_sec": round(
                max(r.tasks_per_second for r in self.results), 2
            ),
            "avg_memory_usage_mb": round(
                sum(r.memory_usage_mb for r in self.results) / len(self.results), 2
            ),
            "task_count_range": {
                "min": min(r.task_count for r in self.results),
                "max": max(r.task_count for r in self.results),
            },
        }

    def _generate_visualization_data(self) -> Dict:
        """
        AC4: Generate data formatted for visualizations.

        Returns:
            Dict with data for charts
        """
        # Sort results by task count for charts
        sorted_results = sorted(self.results, key=lambda r: r.task_count)

        viz_data = {
            "execution_time_by_scale": {
                "x_labels": [r.task_count for r in sorted_results],
                "y_values": [r.execution_time_ms for r in sorted_results],
                "chart_type": "line",
                "title": "Execution Time vs Task Count",
                "x_label": "Number of Tasks",
                "y_label": "Execution Time (ms)",
            },
            "throughput_by_scale": {
                "x_labels": [r.task_count for r in sorted_results],
                "y_values": [r.tasks_per_second for r in sorted_results],
                "chart_type": "bar",
                "title": "Throughput vs Task Count",
                "x_label": "Number of Tasks",
                "y_label": "Tasks per Second",
            },
            "memory_usage_by_scale": {
                "x_labels": [r.task_count for r in sorted_results],
                "y_values": [r.memory_usage_mb for r in sorted_results],
                "chart_type": "line",
                "title": "Memory Usage vs Task Count",
                "x_label": "Number of Tasks",
                "y_label": "Memory Usage (MB)",
            },
        }

        # Add agent utilization data if available
        if sorted_results and sorted_results[0].agent_utilization:
            agent_names = list(sorted_results[0].agent_utilization.keys())
            viz_data["agent_utilization"] = {
                "agents": agent_names,
                "utilization": [
                    sorted_results[-1].agent_utilization.get(agent, 0)
                    for agent in agent_names
                ],
                "chart_type": "pie",
                "title": "Agent Task Distribution",
            }

        return viz_data

    def export_report(self, filename: str = "benchmark_report.json"):
        """
        Export benchmark report to JSON file.

        Args:
            filename: Output filename
        """
        report = self.generate_report()

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        return filename


def run_full_benchmark_suite() -> BenchmarkSuite:
    """
    Run complete benchmark suite with all tests.

    Returns:
        BenchmarkSuite with all results
    """
    suite = BenchmarkSuite()

    print("Running scale benchmarks...")
    suite.run_scale_benchmarks([10, 25, 50, 100])

    print("Running agent count benchmarks...")
    suite.run_agent_count_benchmarks()

    print("Generating report...")
    report = suite.generate_report()

    print(f"\n{'=' * 60}")
    print(f"Performance Benchmark Results")
    print(f"{'=' * 60}")
    print(f"Total benchmarks: {report['total_benchmarks']}")
    print(f"Total tasks executed: {report['summary']['total_tasks_executed']}")
    print(f"Avg execution time: {report['summary']['avg_execution_time_ms']:.2f}ms")
    print(
        f"Max throughput: {report['summary']['max_throughput_tasks_per_sec']:.2f} tasks/sec"
    )
    print(f"Avg memory usage: {report['summary']['avg_memory_usage_mb']:.2f}MB")

    print(f"\n{'=' * 60}")
    print(f"Performance Target Validation")
    print(f"{'=' * 60}")
    validation = report["validation"]
    print(f"All targets passed: {validation['all_passed']}")

    for target_name, target_data in validation["targets"].items():
        status = "✓ PASS" if target_data["passed"] else "✗ FAIL"
        print(f"{status} - {target_name}")
        if "target_ms" in target_data:
            print(
                f"  Target: {target_data['target_ms']}ms, Actual: {target_data['actual_ms']}ms"
            )
        elif "target_tasks_per_sec" in target_data:
            print(
                f"  Target: {target_data['target_tasks_per_sec']} tasks/sec, "
                f"Actual: {target_data['actual_tasks_per_sec']} tasks/sec"
            )

    if validation["violations"]:
        print("\nViolations:")
        for violation in validation["violations"]:
            print(f"  - {violation}")

    return suite


if __name__ == "__main__":
    suite = run_full_benchmark_suite()
    filename = suite.export_report()
    print(f"\nReport exported to: {filename}")
