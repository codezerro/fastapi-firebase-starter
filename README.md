# FastAPI + Firebase Authentication + Firestore Starter

Production-oriented FastAPI boilerplate designed for Google Cloud Run.

## Architecture

```text
Web / Mobile Client
        |
        | Firebase Authentication
        v
 Firebase Auth
        |
        | ID token (JWT)
        v
      FastAPI -----------------> Firestore
        |
        v
   Cloud Run
```

This version intentionally does **not** implement a second JWT issuer. Firebase Authentication already issues signed ID tokens. The API verifies the Firebase ID token with the Firebase Admin SDK and uses the Firebase UID as the application identity.

## Features

- Firebase Authentication token verification
- `GET /api/v1/me` and profile update
- Session/revocation endpoint
- Firestore user profiles
- Firestore CRUD-style starter resource (`items`)
- Admin role support via Firebase custom claim: `admin=true`
- CORS configuration
- Health endpoint
- Dockerfile for Cloud Run
- Docker Compose local development
- Cloud Build deployment config
- Artifact Registry setup script
- Non-root Docker runtime
- Pytest starter

## 1. Firebase setup

1. Create/select a Google Cloud project.
2. Add/enable Firebase for that project.
3. In Firebase Authentication, enable the providers you need (Email/Password, Google, etc.).
4. Create a Firestore database.
5. For local development, create a service account or use Application Default Credentials.

The backend only needs the Firebase Admin SDK. Client applications should authenticate users with the Firebase client SDK and send:

```text
Authorization: Bearer <firebase-id-token>
```

## 2. Local development

Copy `.env.example` to `.env` and set your project ID.

For local credentials, either use ADC:

```bash
gcloud auth application-default login
```

or set:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/service-account.json
```

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload --port 8080
```

Docs: `http://localhost:8080/docs`

## 3. Docker

```bash
docker build -t fastapi-firebase-api .
docker run --rm -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json \
  -v "$PWD/service-account.json:/tmp/service-account.json:ro" \
  fastapi-firebase-api
```

For Compose, put your local service account at `./service-account.json` or change `GOOGLE_APPLICATION_CREDENTIALS_HOST`.

## 4. Admin role

Firebase custom claims are suitable for coarse application roles.

Example conceptually:

```python
firebase_admin.auth.set_custom_user_claims(uid, {"admin": True})
```

Then the API's `/api/v1/admin/users` endpoint will require `admin=true` in the verified Firebase token. After setting a custom claim, the client must obtain a refreshed ID token before the claim appears in the token.

Do not expose claim-setting functionality directly to untrusted clients.

## 5. Deploy to Cloud Run

### One-time setup

```bash
./deploy/setup-gcp.sh YOUR_PROJECT_ID asia-southeast1
```

Build and deploy manually:

```bash
gcloud builds submit \
  --config=deploy/cloudbuild.yaml \
  --substitutions=_REGION=asia-southeast1,_REPOSITORY=apps,_SERVICE=fastapi-firebase-api,_SERVICE_ACCOUNT=fastapi-firebase-api@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

Cloud Run uses its service account and Application Default Credentials. There is no service-account JSON file inside the container.

## 6. CI/CD

`deploy/cloudbuild.yaml` builds the image, pushes it to Artifact Registry, and deploys the immutable image tag to Cloud Run.

A typical GitHub setup is:

```text
GitHub push
   |
   v
Cloud Build trigger
   |
   +--> Docker build
   +--> Artifact Registry
   +--> Cloud Run
```

For GitHub-to-GCP authentication, prefer Workload Identity Federation instead of long-lived JSON service-account keys.

## 7. Firestore data model

```text
users/{firebase_uid}
  uid
  email
  display_name
  photo_url
  created_at
  updated_at

items/{item_id}
  owner_uid
  name
  description
  created_at
  updated_at
```

The API filters items by `owner_uid`, providing an application-level ownership boundary.

## 8. Production recommendations

- Keep Firebase client credentials and server credentials separate.
- Do not commit service-account JSON files.
- Restrict the Cloud Run runtime service account to the minimum required roles.
- Use Secret Manager for non-Firebase application secrets.
- Add structured logging and Cloud Logging correlation IDs.
- Add Firestore indexes as query patterns grow.
- Add rate limiting at the edge/API gateway for public APIs.
- Use Firebase App Check for supported client platforms when appropriate.
- Add automated tests around authorization and Firestore repository logic.

## Endpoints

- `GET /health`
- `GET /`
- `GET /api/v1/me` — authenticated
- `PATCH /api/v1/me` — authenticated
- `POST /api/v1/me/revoke-sessions` — authenticated
- `GET /api/v1/admin/users` — admin custom claim required
- `POST /api/v1/items` — authenticated
- `GET /api/v1/items` — authenticated

## Important Firebase auth distinction

The frontend authenticates with Firebase. The backend should not accept arbitrary user IDs from the client as the identity. It should derive the UID from the verified Firebase ID token (`uid`).
