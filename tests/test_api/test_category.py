import pytest
from fastapi import status

def get_auth_headers(client, email, password):
    resp = client.post("/api/auth/token", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

@pytest.fixture
def admin(client):
    admin_data = {
        "username": "catadmin",
        "email": "catadmin@example.com",
        "password": "Password123!",
        "is_active": True,
        "is_admin": True,
    }
    client.post("/api/auth/register", json=admin_data)
    return admin_data

def test_create_category(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    cat_data = {"name": "pytest-cat", "description": "desc"}
    resp = client.post("/api/categories/", json=cat_data, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["name"] == "pytest-cat"

def test_get_category_list(client):
    resp = client.get("/api/categories/")
    assert resp.status_code == status.HTTP_200_OK
    assert "categories" in resp.json()

def test_get_category_detail(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    cat_data = {"name": "detail-cat", "description": "desc"}
    resp = client.post("/api/categories/", json=cat_data, headers=headers)
    cat_id = resp.json()["id"]
    detail_resp = client.get(f"/api/categories/{cat_id}")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["id"] == cat_id

def test_update_category(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    cat_data = {"name": "update-cat", "description": "desc"}
    resp = client.post("/api/categories/", json=cat_data, headers=headers)
    cat_id = resp.json()["id"]
    update_data = {"name": "updated-cat"}
    update_resp = client.put(f"/api/categories/{cat_id}", json=update_data, headers=headers)
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["name"] == "updated-cat"

def test_delete_category(client, admin):
    headers = get_auth_headers(client, admin["email"], admin["password"])
    cat_data = {"name": "delete-cat", "description": "desc"}
    resp = client.post("/api/categories/", json=cat_data, headers=headers)
    cat_id = resp.json()["id"]
    del_resp = client.delete(f"/api/categories/{cat_id}", headers=headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

def test_category_unauthorized(client):
    cat_data = {"name": "noauth-cat", "description": "desc"}
    resp = client.post("/api/categories/", json=cat_data)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED 