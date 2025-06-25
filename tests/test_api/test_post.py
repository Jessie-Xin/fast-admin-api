import pytest
from fastapi import status

def get_auth_headers(client, email, password):
    resp = client.post("/api/auth/token", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

@pytest.fixture
def user(client):
    user_data = {
        "username": "postuser",
        "email": "postuser@example.com",
        "password": "Password123!",
        "is_active": True,
        "is_admin": False,
    }
    client.post("/api/auth/register", json=user_data)
    return user_data

@pytest.fixture
def admin(client):
    admin_data = {
        "username": "adminuser",
        "email": "adminuser@example.com",
        "password": "Password123!",
        "is_active": True,
        "is_admin": True,
    }
    client.post("/api/auth/register", json=admin_data)
    return admin_data

def test_create_post(client, user):
    headers = get_auth_headers(client, user["email"], user["password"])
    post_data = {
        "title": "Test Post",
        "content_markdown": "# Hello World",
        "summary": "A test post",
        "published": True,
        "category_id": None,
        "tag_ids": [],
    }
    resp = client.post("/api/posts/", json=post_data, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["title"] == "Test Post"

def test_get_post_list(client):
    resp = client.get("/api/posts/")
    assert resp.status_code == status.HTTP_200_OK
    assert "posts" in resp.json()

def test_get_post_detail(client, user):
    headers = get_auth_headers(client, user["email"], user["password"])
    post_data = {
        "title": "Detail Post",
        "content_markdown": "content",
        "summary": "detail",
        "published": True,
        "category_id": None,
        "tag_ids": [],
    }
    resp = client.post("/api/posts/", json=post_data, headers=headers)
    post_id = resp.json()["id"]
    detail_resp = client.get(f"/api/posts/{post_id}")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["id"] == post_id

def test_update_post(client, user):
    headers = get_auth_headers(client, user["email"], user["password"])
    post_data = {
        "title": "Update Post",
        "content_markdown": "content",
        "summary": "update",
        "published": True,
        "category_id": None,
        "tag_ids": [],
    }
    resp = client.post("/api/posts/", json=post_data, headers=headers)
    post_id = resp.json()["id"]
    update_data = {"title": "Updated Title"}
    update_resp = client.put(f"/api/posts/{post_id}", json=update_data, headers=headers)
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["title"] == "Updated Title"

def test_delete_post(client, user):
    headers = get_auth_headers(client, user["email"], user["password"])
    post_data = {
        "title": "Delete Post",
        "content_markdown": "content",
        "summary": "delete",
        "published": True,
        "category_id": None,
        "tag_ids": [],
    }
    resp = client.post("/api/posts/", json=post_data, headers=headers)
    post_id = resp.json()["id"]
    del_resp = client.delete(f"/api/posts/{post_id}", headers=headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

def test_post_permission(client, user, admin):
    # 普通用户创建
    headers = get_auth_headers(client, user["email"], user["password"])
    post_data = {
        "title": "Perm Post",
        "content_markdown": "content",
        "summary": "perm",
        "published": True,
        "category_id": None,
        "tag_ids": [],
    }
    resp = client.post("/api/posts/", json=post_data, headers=headers)
    post_id = resp.json()["id"]
    # 另一个用户尝试删除
    admin_headers = get_auth_headers(client, admin["email"], admin["password"])
    del_resp = client.delete(f"/api/posts/{post_id}", headers=admin_headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

def test_post_unauthorized(client):
    post_data = {
        "title": "No Auth",
        "content_markdown": "content",
        "summary": "noauth",
        "published": True,
        "category_id": None,
        "tag_ids": [],
    }
    resp = client.post("/api/posts/", json=post_data)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED 