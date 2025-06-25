from fastapi import status

def test_register_user(client):
    """测试用户注册功能"""
    # 准备测试数据
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "Password123!",
        "is_active": True,
        "is_admin": False,
    }

    # 发送注册请求
    response = client.post("/api/auth/register", json=user_data)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK

    # 验证返回的用户数据
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data  # 确保哈希密码不在响应中


def test_register_duplicate_username(client, test_user):
    """测试注册重复用户名"""
    # 准备与已存在用户名相同的用户数据
    user_data = {
        "username": test_user.username,  # 使用已存在的用户名
        "email": "different@example.com",
        "password": "Password123!",
        "is_active": True,
        "is_admin": False,
    }

    # 发送注册请求
    response = client.post("/api/auth/register", json=user_data)

    # 验证响应为错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "用户名已存在" in response.json()["detail"]


def test_register_duplicate_email(client, test_user):
    """测试注册重复邮箱"""
    # 准备与已存在邮箱相同的用户数据
    user_data = {
        "username": "newusername",
        "email": test_user.email,  # 使用已存在的邮箱
        "password": "Password123!",
        "is_active": True,
        "is_admin": False,
    }

    # 发送注册请求
    response = client.post("/api/auth/register", json=user_data)

    # 验证响应为错误
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "邮箱已存在" in response.json()["detail"]


def test_login_success(client, test_user):
    """测试成功登录"""
    # 准备登录数据
    login_data = {
        "username": test_user.email,  # 使用邮箱作为用户名
        "password": "password",  # 对应测试用户的哈希密码
    }

    # 发送登录请求
    response = client.post("/api/auth/token", data=login_data)

    # 验证响应
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """测试密码错误的登录尝试"""
    # 准备错误密码的登录数据
    login_data = {"username": test_user.email, "password": "wrongpassword"}

    # 发送登录请求
    response = client.post("/api/auth/token", data=login_data)

    # 验证响应为未授权
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "邮箱或密码错误" in response.json()["detail"]


def test_login_inactive_user(client, session, test_user):
    """测试已禁用用户的登录尝试"""
    # 将测试用户设置为不活跃
    test_user.is_active = False
    session.add(test_user)
    session.commit()

    # 准备登录数据
    login_data = {"username": test_user.email, "password": "password"}

    # 发送登录请求
    response = client.post("/api/auth/token", data=login_data)

    # 验证响应为禁止访问
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "用户已被禁用" in response.json()["detail"]
