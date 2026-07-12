import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api import app
from database import get_connection

client = TestClient(app)

def test_scite_caching():
    project_id = "robert-boson-manuscript"
    doi = "10.1103/PhysRevLett.111.111111"

    # 1. Clear cache for this DOI
    conn = get_connection(project_id)
    conn.execute("DELETE FROM SciteCache WHERE doi = ?", (doi,))
    conn.commit()
    conn.close()

    # 2. Mock httpx to return a fake response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tallies": {"total": 5}}

    with patch("httpx.AsyncClient.get", return_value=mock_response) as mock_get:
        # Patch OS environment to have API KEY
        with patch.dict("os.environ", {"SCITE_API_KEY": "fake_key"}):
            resp = client.get(f"/api/projects/{project_id}/scite?doi={doi}")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
            assert resp.json()["tally"]["total"] == 5
            mock_get.assert_called_once()

    # 3. Call again, should be cached (mock not called)
    with patch("httpx.AsyncClient.get") as mock_get_cache:
        with patch.dict("os.environ", {"SCITE_API_KEY": "fake_key"}):
            resp = client.get(f"/api/projects/{project_id}/scite?doi={doi}")
            assert resp.status_code == 200
            assert resp.json()["tally"]["total"] == 5
            mock_get_cache.assert_not_called()
