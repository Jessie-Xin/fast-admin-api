import pytest
from fastapi import status

def get_auth_headers(client, email, password):
    resp = client.post("/api/auth/token", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

@pytest.fixture
def admin(client):
    admin_data = {
        "username": "tagadmin",
        "email": "tagadmin@example.com",
        "password": "Password123!",
        "is_active": True,
        "is_admin": True,
    }
    client.post("/api/auth/register", json=admin_data)
    return admin_data

def test_create_tag(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    tag_data = {"name": "pytest-tag"}
    resp = client.post("/api/tags/", json=tag_data, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["name"] == "pytest-tag"

def test_get_tag_list(client):
    resp = client.get("/api/tags/")
    assert resp.status_code == status.HTTP_200_OK
    assert "tags" in resp.json()

def test_get_tag_detail(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    tag_data = {"name": "detail-tag"}
    resp = client.post("/api/tags/", json=tag_data, headers=headers)
    tag_id = resp.json()["id"]
    detail_resp = client.get(f"/api/tags/{tag_id}")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["id"] == tag_id

def test_update_tag(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    tag_data = {"name": "update-tag"}
    resp = client.post("/api/tags/", json=tag_data, headers=headers)
    tag_id = resp.json()["id"]
    update_data = {"name": "updated-tag"}
    update_resp = client.put(f"/api/tags/{tag_id}", json=update_data, headers=headers)
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["name"] == "updated-tag"

def test_delete_tag(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    tag_data = {"name": "delete-tag"}
    resp = client.post("/api/tags/", json=tag_data, headers=headers)
    tag_id = resp.json()["id"]
    del_resp = client.delete(f"/api/tags/{tag_id}", headers=headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

def test_tag_unauthorized(client):
    tag_data = {"name": "noauth-tag"}
    resp = client.post("/api/tags/", json=tag_data)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED 