from datetime import datetime, timedelta, UTC

from fastapi import status
from sqlmodel import select

from app.core.security import generate_reset_token
from app.models.user import User


def test_request_password_reset_existing_user(client, test_user, session):
    """测试为现有用户请求密码重置"""
    # 准备请求数据
    reset_request = {"email": test_user.email}

    # 发送密码重置请求
    response = client.post("/api/auth/password-reset-request", json=reset_request)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "token" in data  # 注意：实际应用中不应直接返回令牌

    # 验证用户记录更新
    updated_user = session.exec(select(User).where(User.id == test_user.id)).first()
    assert updated_user.reset_token is not None
    assert updated_user.reset_token_expires is not None
    assert updated_user.reset_token_expires > datetime.now(UTC)


def test_request_password_reset_nonexistent_user(client):
    """测试为不存在的用户请求密码重置"""
    # 准备请求数据
    reset_request = {"email": "nonexistent@example.com"}

    # 发送密码重置请求
    response = client.post("/api/auth/password-reset-request", json=reset_request)

    # 验证响应（为防止用户枚举，应该返回相同的成功响应）
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data


def test_reset_password_valid_token(client, test_user, session):
    """测试使用有效令牌重置密码"""
    # 准备测试数据
    reset_token = generate_reset_token()
    test_user.reset_token = reset_token
    test_user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
    session.add(test_user)
    session.commit()

    # 准备请求数据
    reset_data = {"token": reset_token, "new_password": "NewPassword123!"}

    # 发送密码重置请求
    response = client.post("/api/auth/password-reset", json=reset_data)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data

    # 验证用户记录更新
    session.refresh(test_user)
    assert test_user.reset_token is None
    assert test_user.reset_token_expires is None

    # 验证可以使用新密码登录
    login_data = {"username": test_user.email, "password": "NewPassword123!"}
    login_response = client.post("/api/auth/token", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    assert "access_token" in login_response.json()


def test_reset_password_expired_token(client, test_user, session):
    """测试使用过期令牌重置密码"""
    # 准备测试数据
    reset_token = generate_reset_token()
    test_user.reset_token = reset_token
    test_user.reset_token_expires = datetime.now(UTC) - timedelta(hours=1)  # 过期的令牌
    session.add(test_user)
    session.commit()

    # 准备请求数据
    reset_data = {"token": reset_token, "new_password": "NewPassword123!"}

    # 发送密码重置请求
    response = client.post("/api/auth/password-reset", json=reset_data)

    # 验证响应为错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "已过期" in response.json()["detail"]


def test_reset_password_invalid_token(client):
    """测试使用无效令牌重置密码"""
    # 准备请求数据
    reset_data = {"token": "invalid_token", "new_password": "NewPassword123!"}

    # 发送密码重置请求
    response = client.post("/api/auth/password-reset", json=reset_data)

    # 验证响应为错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "无效" in response.json()["detail"]


def test_reset_password_weak_password(client, test_user, session):
    """测试使用弱密码重置密码"""
    # 准备测试数据
    reset_token = generate_reset_token()
    test_user.reset_token = reset_token
    test_user.reset_token_expires = datetime.now(UTC) + timedelta(hours=1)
    session.add(test_user)
    session.commit()

    # 准备请求数据（弱密码）
    reset_data = {"token": reset_token, "new_password": "weak"}

    # 发送密码重置请求
    response = client.post("/api/auth/password-reset", json=reset_data)

    # 验证响应为错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "密码不符合安全要求" in response.json()["detail"]


def test_change_password(client, test_user, session):
    """测试已登录用户修改密码"""
    # 先登录获取令牌
    login_data = {
        "username": test_user.email,
        "password": "password",  # 对应测试用户的哈希密码
    }
    login_response = client.post("/api/auth/token", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 准备密码修改数据
    change_data = {"current_password": "password", "new_password": "NewPassword123!"}

    # 发送密码修改请求
    response = client.post(
        "/api/auth/change-password", json=change_data, headers=headers
    )

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

    # 验证可以使用新密码登录
    new_login_data = {"username": test_user.email, "password": "NewPassword123!"}
    new_login_response = client.post("/api/auth/token", data=new_login_data)
    assert new_login_response.status_code == status.HTTP_200_OK
    assert "access_token" in new_login_response.json()


def test_change_password_wrong_current(client, test_user, session):
    """测试使用错误的当前密码修改密码"""
    # 先登录获取令牌
    login_data = {
        "username": test_user.email,
        "password": "password",  # 对应测试用户的哈希密码
    }
    login_response = client.post("/api/auth/token", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 准备密码修改数据（错误的当前密码）
    change_data = {
        "current_password": "wrong_password",
        "new_password": "NewPassword123!",
    }

    # 发送密码修改请求
    response = client.post(
        "/api/auth/change-password", json=change_data, headers=headers
    )

    # 验证响应为错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "当前密码不正确" in response.json()["detail"]
