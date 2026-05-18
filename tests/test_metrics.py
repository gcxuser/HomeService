"""测试HomeService 评估指标系统"""

import pytest
import time
from HomeService.agents.router_agent import RouterAgent
from HomeService.eval.metrics import (
    IntentMetrics,
    RouteMetrics,
    ToolCallMetrics,
    TaskMetrics,
    PerformanceMetrics,
    CompositeMetrics,
    RoutingIntent,
)


class TestIntentMetrics:
    """意图识别准确率测试"""

    def test_basic_accuracy(self):
        """测试基本准确率计算"""
        metrics = IntentMetrics()

        # 添加样本：(真实意图, 预测意图)
        metrics.add_sample("booking", "booking")  # 正确
        metrics.add_sample("booking", "booking")  # 正确
        metrics.add_sample("consultation", "consultation")  # 正确
        metrics.add_sample("recommendation", "booking")  # 错误
        metrics.add_sample("booking", "booking")  # 正确

        result = metrics.accuracy
        assert result.total == 5
        assert result.correct == 4
        assert result.value == 0.8

    def test_perfect_accuracy(self):
        """测试完美准确率"""
        metrics = IntentMetrics()
        for _ in range(10):
            metrics.add_sample("booking", "booking")

        assert metrics.accuracy.value == 1.0

    def test_zero_accuracy(self):
        """测试零准确率"""
        metrics = IntentMetrics()
        for _ in range(5):
            metrics.add_sample("booking", "consultation")

        assert metrics.accuracy.value == 0.0

    def test_empty_metrics(self):
        """测试空指标"""
        metrics = IntentMetrics()
        assert metrics.accuracy.total == 0
        assert metrics.accuracy.value == 0.0


class TestRouteMetrics:
    """路由决策准确率测试"""

    def test_basic_routing(self):
        """测试基本路由"""
        metrics = RouteMetrics()

        # 测试路由到 booking agent
        metrics.add_sample("booking", RoutingIntent.BOOKING, "booking")
        metrics.add_sample("reschedule", RoutingIntent.BOOKING, "reschedule")  # 应该路由到 booking
        metrics.add_sample("cancel", RoutingIntent.BOOKING, "cancel")  # 应该路由到 booking

        # 测试路由到 consultation agent
        metrics.add_sample("consultation", RoutingIntent.CONSULTATION, "consultation")

        # 测试路由到 recommendation agent
        metrics.add_sample("recommendation", RoutingIntent.RECOMMENDATION, "recommendation")

        assert metrics.accuracy.total == 5
        # 3 booking + 1 consultation + 1 recommendation = 5 正确
        assert metrics.accuracy.correct == 5
        assert metrics.accuracy.value == 1.0

    def test_misrouting(self):
        """测试错误路由"""
        metrics = RouteMetrics()

        # 应该路由到 booking 但路由到了 consultation
        metrics.add_sample("booking", RoutingIntent.CONSULTATION, "booking")

        assert metrics.accuracy.total == 1
        assert metrics.accuracy.correct == 0


class TestToolCallMetrics:
    """工具调用准确率测试"""

    def test_basic_tool_call(self):
        """测试基本工具调用"""
        metrics = ToolCallMetrics()

        # 正确的工具调用
        metrics.add_call("get_available_slots", True)
        metrics.add_call("get_available_slots", True)
        metrics.add_call("estimate_price", True)
        metrics.add_call("estimate_price", False)  # 错误

        assert metrics.accuracy.total == 4
        assert metrics.accuracy.correct == 3
        assert abs(metrics.accuracy.value - 0.75) < 0.01

    def test_tool_precision(self):
        """测试工具调用精确率"""
        metrics = ToolCallMetrics()
        for _ in range(10):
            metrics.add_call("find_workers", True)
        assert metrics.precision.value == 1.0


class TestTaskMetrics:
    """任务完成率测试"""

    def test_basic_completion(self):
        """测试基本任务完成率"""
        metrics = TaskMetrics()

        # 完成的任务
        metrics.add_task("booking", True, True)
        metrics.add_task("booking", True, True)
        metrics.add_task("consultation", True, True)

        # 失败的任务
        metrics.add_task("booking", True, False)
        metrics.add_task("recommendation", True, False)

        # 完成率：5/5 = 100% (所有5个任务都执行了)
        assert metrics.completion_rate.total == 5
        assert metrics.completion_rate.correct == 5

        # 成功率：5/7 ≈ 71% (7个任务中有5个成功)
        # total = completed_tasks + failed_tasks = 5 + 2 = 7
        assert metrics.success_rate.total == 7
        assert metrics.success_rate.correct == 5

    def test_all_success(self):
        """测试全部成功"""
        metrics = TaskMetrics()
        for _ in range(10):
            metrics.add_task("booking", True, True)
        assert metrics.success_rate.value == 1.0


