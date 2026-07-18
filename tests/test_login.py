from app.core.config import settings


class TestLogin:
    """登录相关接口测试"""

    def test_access_token_success(self, client):
        """POST /login/access-token — 正确凭据登录成功"""
        response = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={"username": "admin@example.com", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_access_token_wrong_password(self, client):
        """POST /login/access-token — 错误密码返回 400"""
        response = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={"username": "admin@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 400
        assert "Incorrect email or password" in response.json()["detail"]

    def test_access_token_nonexistent_user(self, client):
        """POST /login/access-token — 不存在用户返回 400"""
        response = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={"username": "noone@example.com", "password": "whatever123"},
        )
        assert response.status_code == 400
        assert "Incorrect email or password" in response.json()["detail"]

    def test_access_token_missing_fields(self, client):
        """POST /login/access-token — 缺少字段返回 422"""
        response = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={},
        )
        assert response.status_code == 422

    def test_test_token_valid(self, client, superuser_token_headers):
        """POST /login/test-token — 有效 token 返回用户信息"""
        response = client.post(
            f"{settings.API_V1_STR}/login/test-token",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@example.com"
        assert data["is_superuser"] is True

    def test_test_token_no_auth(self, client):
        """POST /login/test-token — 无 token 返回 401"""
        response = client.post(f"{settings.API_V1_STR}/login/test-token")
        assert response.status_code == 401

    def test_test_token_invalid(self, client):
        """POST /login/test-token — 无效 token 返回 403"""
        response = client.post(
            f"{settings.API_V1_STR}/login/test-token",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert response.status_code == 403

    def test_password_recovery_nonexistent(self, client):
        """POST /password-recovery/{email} — 不存在的邮箱不发送邮件"""
        response = client.post(
            f"{settings.API_V1_STR}/password-recovery/noone@test.com"
        )
        # 即使邮箱不存在也返回 200（防止邮箱枚举攻击）
        assert response.status_code == 200

    def test_reset_password_invalid_token(self, client):
        """POST /reset-password/ — 无效 token 返回 400"""
        response = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            json={"token": "invalid", "new_password": "newpass123"},
        )
        assert response.status_code == 400
