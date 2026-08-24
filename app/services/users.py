from datetime import datetime, timezone

from app.core.firebase import firestore_client, firebase_auth


USERS = "users"


def ensure_user_profile(decoded_token: dict) -> dict:
    db = firestore_client()
    uid = decoded_token["uid"]
    ref = db.collection(USERS).document(uid)
    snap = ref.get()
    now = datetime.now(timezone.utc)

    if snap.exists:
        data = snap.to_dict() or {}
        if "updated_at" not in data:
            ref.update({"updated_at": now})
        return {"uid": uid, **data}

    user = {
        "uid": uid,
        "email": decoded_token.get("email"),
        "display_name": decoded_token.get("name"),
        "photo_url": decoded_token.get("picture"),
        "created_at": now,
        "updated_at": now,
    }
    ref.set(user)
    return user


def update_user_profile(uid: str, updates: dict) -> dict:
    db = firestore_client()
    ref = db.collection(USERS).document(uid)
    ref.set({**updates, "updated_at": datetime.now(timezone.utc)}, merge=True)
    snap = ref.get()
    return {"uid": uid, **(snap.to_dict() or {})}


def list_users(limit: int = 50) -> list[dict]:
    db = firestore_client()
    docs = db.collection(USERS).limit(limit).stream()
    return [{"uid": d.id, **(d.to_dict() or {})} for d in docs]


def revoke_refresh_tokens(uid: str) -> None:
    firebase_auth().revoke_refresh_tokens(uid)