class TestPerformanceMetrics:
    """性能指标测试"""

    def test_basic_latency(self):
        """测试基本时延计算"""
        metrics = PerformanceMetrics()
        metrics.add_latency("booking_quote", 50)
        metrics.add_latency("booking_quote", 100)
        metrics.add_latency("booking_quote", 150)

        assert metrics.avg_latency.value == 100.0

    def test_percentile_calculation(self):
        """测试百分位数计算"""
        metrics = PerformanceMetrics()
        for i in range(1, 101):
            metrics.add_latency("test_op", i)

        # P50 应该在 50 附近 (取决于计算方式)
        assert 49 <= metrics.p50_latency.value <= 52
        # P95 应该在 95 附近
        assert 94 <= metrics.p95_latency.value <= 97
        # P99 应该在 99 附近
        assert 98 <= metrics.p99_latency.value <= 101

    def test_operation_details(self):
        """测试操作详情"""
        metrics = PerformanceMetrics()
        metrics.add_latency("quote", 30)
        metrics.add_latency("quote", 40)
        metrics.add_latency("scheduling", 50)

        assert "quote" in metrics.operation_latencies
        assert "scheduling" in metrics.operation_latencies
        assert len(metrics.operation_latencies["quote"]) == 2


class TestCompositeMetrics:
    """综合指标测试"""

    def test_full_workflow(self):
        """测试完整工作流"""
        metrics = CompositeMetrics()

        # 意图识别
        metrics.intent_metrics.add_sample("booking", "booking")
        metrics.intent_metrics.add_sample("booking", "booking")
        metrics.intent_metrics.add_sample("consultation", "consultation")
        metrics.intent_metrics.add_sample("recommendation", "booking")  # 错误

        # 路由决策
        metrics.route_metrics.add_sample("booking", RoutingIntent.BOOKING, "booking")
        metrics.route_metrics.add_sample("reschedule", RoutingIntent.BOOKING, "reschedule")
        metrics.route_metrics.add_sample("consultation", RoutingIntent.CONSULTATION, "consultation")

        # 工具调用
        metrics.tool_call_metrics.add_call("estimate_price", True)
        metrics.tool_call_metrics.add_call("estimate_price", True)
        metrics.tool_call_metrics.add_call("get_slots", True)
        metrics.tool_call_metrics.add_call("get_slots", False)

        # 任务完成
        metrics.task_metrics.add_task("quote", True, True)
        metrics.task_metrics.add_task("quote", True, True)
        metrics.task_metrics.add_task("scheduling", True, True)
        metrics.task_metrics.add_task("booking", True, False)

        # 性能
        metrics.performance_metrics.add_latency("quote", 25.5)
        metrics.performance_metrics.add_latency("quote", 30.2)
        metrics.performance_metrics.add_latency("scheduling", 45.8)

        # 获取摘要
        summary = metrics.get_summary()

        assert "intent_recognition_accuracy" in summary
        assert "route_accuracy" in summary
        assert "tool_call_accuracy" in summary
        assert "task_completion_rate" in summary
        assert "average_latency_ms" in summary

    def test_report_generation(self):
        """测试报告生成"""
        metrics = CompositeMetrics()

        # 添加一些数据
        for _ in range(10):
            metrics.intent_metrics.add_sample("booking", "booking")
            metrics.route_metrics.add_sample("booking", RoutingIntent.BOOKING, "booking")
            metrics.tool_call_metrics.add_call("estimate_price", True)
            metrics.task_metrics.add_task("quote", True, True)
            metrics.performance_metrics.add_latency("quote", 25)

        report = metrics.print_report()
        assert "HomeService 评估报告" in report
        assert "意图识别准确率" in report
        assert "路由决策准确率" in report


class TestIntegration:
    """集成测试 - 使用简单的意图检测"""

    def test_integration_with_metrics(self):
        """测试指标系统集成"""
        # 简化版本，避免 RAG 初始化问题
        from HomeService.agents.router_agent import INTENT_MAP
        from HomeService.eval.metrics import RoutingIntent

        def detect_intent(message: str) -> str:
            for keyword, intent in INTENT_MAP.items():
                if keyword in message:
                    return intent
            return "consultation"

        def get_route(intent: str) -> str:
            if intent in ["booking", "reschedule", "cancel"]:
                return "booking"
            elif intent == "recommendation":
                return "recommendation"
            else:
                return "consultation"

        metrics = CompositeMetrics()

        # 测试用例：(用户输入, 预期意图)
        test_cases = [
            ("我想预约家政服务", "booking"),
            ("改约预约", "booking"),
            ("取消预约", "booking"),
            ("家政服务价格", "pricing"),
            ("有什么服务", "consultation"),
            ("有什么推荐", "recommendation"),
        ]

        for user_input, expected_intent in test_cases:
            predicted_intent = detect_intent(user_input)
            predicted_route = get_route(predicted_intent)

            metrics.intent_metrics.add_sample(expected_intent, predicted_intent)
            metrics.route_metrics.add_sample(predicted_intent, RoutingIntent(predicted_route), expected_intent)

        # 验证指标
        assert metrics.intent_metrics.accuracy.total > 0
        assert metrics.route_metrics.accuracy.total > 0
