import pytest
from fastapi import status

def get_auth_headers(client, email, password):
    resp = client.post("/api/auth/token", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

@pytest.fixture
def user(client):
    user_data = {
        "username": "commentuser",
        "email": "commentuser@example.com",
        "password": "Password123!",
        "is_active": True,
        "is_admin": False,
    }
    client.post("/api/auth/register", json=user_data)
    return user_data

@pytest.fixture
def post_id(client, user):
    headers = get_auth_headers(client, user["email"], user["password"])
    post_data = {
        "title": "Comment Post",
        "content_markdown": "content",
        "summary": "for comment",
        "published": True,
        "category_id": None,
        "tag_ids": [],
    }
    resp = client.post("/api/posts/", json=post_data, headers=headers)
    return resp.json()["id"]

def test_create_comment(client, user, post_id):
    headers = get_auth_headers(client, user["email"], user["password"])
    comment_data = {"content": "Nice post!", "post_id": post_id}
    resp = client.post("/api/comments/", json=comment_data, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["content"] == "Nice post!"

def test_get_comment_list(client, post_id):
    resp = client.get(f"/api/comments/?postId={post_id}")
    assert resp.status_code == status.HTTP_200_OK
    assert "comments" in resp.json()

def test_get_comment_detail(client, user, post_id):
    headers = get_auth_headers(client, user["email"], user["password"])
    comment_data = {"content": "Detail comment", "post_id": post_id}
    resp = client.post("/api/comments/", json=comment_data, headers=headers)
    comment_id = resp.json()["id"]
    detail_resp = client.get(f"/api/comments/{comment_id}")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["id"] == comment_id

def test_update_comment(client, user, post_id):
    headers = get_auth_headers(client, user["email"], user["password"])
    comment_data = {"content": "Update comment", "post_id": post_id}
    resp = client.post("/api/comments/", json=comment_data, headers=headers)
    comment_id = resp.json()["id"]
    update_data = {"content": "Updated!"}
    update_resp = client.put(f"/api/comments/{comment_id}", json=update_data, headers=headers)
    assert update_resp.status_code == status.HTTP_200_OK
    assert update_resp.json()["content"] == "Updated!"

def test_delete_comment(client, user, post_id):
    headers = get_auth_headers(client, user["email"], user["password"])
    comment_data = {"content": "Delete comment", "post_id": post_id}
    resp = client.post("/api/comments/", json=comment_data, headers=headers)
    comment_id = resp.json()["id"]
    del_resp = client.delete(f"/api/comments/{comment_id}", headers=headers)
    assert del_resp.status_code == status.HTTP_204_NO_CONTENT

def test_comment_unauthorized(client, post_id):
    comment_data = {"content": "No Auth", "post_id": post_id}
    resp = client.post("/api/comments/", json=comment_data)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED 