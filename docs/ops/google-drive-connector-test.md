# Google Drive Connector Test State

Date: 2026-04-27

This note records the non-secret tested state of the Onyx Google Drive connector. Keep service-account JSON keys and auth cookies out of git and out of this file.

## Current Result

Status: working end to end.

The Onyx Google Drive connector successfully indexed one Google Drive PDF from the configured test folder, and that document is discoverable through Onyx search.

Fresh test run:

- Connector: `Google Drive Test`
- Connector ID: `10`
- Credential: `Service Account (uploaded)`
- Credential ID: `6`
- Connector credential pair ID: `6`
- Source: `google_drive`
- Input type: `poll`
- Access type: `PUBLIC`
- Attached document set: `AiSci Wiki`
- Test run index attempt: `109`
- Test run status: `SUCCESS`
- Test run time: `2026-04-27 00:29:40Z` to `2026-04-27 00:31:06Z`
- Test run result: `total_docs_indexed=1`, `new_docs_indexed=0`, `total_chunks=18`

The earlier first successful Google Drive run was index attempt `106`, with `total_docs_indexed=1`, `new_docs_indexed=1`, and `total_chunks=18`.

Indexed document:

- Document ID: `https://drive.google.com/file/d/1FljUfpN2d4O87brUbAxJ2ogs2qdb-02f`
- Semantic ID: `oai_ai-as-a-scientific-collaborator_jan-2026.pdf`
- Link: `https://drive.google.com/file/d/1FljUfpN2d4O87brUbAxJ2ogs2qdb-02f/view?usp=drivesdk`
- Metadata path: `My Drive / AiSci`
- Chunk count: `18`
- Search query tested: `scientific collaborator`

## Google Cloud Setup

- Project display name: `missioncontrol314`
- Project ID: `missioncontrol314`
- Google Cloud organization: `21366002793`
- gcloud account used during setup: `jurkemik@activestyle.sk`
- Service account: `onyx-drive-connector-test@missioncontrol314.iam.gserviceaccount.com`
- Display name: `Onyx Drive Connector Test`
- Domain-wide delegation client ID / unique ID: `107191948287339294955`
- Active key ID: `a9288b25ff14c2092712149364893dc0cefcfd3c`

The local key file was created at:

```text
docs/ops/private/onyx-drive-connector-test-missioncontrol314.json
```

It was uploaded into Onyx and then removed locally after the successful test. As of this test, `docs/ops/private/` is empty.

Enabled APIs:

- `drive.googleapis.com`
- `admin.googleapis.com`
- `docs.googleapis.com`
- `sheets.googleapis.com`
- `iam.googleapis.com`
- `iamcredentials.googleapis.com`
- `cloudresourcemanager.googleapis.com`
- `serviceusage.googleapis.com`

## Workspace Admin State

Domain-wide delegation is functionally complete for this test, because the service-account connector can read and index the configured folder.

Configured OAuth scopes:

```text
https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/drive.metadata.readonly,https://www.googleapis.com/auth/admin.directory.group.readonly,https://www.googleapis.com/auth/admin.directory.user.readonly
```

The Primary Admin Email is stored in Onyx with the credential. Do not write it here unless there is a non-secret operational reason.

## Onyx Connector State

Onyx was reachable through nginx:

```bash
curl -sS -o /tmp/onyx_health.out -w '%{http_code}\n' http://localhost:3000/api/health
```

Result:

```text
200
{"success":true,"message":"ok","data":null}
```

Direct host access to `localhost:8080` failed; use `http://localhost:3000/api` from the host, or run commands inside the container.

Connector config returned by:

```bash
curl -sS -b /tmp/onyx-cookie-jar.txt \
  'http://localhost:3000/api/manage/admin/connector?credential=6'
```

Important fields:

```json
{
  "id": 10,
  "name": "Google Drive Test",
  "source": "google_drive",
  "input_type": "poll",
  "credential_ids": [6],
  "connector_specific_config": {
    "include_my_drives": false,
    "include_shared_drives": false,
    "include_files_shared_with_me": false,
    "shared_folder_urls": "https://drive.google.com/drive/u/0/folders/1k0MgWmZ7_HrWmMEa-M37vsqu_QU47vbn"
  }
}
```

## Tested Commands

Authenticate to the local Onyx API without printing credentials:

```bash
ADMIN_EMAIL=$(docker exec onyx-api_server-1 sh -lc 'printf %s "$ADMIN_EMAIL"')
ADMIN_PASSWORD=$(docker exec onyx-api_server-1 sh -lc 'printf %s "$ADMIN_PASSWORD"')

curl -sS -c /tmp/onyx-cookie-jar.txt -b /tmp/onyx-cookie-jar.txt \
  -X POST http://localhost:3000/api/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "username=${ADMIN_EMAIL}" \
  --data-urlencode "password=${ADMIN_PASSWORD}"
```

Login result: HTTP `204`.

Credential listing:

```bash
curl -sS -b /tmp/onyx-cookie-jar.txt \
  http://localhost:3000/api/manage/admin/credential
```

Relevant result:

```json
{"id":6,"name":"Service Account (uploaded)","source":"google_drive","admin_public":true,"curator_public":false}
```

Onyx Google Drive auth check endpoint:

```bash
curl -sS -b /tmp/onyx-cookie-jar.txt \
  http://localhost:3000/api/manage/admin/connector/google-drive/check-auth/6
```

Result:

```json
{"authenticated":false}
```

This did not block indexing. Source inspection in `/app/onyx/server/documents/connector.py` shows this endpoint checks for OAuth token credentials (`DB_CREDENTIALS_DICT_TOKEN_KEY`), so it is not a reliable pass/fail check for the service-account credential path used here.

Trigger a fresh connector run:

