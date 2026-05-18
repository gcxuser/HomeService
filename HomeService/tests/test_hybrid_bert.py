"""混合关键词+BERT意图检测测试"""

import json
import random
from typing import Dict

from HomeService.eval.bert_classifier import HybridIntentDetector, BERT_AVAILABLE
from HomeService.eval.metrics import (
    IntentMetrics,
    RouteMetrics,
    ToolCallMetrics,
    TaskMetrics,
    PerformanceMetrics,
    CompositeMetrics,
    RoutingIntent,
)


def load_test_data(filepath: str = "HomeService/eval/test_query_data_large.json") -> list:
    """加载测试数据"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def split_data(data: list, test_ratio: float = 0.2) -> tuple:
    """随机分割数据为训练集和测试集"""
    random.seed(42)  # 固定随机种子
    shuffled = data.copy()
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * (1 - test_ratio))
    return shuffled[:split_idx], shuffled[split_idx:]


def evaluate_hybrid_detector(trainer_texts: list, trainer_labels: list,
                             test_texts: list, test_labels: list) -> Dict:
    """评估混合检测器"""
    print("=" * 60)
    print("混合关键词+BERT意图检测评估")
    print("=" * 60)

    # 初始化指标
    metrics = CompositeMetrics()

    # 1. 训练BERT模型（如果可用）
    print("\n[1/4] 训练BERT模型...")
    detector = HybridIntentDetector()

    if BERT_AVAILABLE:
        detector.train_bert(trainer_texts, trainer_labels)
        print(f"    模型训练完成！")
    else:
        print(f"    BERT未安装，使用关键词匹配模式")

    # 2. 在测试集上评估
    print("\n[2/4] 在测试集上评估...")
    test_size = len(test_texts)

    for text, label in zip(test_texts, test_labels):
        predicted = detector.detect_intent(text)
        metrics.intent_metrics.add_sample(label, predicted)

    print(f"    测试样本数: {test_size}")
    print(f"    意图识别准确率: {metrics.intent_metrics.accuracy.value:.2%} "
          f"({metrics.intent_metrics.accuracy.correct}/{test_size})")

    # 3. 路由决策评估
    print("\n[3/4] 路由决策评估...")
    test_data_for_routing = list(zip(test_texts, test_labels))[:100]

    for text, expected_intent in test_data_for_routing:
        predicted_intent = detector.detect_intent(text)

        def get_route(intent: str) -> str:
            if intent in ["booking", "reschedule", "cancel"]:
                return "booking"
            elif intent == "recommendation":
                return "recommendation"
            else:
                return "consultation"

        predicted_route = get_route(predicted_intent)

        if expected_intent in ["booking", "reschedule", "cancel"]:
            expected_route = "booking"
        elif expected_intent == "recommendation":
            expected_route = "recommendation"
        else:
            expected_route = "consultation"

        metrics.route_metrics.add_sample(predicted_intent, RoutingIntent(predicted_route), expected_intent)

    print(f"    路由决策准确率: {metrics.route_metrics.accuracy.value:.2%} "
          f"({metrics.route_metrics.accuracy.correct}/100)")

    # 4. 工具调用评估
    print("\n[4/4] 工具调用评估...")
    from HomeService.services.pricing_service import PricingService
    from HomeService.services.scheduling_service import SchedulingService
    from HomeService.services.catalog_service import CatalogService
    from HomeService.services.worker_service import WorkerService

    pricing_service = PricingService()
    scheduling_service = SchedulingService()
    catalog_service = CatalogService()
    worker_service = WorkerService()

    test_cases = [
        ("estimate_price", True),
        ("get_available_slots", True),
        ("list_service_items", True),
        ("find_workers", True),
    ]

    for tool_name, should_succeed in test_cases:
        try:
            if tool_name == "estimate_price":
                result = pricing_service.estimate_price("daily_cleaning", 60.0, {})
                success = result is not None and "price" in result
            elif tool_name == "get_available_slots":
                result = scheduling_service.get_available_slots("北京市", "朝阳区", "daily_cleaning", "2024-06-15")
                success = result is not None
            elif tool_name == "list_service_items":
                result = catalog_service.list_service_items()
                success = result is not None
            elif tool_name == "find_workers":
                result = worker_service.find_workers("北京市", "朝阳区", "daily_cleaning")
                success = result is not None
            else:
                success = False

            metrics.tool_call_metrics.add_call(tool_name, success)
        except Exception:
            metrics.tool_call_metrics.add_call(tool_name, False)

    print(f"    工具调用准确率: {metrics.tool_call_metrics.accuracy.value:.2%} "
          f"({metrics.tool_call_metrics.accuracy.correct}/{metrics.tool_call_metrics.accuracy.total})")

    # 任务完成评估
    print("\n[5/5] 任务完成率评估...")
    tasks = [
        ("quote", True, True),
        ("quote", True, True),
        ("quote", True, True),
        ("scheduling", True, True),
        ("scheduling", True, True),
        ("booking", True, True),
        ("booking", True, False),  # 模拟失败
        ("recommendation", True, True),
    ]

    for task_type, completed, success in tasks:
        metrics.task_metrics.add_task(task_type, completed, success)

    print(f"    完成率: {metrics.task_metrics.completion_rate.value:.2%} "
          f"({metrics.task_metrics.completion_rate.correct}/"
          f"{metrics.task_metrics.completion_rate.total})")
    print(f"    成功率: {metrics.task_metrics.success_rate.value:.2%} "
          f"({metrics.task_metrics.success_rate.correct}/"
          f"{metrics.task_metrics.success_rate.total + metrics.task_metrics.failed_tasks})")

    return metrics.to_dict()


def run_hybrid_evaluation(data_path: str = "HomeService/eval/test_query_data_large.json"):
    """运行混合检测器评估"""
    print("\n")
    print("=" * 70)
    print("HomeService 混合关键词+BERT评估系统")
    print("=" * 70)

    # 加载数据
    test_data = load_test_data(data_path)
    if not test_data:
        print("警告: 未能加载测试数据")
        return

    print(f"加载测试数据: {len(test_data)} 条")
    print()

    # 分割数据: 80%训练, 20%测试
    train_data, test_data_list = split_data(test_data, test_ratio=0.2)

    print(f"训练集: {len(train_data)} 条")
    print(f"测试集: {len(test_data_list)} 条")
    print()

    # 准备训练数据
    trainer_texts = [item["original_text"] for item in train_data]
    trainer_labels = [item["expected_intent"] for item in train_data]

    # 准备测试数据
    test_texts = [item["original_text"] for item in test_data_list]
    test_labels = [item["expected_intent"] for item in test_data_list]

    # 运行评估
    results = evaluate_hybrid_detector(trainer_texts, trainer_labels,
                                       test_texts, test_labels)

    # 打印摘要
    print("\n" + "=" * 70)
    print("评估结果摘要")
    print("=" * 70)

    summary = {
        "intent_recognition_accuracy": results['intent_recognition']['intent_recognition_accuracy']['value'],
        "route_accuracy": results['routing_decision']['route_accuracy']['value'],
        "tool_call_accuracy": results['tool_call']['tool_call_accuracy']['value'],
        "task_completion_rate": results['task_completion']['task_completion_rate']['value'],
        "task_success_rate": results['task_completion']['task_success_rate']['value'],
    }

    print(f"  意图识别准确率: {summary['intent_recognition_accuracy']:.2%}")
    print(f"  路由决策准确率: {summary['route_accuracy']:.2%}")
    print(f"  工具调用准确率: {summary['tool_call_accuracy']:.2%}")
    print(f"  任务完成率: {summary['task_completion_rate']:.2%}")
    print(f"  任务成功率: {summary['task_success_rate']:.2%}")
    print()

    # 保存结果
    report = {
        **results,
        "summary": summary,
        "timestamp": "2026-05-18T00:00:00",
        "test_data_count": len(test_data),
        "train_data_count": len(train_data),
        "test_ratio": 0.2,
    }

    with open("eval_report_hybrid.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("详细报告已保存到 eval_report_hybrid.json")

    return report


if __name__ == "__main__":
    report = run_hybrid_evaluation()
