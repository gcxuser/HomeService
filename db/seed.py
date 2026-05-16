from HomeService.db.session import SessionLocal
from HomeService.db.models import (
    ServiceItem,
    ServiceCategory,
    ServicePackage,
    Worker,
    WorkerAvailability,
    WorkerSkill,
)

DEFAULT_CATEGORIES = [
    {"name": "保洁", "description": "家庭日常及深度保洁服务"},
    {"name": "专项", "description": "专项清洗、擦玻璃、地毯和家电清洗"},
]

DEFAULT_ITEMS = [
    {
        "name": "日常保洁",
        "category": "保洁",
        "base_price": 120.0,
        "price_unit": "per_hour",
        "estimated_duration": 3.0,
        "description": "客厅、卧室、厨房台面、卫生间、阳台基础清洁。",
    },
    {
        "name": "深度保洁",
        "category": "保洁",
        "base_price": 220.0,
        "price_unit": "per_hour",
        "estimated_duration": 5.0,
        "description": "厨房重油污、卫生间除垢、窗台、门窗、家具缝隙深度清洁。",
    },
    {
        "name": "开荒保洁",
        "category": "保洁",
        "base_price": 280.0,
        "price_unit": "per_hour",
        "estimated_duration": 6.0,
        "description": "新房交付或长期空置房的全面开荒清洁服务。",
    },
    {
        "name": "家电清洗",
        "category": "专项",
        "base_price": 150.0,
        "price_unit": "per_unit",
        "estimated_duration": 2.0,
        "description": "空调、油烟机、冰箱、洗衣机等家电专项清洗服务。",
    },
]

DEFAULT_PACKAGES = [
    {
        "name": "标准日常保洁套餐",
        "service_name": "日常保洁",
        "included_scope": "客厅、卧室、厨房、卫生间、阳台表面清洁、垃圾清理、吸尘拖地。",
        "excluded_scope": "不含地毯深层清洗、不含油烟机和冰箱内部清洗。",
        "base_price": 120.0,
        "estimated_duration": 3.0,
        "price_rule": "按小时计费，标准 120 元/小时，90 平米常规服务约 3 小时。",
    },
    {
        "name": "深度保洁升级套餐",
        "service_name": "深度保洁",
        "included_scope": "新增厨房油烟机、灶台、阳台窗台深度清洁。",
        "excluded_scope": "不含家具拆装、墙面翻新。",
        "base_price": 220.0,
        "estimated_duration": 5.0,
        "price_rule": "按小时计费，基础价格 220 元/小时，根据面积和油污程度测算。",
    },
]

DEFAULT_WORKERS = [
    {
        "name": "李阿姨",
        "city": "上海",
        "district": "浦东",
        "status": "active",
        "rating": 4.9,
        "tags": "细心,深度保洁,宠物友好",
    },
    {
        "name": "张师傅",
        "city": "上海",
        "district": "静安",
        "status": "active",
        "rating": 4.8,
        "tags": "快速,老人陪护,收纳整理",
    },
    {
        "name": "王阿姨",
        "city": "北京",
        "district": "朝阳",
        "status": "active",
        "rating": 4.7,
        "tags": "家电清洗,精细清洁",
    },
]

DEFAULT_WORKER_SKILLS = [
    {"worker_name": "李阿姨", "service_name": "深度保洁", "skill_level": "expert"},
    {"worker_name": "张师傅", "service_name": "日常保洁", "skill_level": "advanced"},
    {"worker_name": "王阿姨", "service_name": "家电清洗", "skill_level": "expert"},
]

DEFAULT_AVAILABILITIES = [
    {
        "worker_name": "李阿姨",
        "city": "上海",
        "district": "浦东",
        "available_date": "2026-05-18",
        "start_time": "09:00",
        "end_time": "13:00",
    },
    {
        "worker_name": "李阿姨",
        "city": "上海",
        "district": "浦东",
        "available_date": "2026-05-18",
        "start_time": "14:00",
        "end_time": "18:00",
    },
    {
        "worker_name": "张师傅",
        "city": "上海",
        "district": "静安",
        "available_date": "2026-05-18",
        "start_time": "10:00",
        "end_time": "16:00",
    },
]

def seed_default_data() -> None:
    db = SessionLocal()
    try:
        category_map = {}
        if db.query(ServiceCategory).count() == 0:
            for item in DEFAULT_CATEGORIES:
                category = ServiceCategory(**item)
                db.add(category)
            db.flush()
            category_map = {c.name: c for c in db.query(ServiceCategory).all()}
        else:
            category_map = {c.name: c for c in db.query(ServiceCategory).all()}

        item_map = {}
        if db.query(ServiceItem).count() == 0:
            for item in DEFAULT_ITEMS:
                category = category_map.get(item["category"])
                service_item = ServiceItem(
                    name=item["name"],
                    category=item["category"],
                    category_id=category.id if category else None,
                    base_price=item["base_price"],
                    price_unit=item["price_unit"],
                    estimated_duration=item["estimated_duration"],
                    description=item["description"],
                )
                db.add(service_item)
            db.flush()
            item_map = {i.name: i for i in db.query(ServiceItem).all()}
        else:
            item_map = {i.name: i for i in db.query(ServiceItem).all()}

        if db.query(ServicePackage).count() == 0:
            for package in DEFAULT_PACKAGES:
                service_item = item_map.get(package["service_name"])
                if service_item:
                    db.add(ServicePackage(
                        service_item_id=service_item.id,
                        name=package["name"],
                        included_scope=package["included_scope"],
                        excluded_scope=package["excluded_scope"],
                        base_price=package["base_price"],
                        estimated_duration=package["estimated_duration"],
                        price_rule=package["price_rule"],
                    ))

        if db.query(Worker).count() == 0:
            workers = []
            for item in DEFAULT_WORKERS:
                worker = Worker(**item)
                db.add(worker)
                workers.append(worker)
            db.flush()
            worker_map = {w.name: w for w in workers}
            for skill in DEFAULT_WORKER_SKILLS:
                worker = worker_map.get(skill["worker_name"])
                service_item = item_map.get(skill["service_name"])
                if worker and service_item:
                    db.add(WorkerSkill(
                        worker_id=worker.id,
                        service_item_id=service_item.id,
                        skill_level=skill["skill_level"],
                    ))
            for availability in DEFAULT_AVAILABILITIES:
                worker = worker_map.get(availability["worker_name"])
                if worker:
                    db.add(WorkerAvailability(
                        worker_id=worker.id,
                        city=availability["city"],
                        district=availability["district"],
                        available_date=availability["available_date"],
                        start_time=availability["start_time"],
                        end_time=availability["end_time"],
                        status="open",
                    ))

        db.commit()
    finally:
        db.close()
