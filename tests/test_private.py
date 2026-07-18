from app.core.config import settings


class TestPrivateRoutes:
    """私有路由接口测试（仅 local 环境可用）"""

    def test_create_user_private(self, client):
        """POST /private/users/ — 直接创建用户（无认证）"""
        import uuid
        email = f"private_{uuid.uuid4().hex[:8]}@test.com"
        response = client.post(
            f"{settings.API_V1_STR}/private/users/",
            json={
                "email": email,
                "password": "private123",
                "full_name": "Private User",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["full_name"] == "Private User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_create_user_private_duplicate(self, client):
        """POST /private/users/ — 重复邮箱直接 raise IntegrityError（未处理异常）"""
        import pytest
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            client.post(
                f"{settings.API_V1_STR}/private/users/",
                json={
                    "email": "admin@example.com",
                    "password": "test123",
                    "full_name": "Duplicate",
                },
            )
