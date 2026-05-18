"""HomeService 评估指标定义"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from time import time
from enum import Enum


class RoutingIntent(Enum):
    """路由意图枚举"""
    BOOKING = "booking"           # 预约相关
    CONSULTATION = "consultation" # 咨询相关
    RECOMMENDATION = "recommendation"  # 推荐相关


@dataclass
class MetricResult:
    """单个指标结果"""
    name: str
    value: float
    total: int = 0
    correct: int = 0
    description: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": round(self.value, 4),
            "total": self.total,
            "correct": self.correct,
            "description": self.description
        }


@dataclass
class IntentMetrics:
    """意图识别准确率指标"""
    total_samples: int = 0
    correct_samples: int = 0
    # 混淆矩阵：(真实意图, 预测意图) -> 次数
    confusion_matrix: Dict[Tuple[str, str], int] = field(default_factory=dict)

    def add_sample(self, true_intent: str, predicted_intent: str) -> None:
        """添加一个样本"""
        self.total_samples += 1
        if true_intent == predicted_intent:
            self.correct_samples += 1
        key = (true_intent, predicted_intent)
        self.confusion_matrix[key] = self.confusion_matrix.get(key, 0) + 1

    @property
    def accuracy(self) -> MetricResult:
        """意图识别准确率"""
        value = self.correct_samples / self.total_samples if self.total_samples > 0 else 0.0
        return MetricResult(
            name="intent_recognition_accuracy",
            value=value,
            total=self.total_samples,
            correct=self.correct_samples,
            description="意图识别准确率：预测意图与真实意图一致的比例"
        )

    def to_dict(self) -> Dict:
        return {
            "intent_recognition_accuracy": {
                "value": round(self.accuracy.value, 4),
                "total": self.total_samples,
                "correct": self.correct_samples,
                "description": self.accuracy.description
            },
            "confusion_matrix": {
                f"{k[0]}_to_{k[1]}": v for k, v in self.confusion_matrix.items()
            }
        }


@dataclass
class RouteMetrics:
    """路由决策准确率指标"""
    total_samples: int = 0
    correct_samples: int = 0
    # 每个意图的路由准确率
    intent_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def add_sample(self, intent: str, routing_intent: RoutingIntent, expected_intent: str) -> None:
        """添加一个样本"""
        self.total_samples += 1

        # 预期意图映射到路由意图
        expected_route = self._intent_to_route(expected_intent)
        if routing_intent.value == expected_route:
            self.correct_samples += 1

        # 记录每个意图的路由情况
        if intent not in self.intent_stats:
            self.intent_stats[intent] = {"total": 0, "correct": 0}
        self.intent_stats[intent]["total"] += 1
        if routing_intent.value == expected_route:
            self.intent_stats[intent]["correct"] += 1

    def _intent_to_route(self, intent: str) -> str:
        """将真实意图映射到路由意图"""
        if intent in ["booking", "reschedule", "cancel"]:
            return "booking"
        elif intent == "recommendation":
            return "recommendation"
        else:
            return "consultation"

    @property
    def accuracy(self) -> MetricResult:
        """路由决策准确率"""
        value = self.correct_samples / self.total_samples if self.total_samples > 0 else 0.0
        return MetricResult(
            name="route_accuracy",
            value=value,
            total=self.total_samples,
            correct=self.correct_samples,
            description="路由决策准确率：正确路由到目标 Agent 的比例"
        )

    def to_dict(self) -> Dict:
        intent_details = {}
        for intent, stats in self.intent_stats.items():
            intent_details[intent] = {
                "accuracy": round(stats["correct"] / stats["total"], 4) if stats["total"] > 0 else 0.0,
                "total": stats["total"]
            }

        return {
            "route_accuracy": {
                "value": round(self.accuracy.value, 4),
                "total": self.total_samples,
                "correct": self.correct_samples,
                "description": self.accuracy.description
            },
            "intent_details": intent_details
        }


@dataclass
class ToolCallMetrics:
    """工具调用准确率指标"""
    total_calls: int = 0
    correct_calls: int = 0
    # 工具调用详情
    tool_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def add_call(self, tool_name: str, called_correctly: bool) -> None:
        """添加一个工具调用样本"""
        self.total_calls += 1
        if called_correctly:
            self.correct_calls += 1

        if tool_name not in self.tool_stats:
            self.tool_stats[tool_name] = {"total": 0, "correct": 0}
        self.tool_stats[tool_name]["total"] += 1
        if called_correctly:
            self.tool_stats[tool_name]["correct"] += 1

    @property
    def accuracy(self) -> MetricResult:
        """工具调用准确率"""
        value = self.correct_calls / self.total_calls if self.total_calls > 0 else 0.0
        return MetricResult(
            name="tool_call_accuracy",
            value=value,
            total=self.total_calls,
            correct=self.correct_calls,
            description="工具调用准确率：正确调用所需工具的比例"
        )

    @property
    def precision(self) -> MetricResult:
        """工具调用精确率（预测为正的中真正为正的比例）"""
        # 这里简化处理，与准确率相同
        return self.accuracy

    def to_dict(self) -> Dict:
        tool_details = {}
        for tool, stats in self.tool_stats.items():
            tool_details[tool] = {
                "accuracy": round(stats["correct"] / stats["total"], 4) if stats["total"] > 0 else 0.0,
                "total": stats["total"]
            }

        return {
            "tool_call_accuracy": {
                "value": round(self.accuracy.value, 4),
                "total": self.total_calls,
                "correct": self.correct_calls,
                "description": self.accuracy.description
            },
            "tool_details": tool_details
        }


@dataclass
class TaskMetrics:
    """任务完成率指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    # 任务完成详情
    task_details: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def add_task(self, task_type: str, completed: bool, success: bool) -> None:
        """添加一个任务"""
        self.total_tasks += 1

        if completed:
            self.completed_tasks += 1
            if success:
                self.task_details[task_type] = self.task_details.get(task_type, {})
                self.task_details[task_type]["success"] = self.task_details[task_type].get("success", 0) + 1
            else:
                self.failed_tasks += 1
                self.task_details[task_type] = self.task_details.get(task_type, {})
                self.task_details[task_type]["failed"] = self.task_details[task_type].get("failed", 0) + 1

    @property
    def completion_rate(self) -> MetricResult:
        """任务完成率"""
        value = self.completed_tasks / self.total_tasks if self.total_tasks > 0 else 0.0
        return MetricResult(
            name="task_completion_rate",
            value=value,
            total=self.total_tasks,
            correct=self.completed_tasks,
            description="任务完成率：成功完成的任务占总任务的比例"
        )

    @property
    def success_rate(self) -> MetricResult:
        """任务成功率（完成的任务中成功的比例）"""
        value = self.completed_tasks / (self.completed_tasks + self.failed_tasks) if (self.completed_tasks + self.failed_tasks) > 0 else 0.0
        return MetricResult(
            name="task_success_rate",
            value=value,
            total=self.completed_tasks + self.failed_tasks,
            correct=self.completed_tasks,
            description="任务成功率：完成的任务中成功完成的比例"
        )

    def to_dict(self) -> Dict:
        task_details = {}
        for task, stats in self.task_details.items():
            task_details[task] = {
                "success": stats.get("success", 0),
                "failed": stats.get("failed", 0)
            }

        return {
            "task_completion_rate": {
                "value": round(self.completion_rate.value, 4),
                "total": self.total_tasks,
                "completed": self.completed_tasks,
                "description": self.completion_rate.description
            },
            "task_success_rate": {
                "value": round(self.success_rate.value, 4),
                "completed_tasks": self.completed_tasks,
                "failed_tasks": self.failed_tasks,
                "description": self.success_rate.description
            },
            "task_details": task_details
        }


