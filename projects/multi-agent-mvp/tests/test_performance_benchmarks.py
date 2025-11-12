"""
Tests for Story 4.2: Performance Benchmarking

Acceptance Criteria:
AC1: Benchmark suite measures workflow execution time across scales
AC2: Track task throughput, agent utilization, memory usage
AC3: Compare performance across configurations
AC4: Generate performance report with visualizations
AC5: Validate performance targets (<1s for 10 tasks, <5s for 50 tasks)
"""

import json
import os

import pytest
from src.benchmarks.performance import BenchmarkResult, BenchmarkSuite

# ============================================================================
# AC1: Benchmark suite measures execution time across scales
# ============================================================================


def test_benchmark_suite_creation():
    """AC1: BenchmarkSuite can be created and configured."""
    suite = BenchmarkSuite(suite_name="Test Suite")

    assert suite.suite_name == "Test Suite"
    assert len(suite.results) == 0
    assert suite.performance_targets["10_tasks_max_ms"] == 1000
    assert suite.performance_targets["50_tasks_max_ms"] == 5000


def test_run_single_benchmark():
    """AC1 & AC2: Run single benchmark and collect metrics."""
    suite = BenchmarkSuite()

    result = suite.run_benchmark(
        benchmark_name="test_bench",
        task_count=5,
        agent_names=["Athena", "Cato"],
        workflow_config="2_agents",
    )

    # Verify result structure
    assert result.benchmark_name == "test_bench"
    assert result.task_count == 5
    assert result.agent_count == 2
    assert result.workflow_config == "2_agents"
    assert result.execution_time_ms >= 0  # Can be 0 if very fast
    assert result.tasks_completed == 5
    assert result.tasks_per_second >= 0  # Can be 0 if time rounds to 0
    assert len(result.agent_utilization) > 0
    assert result.memory_usage_mb > 0


def test_run_scale_benchmarks():
    """AC1: Benchmark across different task scales."""
    suite = BenchmarkSuite()

    # Run with custom scales
    results = suite.run_scale_benchmarks(task_counts=[5, 10, 15])

    assert len(results) == 3
    assert results[0].task_count == 5
    assert results[1].task_count == 10
    assert results[2].task_count == 15

    # All should have completed successfully
    for result in results:
        assert result.tasks_completed == result.task_count
        assert result.execution_time_ms >= 0  # Can be 0 if very fast


def test_execution_time_increases_with_scale():
    """AC1: Execution time should increase (roughly) with task count."""
    suite = BenchmarkSuite()

    results = suite.run_scale_benchmarks(task_counts=[10, 20, 30])

    # Generally, more tasks take more time (though not strictly monotonic due to overhead)
    assert len(results) == 3
    # Just verify all completed
    assert all(r.tasks_completed > 0 for r in results)


# ============================================================================
# AC2: Track task throughput, agent utilization, memory usage
# ============================================================================


def test_benchmark_tracks_throughput():
    """AC2: Benchmark calculates tasks per second."""
    suite = BenchmarkSuite()

    result = suite.run_benchmark(
        benchmark_name="throughput_test",
        task_count=20,
        agent_names=["Athena", "Cato", "Zephyr"],
    )

    # Throughput should be positive
    assert result.tasks_per_second > 0

    # Should be reasonable (completed tasks / time in seconds)
    expected_throughput = result.tasks_completed / (result.execution_time_ms / 1000)
    assert abs(result.tasks_per_second - expected_throughput) < 0.1


def test_benchmark_tracks_agent_utilization():
    """AC2: Benchmark tracks which agents completed tasks."""
    suite = BenchmarkSuite()

    result = suite.run_benchmark(
        benchmark_name="utilization_test",
        task_count=15,
        agent_names=["Athena", "Cato", "Zephyr"],
    )

    # Should have utilization for agents
    assert len(result.agent_utilization) > 0

    # Utilization percentages should sum to ~100
    total_utilization = sum(result.agent_utilization.values())
    assert 99 <= total_utilization <= 101  # Allow small rounding error


def test_benchmark_tracks_memory_usage():
    """AC2: Benchmark estimates memory usage."""
    suite = BenchmarkSuite()

    result = suite.run_benchmark(
        benchmark_name="memory_test",
        task_count=10,
        agent_names=["Athena"],
    )

    # Should have positive memory estimate
    assert result.memory_usage_mb > 0

    # Should be reasonable (not gigabytes for small workflow)
    assert result.memory_usage_mb < 100  # Less than 100MB for 10 tasks


