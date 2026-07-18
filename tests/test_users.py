import pytest
from app.core.config import settings
from tests.conftest import create_test_user


class TestUserSignup:
    """用户注册接口测试"""

    def test_signup_success(self, client):
        """POST /users/signup — 正常注册成功"""
        import uuid
        email = f"new_{uuid.uuid4().hex[:8]}@test.com"
        response = client.post(
            f"{settings.API_V1_STR}/users/signup",
            json={"email": email, "password": "newpass123", "full_name": "New User"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "id" in data
        assert "hashed_password" not in data

    def test_signup_duplicate_email(self, client):
        """POST /users/signup — 重复邮箱返回 400"""
        response = client.post(
            f"{settings.API_V1_STR}/users/signup",
            json={
                "email": "admin@example.com",
                "password": "somepass123",
            },
        )
        assert response.status_code == 400

    def test_signup_invalid_email(self, client):
        """POST /users/signup — 无效邮箱格式返回 422"""
        response = client.post(
            f"{settings.API_V1_STR}/users/signup",
            json={"email": "not-an-email", "password": "somepass123"},
        )
        assert response.status_code == 422

    def test_signup_short_password(self, client):
        """POST /users/signup — 密码过短返回 422"""
        response = client.post(
            f"{settings.API_V1_STR}/users/signup",
            json={"email": "test@test.com", "password": "short"},
        )
        assert response.status_code == 422

    def test_signup_missing_fields(self, client):
        """POST /users/signup — 缺少必填字段返回 422"""
        response = client.post(
            f"{settings.API_V1_STR}/users/signup",
            json={},
        )
        assert response.status_code == 422


class TestUserMe:
    """当前用户自操作接口测试"""

    def test_read_user_me(self, client, normal_user_headers):
        """GET /users/me — 获取当前用户信息"""
        response = client.get(
            f"{settings.API_V1_STR}/users/me",
            headers=normal_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data
        assert "is_active" in data
        assert "hashed_password" not in data

    def test_read_user_me_no_auth(self, client):
        """GET /users/me — 无认证返回 401"""
        response = client.get(f"{settings.API_V1_STR}/users/me")
        assert response.status_code == 401

    def test_update_user_me(self, client, normal_user_headers):
        """PATCH /users/me — 更新自己的信息"""
        response = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=normal_user_headers,
            json={"full_name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"

    def test_update_user_me_partial(self, client, normal_user_headers):
        """PATCH /users/me — 部分更新姓名（UserUpdateMe 全字段可选）"""
        response = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=normal_user_headers,
            json={"full_name": "Partial Name"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Partial Name"

    def test_update_password_success(self, client, normal_user_headers):
        """PATCH /users/me/password — 修改密码成功"""
        response = client.patch(
            f"{settings.API_V1_STR}/users/me/password",
            headers=normal_user_headers,
            json={
                "current_password": "testpass123",
                "new_password": "newpass456",
            },
        )
        assert response.status_code == 200

    def test_update_password_wrong_current(self, client, normal_user_headers):
        """PATCH /users/me/password — 当前密码错误返回 400"""
        response = client.patch(
            f"{settings.API_V1_STR}/users/me/password",
            headers=normal_user_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpass456",
            },
        )
        assert response.status_code == 400

    def test_delete_user_me_no_superuser(self, client, normal_user_headers):
        """DELETE /users/me — 普通用户删除自己成功"""
        # 创建临时用户来测试删除
        import uuid
        email = f"delme_{uuid.uuid4().hex[:8]}@test.com"
        resp = client.post(
            f"{settings.API_V1_STR}/users/signup",
            json={"email": email, "password": "delpass123", "full_name": "DeleteMe"},
        )
        uid = resp.json()["id"]
        login_resp = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={"username": email, "password": "delpass123"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
        response = client.delete(
            f"{settings.API_V1_STR}/users/me", headers=headers
        )
        assert response.status_code == 200


class TestSuperuserManagement:
    """超级用户管理接口测试"""

    def test_read_users(self, client, superuser_token_headers):
        """GET /users/ — 获取用户列表"""
        response = client.get(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)

    def test_read_users_with_pagination(self, client, superuser_token_headers):
        """GET /users/ — 分页参数"""
        response = client.get(
            f"{settings.API_V1_STR}/users/?skip=0&limit=1",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) <= 1

    def test_read_users_forbidden_for_normal(self, client, normal_user_headers):
        """GET /users/ — 普通用户无权访问"""
        response = client.get(
            f"{settings.API_V1_STR}/users/",
            headers=normal_user_headers,
        )
        assert response.status_code == 403

    def test_create_user_by_admin(self, client, superuser_token_headers):
        """POST /users/ — 管理员创建用户"""
        import uuid
        email = f"admin_created_{uuid.uuid4().hex[:8]}@test.com"
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
            json={
                "email": email,
                "password": "adminpass123",
                "full_name": "Admin Created",
                "is_superuser": False,
            },
        )
        assert response.status_code == 200
        assert response.json()["email"] == email
        assert response.json()["is_superuser"] is False

    def test_get_user_by_id(self, client, superuser_token_headers):
        """GET /users/{id} — 按 ID 获取用户"""
        # 先获取用户列表
        resp = client.get(
            f"{settings.API_V1_STR}/users/?limit=1",
            headers=superuser_token_headers,
        )
        users = resp.json()["data"]
        assert len(users) > 0
        user_id = users[0]["id"]

        response = client.get(
            f"{settings.API_V1_STR}/users/{user_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_get_user_not_found(self, client, superuser_token_headers):
        """GET /users/{id} — 不存在的用户返回 404"""
        response = client.get(
            f"{settings.API_V1_STR}/users/00000000-0000-0000-0000-000000000000",
            headers=superuser_token_headers,
        )
        assert response.status_code == 404

    def test_update_user(self, client, superuser_token_headers):
        """PATCH /users/{id} — 管理员更新用户"""
        user = create_test_user(client, suffix="_update")
        resp = client.get(
            f"{settings.API_V1_STR}/users/?limit=50",
            headers=superuser_token_headers,
        )
        # 从列表中找到我们的用户
        target = None
        for u in resp.json()["data"]:
            if u["email"] == user["email"]:
                target = u
                break
        assert target is not None

        response = client.patch(
            f"{settings.API_V1_STR}/users/{target['id']}",
            headers=superuser_token_headers,
            json={"full_name": "Admin Updated", "is_active": False},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Admin Updated"
        assert response.json()["is_active"] is False

    def test_delete_user(self, client, superuser_token_headers):
        """DELETE /users/{id} — 管理员删除用户"""
        user = create_test_user(client, suffix="_delete")
        resp = client.get(
            f"{settings.API_V1_STR}/users/?limit=50",
            headers=superuser_token_headers,
        )
        target = None
        for u in resp.json()["data"]:
            if u["email"] == user["email"]:
                target = u
                break
        assert target is not None

        response = client.delete(
            f"{settings.API_V1_STR}/users/{target['id']}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200

    def test_delete_superuser_self(self, client, superuser_token_headers):
        """DELETE /users/me — 超级用户不能删除自己"""
        response = client.delete(
            f"{settings.API_V1_STR}/users/me",
            headers=superuser_token_headers,
        )
        assert response.status_code == 403