@dataclass
class PerformanceMetrics:
    """性能指标（执行时延）"""
    latencies: List[float] = field(default_factory=list)
    # 按操作类型的时延
    operation_latencies: Dict[str, List[float]] = field(default_factory=dict)

    def add_latency(self, operation: str, latency_ms: float) -> None:
        """添加一个时延样本"""
        self.latencies.append(latency_ms)
        if operation not in self.operation_latencies:
            self.operation_latencies[operation] = []
        self.operation_latencies[operation].append(latency_ms)

    def _calc_percentile(self, data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        index = min(index, len(sorted_data) - 1)
        return sorted_data[index]

    @property
    def avg_latency(self) -> MetricResult:
        """平均执行时延"""
        value = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        return MetricResult(
            name="average_latency_ms",
            value=value,
            total=len(self.latencies),
            correct=int(sum(self.latencies)),
            description="平均执行时延：所有操作的平均响应时间"
        )

    @property
    def p50_latency(self) -> MetricResult:
        """P50 时延（中位数）"""
        value = self._calc_percentile(self.latencies, 50)
        return MetricResult(
            name="p50_latency_ms",
            value=value,
            total=len(self.latencies),
            correct=int(value),
            description="P50 时延：50% 请求的响应时间"
        )

    @property
    def p95_latency(self) -> MetricResult:
        """P95 时延"""
        value = self._calc_percentile(self.latencies, 95)
        return MetricResult(
            name="p95_latency_ms",
            value=value,
            total=len(self.latencies),
            correct=int(value),
            description="P95 时延：95% 请求的响应时间"
        )

    @property
    def p99_latency(self) -> MetricResult:
        """P99 时延"""
        value = self._calc_percentile(self.latencies, 99)
        return MetricResult(
            name="p99_latency_ms",
            value=value,
            total=len(self.latencies),
            correct=int(value),
            description="P99 时延：99% 请求的响应时间"
        )

    def to_dict(self) -> Dict:
        operation_stats = {}
        for op, latencies in self.operation_latencies.items():
            if latencies:
                operation_stats[op] = {
                    "avg": round(sum(latencies) / len(latencies), 2),
                    "p50": round(self._calc_percentile(latencies, 50), 2),
                    "p95": round(self._calc_percentile(latencies, 95), 2),
                    "count": len(latencies)
                }

        return {
            "performance_metrics": {
                "average_latency_ms": round(self.avg_latency.value, 2),
                "p50_latency_ms": round(self.p50_latency.value, 2),
                "p95_latency_ms": round(self.p95_latency.value, 2),
                "p99_latency_ms": round(self.p99_latency.value, 2),
                "total_samples": len(self.latencies)
            },
            "operation_details": operation_stats
        }


@dataclass
class CompositeMetrics:
    """综合指标汇总"""
    intent_metrics: IntentMetrics = field(default_factory=IntentMetrics)
    route_metrics: RouteMetrics = field(default_factory=RouteMetrics)
    tool_call_metrics: ToolCallMetrics = field(default_factory=ToolCallMetrics)
    task_metrics: TaskMetrics = field(default_factory=TaskMetrics)
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "intent_recognition": self.intent_metrics.to_dict(),
            "routing_decision": self.route_metrics.to_dict(),
            "tool_call": self.tool_call_metrics.to_dict(),
            "task_completion": self.task_metrics.to_dict(),
            "performance": self.performance_metrics.to_dict()
        }

    def get_summary(self) -> Dict[str, float]:
        """获取核心指标摘要"""
        return {
            "intent_recognition_accuracy": round(self.intent_metrics.accuracy.value, 4),
            "route_accuracy": round(self.route_metrics.accuracy.value, 4),
            "tool_call_accuracy": round(self.tool_call_metrics.accuracy.value, 4),
            "task_completion_rate": round(self.task_metrics.completion_rate.value, 4),
            "task_success_rate": round(self.task_metrics.success_rate.value, 4),
            "average_latency_ms": round(self.performance_metrics.avg_latency.value, 2),
            "p50_latency_ms": round(self.performance_metrics.p50_latency.value, 2),
            "p95_latency_ms": round(self.performance_metrics.p95_latency.value, 2)
        }

    def print_report(self) -> str:
        """打印格式化报告"""
        summary = self.get_summary()

        report = [
            "=" * 60,
            "HomeService 评估报告",
            "=" * 60,
            "",
            "【核心指标】",
            f"  意图识别准确率: {summary['intent_recognition_accuracy']:.2%}",
            f"  路由决策准确率: {summary['route_accuracy']:.2%}",
            f"  工具调用准确率: {summary['tool_call_accuracy']:.2%}",
            f"  任务完成率: {summary['task_completion_rate']:.2%}",
            f"  任务成功率: {summary['task_success_rate']:.2%}",
            "",
            "【性能指标】",
            f"  平均响应时间: {summary['average_latency_ms']:.2f} ms",
            f"  P50 (中位数): {summary['p50_latency_ms']:.2f} ms",
            f"  P95: {summary['p95_latency_ms']:.2f} ms",
            "=" * 60,
        ]
        return "\n".join(report)