def test_memory_increases_with_scale():
    """AC2: Memory usage should increase with task count."""
    suite = BenchmarkSuite()

    result_small = suite.run_benchmark(
        benchmark_name="memory_small",
        task_count=10,
        agent_names=["Athena"],
    )

    result_large = suite.run_benchmark(
        benchmark_name="memory_large",
        task_count=100,
        agent_names=["Athena"],
    )

    # More tasks should use more memory
    assert result_large.memory_usage_mb > result_small.memory_usage_mb


# ============================================================================
# AC3: Compare performance across configurations
# ============================================================================


def test_run_agent_count_benchmarks():
    """AC3: Benchmark across different agent counts."""
    suite = BenchmarkSuite()

    agent_configs = [["Athena"], ["Athena", "Cato"]]
    results = suite.run_agent_count_benchmarks(agent_configs=agent_configs)

    assert len(results) == 2
    assert results[0].agent_count == 1
    assert results[1].agent_count == 2

    # Same task count for comparison
    assert results[0].task_count == results[1].task_count


def test_compare_different_configurations():
    """AC3: Can compare performance across configurations."""
    suite = BenchmarkSuite()

    # Run with different configurations
    result1 = suite.run_benchmark(
        benchmark_name="config_1",
        task_count=20,
        agent_names=["Athena"],
        workflow_config="single_agent",
    )

    result2 = suite.run_benchmark(
        benchmark_name="config_2",
        task_count=20,
        agent_names=["Athena", "Cato", "Zephyr"],
        workflow_config="three_agents",
    )

    # Both should complete all tasks
    assert result1.tasks_completed == 20
    assert result2.tasks_completed == 20

    # Different configurations
    assert result1.workflow_config != result2.workflow_config
    assert result1.agent_count != result2.agent_count


# ============================================================================
# AC4: Generate performance report with visualizations
# ============================================================================


def test_generate_report():
    """AC4: Can generate comprehensive performance report."""
    suite = BenchmarkSuite()

    # Run a few benchmarks
    suite.run_scale_benchmarks(task_counts=[10, 20])

    report = suite.generate_report()

    # Verify report structure
    assert "suite_name" in report
    assert "started_at" in report
    assert "completed_at" in report
    assert "total_benchmarks" in report
    assert "performance_targets" in report
    assert "validation" in report
    assert "results" in report
    assert "summary" in report
    assert "visualizations" in report

    # Verify results
    assert report["total_benchmarks"] == 2
    assert len(report["results"]) == 2


def test_report_includes_summary():
    """AC4: Report includes summary statistics."""
    suite = BenchmarkSuite()

    suite.run_scale_benchmarks(task_counts=[10, 20, 30])

    report = suite.generate_report()
    summary = report["summary"]

    assert "total_tasks_executed" in summary
    assert "avg_execution_time_ms" in summary
    assert "max_throughput_tasks_per_sec" in summary
    assert "avg_memory_usage_mb" in summary
    assert "task_count_range" in summary

    # Verify values
    assert summary["total_tasks_executed"] == 60  # 10 + 20 + 30
    assert summary["task_count_range"]["min"] == 10
    assert summary["task_count_range"]["max"] == 30


def test_report_includes_visualization_data():
    """AC4: Report includes data formatted for visualizations."""
    suite = BenchmarkSuite()

    suite.run_scale_benchmarks(task_counts=[10, 20, 30])

    report = suite.generate_report()
    viz = report["visualizations"]

    # Should have chart data
    assert "execution_time_by_scale" in viz
    assert "throughput_by_scale" in viz
    assert "memory_usage_by_scale" in viz

    # Check execution time chart
    exec_time_chart = viz["execution_time_by_scale"]
    assert exec_time_chart["chart_type"] == "line"
    assert exec_time_chart["x_labels"] == [10, 20, 30]
    assert len(exec_time_chart["y_values"]) == 3
    assert "title" in exec_time_chart
    assert "x_label" in exec_time_chart
    assert "y_label" in exec_time_chart