```bash
curl -sS -b /tmp/onyx-cookie-jar.txt \
  -H 'Content-Type: application/json' \
  -d '{"connector_id":10,"credential_ids":[6],"from_beginning":false}' \
  http://localhost:3000/api/manage/admin/connector/run-once
```

Result:

```json
{"success":true,"message":"Marked 1 index attempts with indexing triggers.","data":1}
```

Poll the index attempt from Postgres:

```bash
docker exec onyx-relational_db-1 psql -U postgres -d postgres -P pager=off -c \
  "select id, status, time_created, time_started, time_updated,
          total_docs_indexed, new_docs_indexed, total_chunks, error_msg
   from index_attempt
   where connector_credential_pair_id=6
   order by id desc
   limit 5;"
```

Fresh result:

```text
109 | SUCCESS | 2026-04-27 00:29:40.560031+00 | 2026-04-27 00:29:43.037559+00 | 2026-04-27 00:31:06.769468+00 | 1 | 0 | 18 |
106 | SUCCESS | 2026-04-27 00:00:14.481194+00 | 2026-04-27 00:00:17.060264+00 | 2026-04-27 00:01:36.79698+00  | 1 | 1 | 18 |
```

Verify document association:

```bash
docker exec onyx-relational_db-1 psql -U postgres -d postgres -P pager=off -c \
  "select d.id, d.semantic_id, d.link, d.last_synced, d.chunk_count, d.doc_metadata
   from document d
   join document_by_connector_credential_pair m on m.id=d.id
   where m.connector_id=10 and m.credential_id=6;"
```

Result: one Google Drive document, `oai_ai-as-a-scientific-collaborator_jan-2026.pdf`, with `18` chunks.

Verify admin search:

```bash
curl -sS -b /tmp/onyx-cookie-jar.txt \
  -H 'Content-Type: application/json' \
  -d '{"query":"scientific collaborator","filters":{"source_type":["google_drive"]}}' \
  http://localhost:3000/api/admin/search
```

Result: one Google Drive hit for `oai_ai-as-a-scientific-collaborator_jan-2026.pdf`.

Verify user search API:

```bash
curl -sS -b /tmp/onyx-cookie-jar.txt \
  -H 'Content-Type: application/json' \
  -d '{"search_query":"scientific collaborator","filters":{"source_type":["google_drive"]},"num_hits":5,"include_content":false,"stream":false}' \
  http://localhost:3000/api/search/send-search-message
```

Result: `search_docs` included multiple chunks from the same Google Drive PDF and no API error.

Verify chunk content:

```bash
doc='https://drive.google.com/file/d/1FljUfpN2d4O87brUbAxJ2ogs2qdb-02f'
curl -sS -b /tmp/onyx-cookie-jar.txt --get \
  --data-urlencode "document_id=$doc" \
  --data-urlencode 'chunk_id=0' \
  http://localhost:3000/api/document/chunk-info
```

Result: chunk content begins with the PDF title and extracted body text.

## Cleanup Performed

- Removed the local missioncontrol314 service-account key file after upload and successful indexing.
- Removed temporary local API response files and the temporary Onyx auth cookie jar under `/tmp`.
- Confirmed old local duplicate key files are absent:
  - `docs/ops/private/onyx-drive-connector-test.json`
  - `docs/ops/private/onyx-drive-connector-test-euteko-obuv.json`
- Did not delete the active Onyx credential, active Onyx connector, Google Cloud key, or service account, because the connector still depends on them.

## Remaining Issues

- `GET /api/manage/admin/connector` without a credential filter currently fails with a validation error because an older non-Google connector has `input_type = NULL`. Use `GET /api/manage/admin/connector?credential=6` or database queries for this connector until the stale connector is fixed separately.
- `GET /api/manage/admin/connector/google-drive/check-auth/6` returns `authenticated: false`, but the service-account connector still indexes successfully. Treat this endpoint as an OAuth-token check, not as the service-account connector health check.
- `connector_credential_pair.total_docs_indexed` for the Google Drive pair still shows `0` even though index attempts and document mappings show one indexed document. Prefer `index_attempt`, `document_by_connector_credential_pair`, and search verification for now.
- The Google Drive connector is attached to the `AiSci Wiki` document set. Move it to a dedicated Google Drive or project document set if that is not the intended organization.

## Decommission Cleanup

Only run this when the Google Drive connector is no longer needed.

Delete the active Google Cloud key:

```bash
gcloud iam service-accounts keys delete a9288b25ff14c2092712149364893dc0cefcfd3c \
  --iam-account=onyx-drive-connector-test@missioncontrol314.iam.gserviceaccount.com \
  --project=missioncontrol314
```

Delete the service account:

```bash
gcloud iam service-accounts delete onyx-drive-connector-test@missioncontrol314.iam.gserviceaccount.com \
  --project=missioncontrol314
```

## Superseded Test Resources

Earlier local key files from the `euteko` and `euteko-obuv` test projects are no longer present under `docs/ops/private/` and are not the active connector setup.

### Euteko-obuv

- Service account: `onyx-drive-connector-test@euteko-obuv-1750206379826.iam.gserviceaccount.com`
- Former local key file: `docs/ops/private/onyx-drive-connector-test-euteko-obuv.json`
- Key ID: `53e83f01368737025e6f6b324303ef8374dc2d4f`

### Euteko

- Service account: `onyx-drive-connector-test@euteko.iam.gserviceaccount.com`
- Former local key file: `docs/ops/private/onyx-drive-connector-test.json`
- Key ID: `d100dbd8d41415a6c4a09deecbbcd72e5769a88d`

## References

- Onyx Google Drive Service Account: https://docs.onyx.app/admins/connectors/official/google_drive/service_account
- Google Workspace domain-wide delegation: https://support.google.com/a/answer/162106
