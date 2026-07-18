import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.main import app

# 已存在的超级用户凭据（由 initial_data.py 创建）
SUPERUSER_EMAIL = "admin@example.com"
SUPERUSER_PASSWORD = "admin123"


@pytest.fixture
def client():
    """FastAPI TestClient，每次测试独立"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    """提供数据库会话用于直接清理数据"""
    with Session(engine) as session:
        yield session


@pytest.fixture
def superuser_token_headers(client):
    """获取超级用户的 Bearer Token headers"""
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": SUPERUSER_EMAIL, "password": SUPERUSER_PASSWORD},
    )
    assert response.status_code == 200, f"Superuser login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def normal_user_headers(client):
    """
    创建普通用户并返回其 Token headers。
    每个测试模块创建一个唯一用户，测试结束后清理。
    """
    import uuid
    test_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
    test_password = "testpass123"
    test_fullname = "Test User"

    response = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json={
            "email": test_email,
            "password": test_password,
            "full_name": test_fullname,
        },
    )
    assert response.status_code == 200, f"Signup failed: {response.json()}"
    user_data = response.json()

    # 登录获取 token
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": test_email, "password": test_password},
    )
    token = response.json()["access_token"]

    yield {"Authorization": f"Bearer {token}"}

    # 清理：用 superuser 删除测试用户
    super_resp = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": SUPERUSER_EMAIL, "password": SUPERUSER_PASSWORD},
    )
    super_headers = {"Authorization": f"Bearer {super_resp.json()['access_token']}"}
    client.delete(
        f"{settings.API_V1_STR}/users/{user_data['id']}",
        headers=super_headers,
    )


def create_test_user(client, suffix="") -> dict:
    """辅助函数：注册并返回用户数据 + token"""
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}{suffix}@test.com"
    password = "testpass123"
    resp = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json={"email": email, "password": password, "full_name": "Test"},
    )
    assert resp.status_code == 200, f"Create user failed: {resp.json()}"
    user = resp.json()
    login_resp = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    token = login_resp.json()["access_token"]
    return {
        "id": user["id"],
        "email": email,
        "password": password,
        "headers": {"Authorization": f"Bearer {token}"},
    }
