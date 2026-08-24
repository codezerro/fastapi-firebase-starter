import firebase_admin
from firebase_admin import credentials, firestore, auth

from app.core.config import settings


def init_firebase() -> None:
    if firebase_admin._apps:
        return

    # Cloud Run uses Application Default Credentials automatically.
    # For local development, GOOGLE_APPLICATION_CREDENTIALS can point to a service account JSON.
    options = {}
    if settings.google_cloud_project:
        options["projectId"] = settings.google_cloud_project
    if settings.firebase_storage_bucket:
        options["storageBucket"] = settings.firebase_storage_bucket

    firebase_admin.initialize_app(credentials.ApplicationDefault(), options=options or None)


def firestore_client():
    init_firebase()
    return firestore.client()


def firebase_auth():
    init_firebase()
    return auth
