from datetime import datetime, timezone
import uuid

from app.core.firebase import firestore_client


ITEMS = "items"


def create_item(owner_uid: str, name: str, description: str | None) -> dict:
    db = firestore_client()
    now = datetime.now(timezone.utc)
    item_id = str(uuid.uuid4())
    item = {
        "name": name,
        "description": description,
        "owner_uid": owner_uid,
        "created_at": now,
        "updated_at": now,
    }
    db.collection(ITEMS).document(item_id).set(item)
    return {"id": item_id, **item}


def list_items(owner_uid: str, limit: int = 100) -> list[dict]:
    db = firestore_client()
    docs = (
        db.collection(ITEMS)
        .where("owner_uid", "==", owner_uid)
        .order_by("created_at", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