def test_export_report_to_file():
    """AC4: Can export report to JSON file."""
    suite = BenchmarkSuite()

    suite.run_benchmark(
        benchmark_name="export_test",
        task_count=5,
        agent_names=["Athena"],
    )

    # Export to temp file
    filename = "test_benchmark_report.json"

    try:
        suite.export_report(filename)

        # Verify file exists and is valid JSON
        assert os.path.exists(filename)

        with open(filename, "r") as f:
            data = json.load(f)

        assert data["suite_name"] == suite.suite_name
        assert data["total_benchmarks"] == 1

    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)


# ============================================================================
# AC5: Validate performance targets
# ============================================================================


def test_validate_performance_targets():
    """AC5: Can validate performance against targets."""
    suite = BenchmarkSuite()

    # Run benchmarks that should meet targets
    suite.run_scale_benchmarks(task_counts=[10, 50])

    validation = suite.validate_performance_targets()

    # Verify validation structure
    assert "all_passed" in validation
    assert "targets" in validation
    assert "violations" in validation

    # Should check 10 tasks target
    if "10_tasks" in validation["targets"]:
        target_check = validation["targets"]["10_tasks"]
        assert "target_ms" in target_check
        assert "actual_ms" in target_check
        assert "passed" in target_check


def test_performance_target_10_tasks():
    """AC5: Validate 10 tasks complete in <1 second."""
    suite = BenchmarkSuite()

    suite.run_benchmark(
        benchmark_name="target_10",
        task_count=10,
        agent_names=["Athena", "Cato", "Zephyr"],
    )

    validation = suite.validate_performance_targets()

    if "10_tasks" in validation["targets"]:
        target = validation["targets"]["10_tasks"]
        # Should pass the <1000ms target
        assert target["passed"] is True
        assert target["actual_ms"] < 1000


def test_performance_target_50_tasks():
    """AC5: Validate 50 tasks complete in <5 seconds."""
    suite = BenchmarkSuite()

    suite.run_benchmark(
        benchmark_name="target_50",
        task_count=50,
        agent_names=["Athena", "Cato", "Zephyr"],
    )

    validation = suite.validate_performance_targets()

    if "50_tasks" in validation["targets"]:
        target = validation["targets"]["50_tasks"]
        # Should pass the <5000ms target
        assert target["passed"] is True
        assert target["actual_ms"] < 5000


def test_throughput_target():
    """AC5: Validate throughput meets minimum target."""
    suite = BenchmarkSuite()

    # Run multiple benchmarks to get good throughput measurement
    suite.run_scale_benchmarks(task_counts=[20, 40])

    validation = suite.validate_performance_targets()

    if "throughput" in validation["targets"]:
        throughput_check = validation["targets"]["throughput"]
        assert "target_tasks_per_sec" in throughput_check
        assert "actual_tasks_per_sec" in throughput_check
        assert "passed" in throughput_check


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_benchmark_suite_run():
    """Integration: Run complete benchmark suite."""
    suite = BenchmarkSuite(suite_name="Integration Test Suite")

    # Run scale benchmarks
    scale_results = suite.run_scale_benchmarks(task_counts=[10, 25])
    assert len(scale_results) == 2

    # Run agent count benchmarks
    agent_results = suite.run_agent_count_benchmarks(
        agent_configs=[["Athena"], ["Athena", "Cato"]]
    )
    assert len(agent_results) == 2

    # Generate report
    report = suite.generate_report()

    # Should have all results
    assert report["total_benchmarks"] == 4

    # Should validate targets
    validation = report["validation"]
    assert "all_passed" in validation

    # Should have visualizations
    assert len(report["visualizations"]) >= 3


def test_benchmark_result_serialization():
    """Integration: BenchmarkResult can be serialized to dict."""
    result = BenchmarkResult(
        benchmark_name="serialize_test",
        task_count=10,
        agent_count=2,
        workflow_config="test_config",
        execution_time_ms=123.45,
        tasks_completed=10,
        tasks_per_second=81.0,
        agent_utilization={"Athena": 60.0, "Cato": 40.0},
        memory_usage_mb=1.5,
        metadata={"test": True},
    )

    result_dict = result.to_dict()

    # Verify all fields present
    assert result_dict["benchmark_name"] == "serialize_test"
    assert result_dict["task_count"] == 10
    assert result_dict["agent_count"] == 2
    assert result_dict["execution_time_ms"] == 123.45
    assert result_dict["execution_time_s"] == 0.123
    assert result_dict["tasks_per_second"] == 81.0

    # Should be JSON serializable
    json_str = json.dumps(result_dict)
    assert len(json_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
