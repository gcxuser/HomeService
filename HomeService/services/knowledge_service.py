from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
from sqlalchemy.orm import Session
from HomeService.db.session import SessionLocal
from HomeService.db.models import KnowledgeDocument

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"
MANIFEST_FILE = STORAGE_DIR / "knowledge_manifest.json"

DEFAULT_KNOWLEDGE = [
    {
        "title": "日常保洁服务说明",
        "doc_type": "service",
        "service_type": "daily_cleaning",
        "city": "全国",
        "content": (
            "日常保洁适合已有定期清洁习惯的家庭，包含客厅、卧室、餐厅、厨房台面、卫生间、阳台表面清洁，"
            "以及垃圾清理、吸尘拖地。一般按照面积和工作时长计价，70-120 元/小时，"
            "90 平米住宅通常需要 3-4 小时完成。"
        ),
    },
    {
        "title": "深度保洁服务说明",
        "doc_type": "service",
        "service_type": "deep_cleaning",
        "city": "全国",
        "content": (
            "深度保洁适用于久未清洁或需要做一次彻底清洁的住宅，服务内容包括厨房油污清除、"
            "卫生间除垢、窗台、窗框、门窗、墙角、家具缝隙清洁。通常按面积加项目计价，"
            "90 平米住宅预计 4-6 小时，价格约为 200-400 元/小时，具体视油污程度和附加项目而定。"
        ),
    },
    {
        "title": "开荒保洁服务说明",
        "doc_type": "service",
        "service_type": "move_out_cleaning",
        "city": "全国",
        "content": (
            "开荒保洁适合新房交付或长期空置房屋，清洁范围涵盖地面、墙面、门窗、厨房、卫生间、阳台、管道表面和电器外壳。"
            "该服务通常需要多人配合，时长可达 6-10 小时，价格多以面积和难度综合评估。"
        ),
    },
    {
        "title": "家电清洗服务说明",
        "doc_type": "service",
        "service_type": "appliance_cleaning",
        "city": "全国",
        "content": (
            "家电清洗项目包括空调、油烟机、冰箱、洗衣机、热水器等，按台/套计价。"
            "家电清洗一般包含外部表面清洁、内部滤网清洗、积垢去除和消毒处理。"
            "建议在预约时说明家电类型、品牌和使用年限，以便安排合适师傅。"
        ),
    },
    {
        "title": "预约与取消规则",
        "doc_type": "policy",
        "service_type": "general",
        "city": "全国",
        "content": (
            "预约需要提前告知服务地址、面积、服务类型、期望时间和联系电话。"
            "一般建议至少提前 24 小时预约，以便安排师傅和计算上门时间。"
            "取消规则：服务开始前 24 小时可免费取消；12-24 小时取消可能扣取 50% 预约费；"
            "12 小时内取消可能扣费或仅退还部分费用。改约需另行确认师傅可用性。"
        ),
    },
]

class KnowledgeService:
    def __init__(self):
        self._ensure_storage_dir()
        self._ensure_default_documents()

    def _ensure_storage_dir(self) -> None:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def _ensure_default_documents(self) -> None:
        if not MANIFEST_FILE.exists():
            self._save_manifest(DEFAULT_KNOWLEDGE)

        db: Session = SessionLocal()
        try:
            count = db.query(KnowledgeDocument).count()
            if count == 0:
                docs = self._load_manifest()
                for item in docs:
                    doc = KnowledgeDocument(
                        title=item["title"],
                        doc_type=item["doc_type"],
                        service_type=item["service_type"],
                        city=item["city"],
                        content=item["content"],
                        created_at=datetime.utcnow(),
                    )
                    db.add(doc)
                db.commit()
        finally:
            db.close()

    def _load_manifest(self) -> List[Dict]:
        if not MANIFEST_FILE.exists():
            return DEFAULT_KNOWLEDGE
        with MANIFEST_FILE.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_manifest(self, docs: List[Dict]) -> None:
        with MANIFEST_FILE.open("w", encoding="utf-8") as handle:
            json.dump(docs, handle, ensure_ascii=False, indent=2)

    def create_document(self, title: str, doc_type: str, service_type: str, city: str, content: str) -> KnowledgeDocument:
        doc_data = {
            "title": title,
            "doc_type": doc_type,
            "service_type": service_type,
            "city": city,
            "content": content,
        }
        manifest = self._load_manifest()
        manifest.append(doc_data)
        self._save_manifest(manifest)

        db: Session = SessionLocal()
        doc = KnowledgeDocument(
            title=title,
            doc_type=doc_type,
            service_type=service_type,
            city=city,
            content=content,
            created_at=datetime.utcnow(),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        db.close()
        return doc

    def list_documents(self) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.id.desc()).all()
            return [self._to_dict(doc) for doc in docs]
        finally:
            db.close()

    def get_document(self, doc_id: int) -> Optional[Dict]:
        db: Session = SessionLocal()
        try:
            doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()
            return self._to_dict(doc) if doc else None
        finally:
            db.close()

    def search_documents(self, query: str) -> List[Dict]:
        db: Session = SessionLocal()
        try:
            query_lower = query.lower()
            docs = db.query(KnowledgeDocument).all()
            scored = []
            for doc in docs:
                score = 0
                content = f"{doc.title}\n{doc.content}".lower()
                if query_lower in content:
                    score += 10
                for token in query_lower.split():
                    score += content.count(token)
                if score > 0:
                    scored.append((score, doc))
            scored.sort(key=lambda pair: pair[0], reverse=True)
            return [self._to_dict(doc) for _, doc in scored[:10]]
        finally:
            db.close()

    def find_relevant_docs(self, query: str, top_k: int = 3) -> List[Dict]:
        docs = self.search_documents(query)
        if docs:
            return docs[:top_k]

        db: Session = SessionLocal()
        try:
            docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.id.desc()).limit(top_k).all()
            return [self._to_dict(doc) for doc in docs]
        finally:
            db.close()

    def _to_dict(self, doc: KnowledgeDocument) -> Dict:
        return {
            "id": doc.id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "service_type": doc.service_type,
            "city": doc.city,
            "content": doc.content,
            "created_at": doc.created_at.isoformat(),
        }
