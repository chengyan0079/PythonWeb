import pytest
from app.core.config import settings
from tests.conftest import create_test_user, SUPERUSER_EMAIL, SUPERUSER_PASSWORD


class TestItemsCreate:
    """Item 创建接口测试"""

    def test_create_item(self, client, normal_user_headers):
        """POST /items/ — 创建 item 成功"""
        response = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "Test Item", "description": "A test item"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Item"
        assert data["description"] == "A test item"
        assert "id" in data
        assert "owner_id" in data
        assert "created_at" in data

    def test_create_item_no_auth(self, client):
        """POST /items/ — 无认证返回 401"""
        response = client.post(
            f"{settings.API_V1_STR}/items/",
            json={"title": "No Auth"},
        )
        assert response.status_code == 401

    def test_create_item_empty_title(self, client, normal_user_headers):
        """POST /items/ — 空标题返回 422"""
        response = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": ""},
        )
        assert response.status_code == 422

    def test_create_item_title_too_long(self, client, normal_user_headers):
        """POST /items/ — 标题过长返回 422"""
        response = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "x" * 256},
        )
        assert response.status_code == 422


class TestItemsRead:
    """Item 读取接口测试"""

    def test_read_items(self, client, normal_user_headers):
        """GET /items/ — 获取自己的 items"""
        # 先创建几个 items
        client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "Item 1"},
        )
        client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "Item 2"},
        )

        response = client.get(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)

    def test_read_items_with_pagination(self, client, normal_user_headers):
        """GET /items/ — 分页参数"""
        response = client.get(
            f"{settings.API_V1_STR}/items/?skip=0&limit=1",
            headers=normal_user_headers,
        )
        assert response.status_code == 200
        assert len(response.json()["data"]) <= 1

    def test_read_items_no_auth(self, client):
        """GET /items/ — 无认证返回 401"""
        response = client.get(f"{settings.API_V1_STR}/items/")
        assert response.status_code == 401

    def test_read_item_by_id(self, client, normal_user_headers):
        """GET /items/{id} — 按 ID 获取自己的 item"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "Specific Item"},
        )
        item_id = create_resp.json()["id"]

        response = client.get(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=normal_user_headers,
        )
        assert response.status_code == 200
        assert response.json()["id"] == item_id
        assert response.json()["title"] == "Specific Item"

    def test_read_item_not_found(self, client, normal_user_headers):
        """GET /items/{id} — 不存在的 item 返回 404"""
        response = client.get(
            f"{settings.API_V1_STR}/items/00000000-0000-0000-0000-000000000000",
            headers=normal_user_headers,
        )
        assert response.status_code == 404

    def test_read_other_user_item_as_normal(self, client):
        """GET /items/{id} — 普通用户不能查看别人的 item"""
        # 用户A创建 item
        user_a = create_test_user(client, suffix="_a")
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=user_a["headers"],
            json={"title": "User A Item"},
        )
        item_id = create_resp.json()["id"]

        # 用户B尝试获取
        user_b = create_test_user(client, suffix="_b")
        response = client.get(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=user_b["headers"],
        )
        # item route 对非所有者且非 superuser 返回 403
        assert response.status_code == 403

    def test_read_other_user_item_as_superuser(self, client, superuser_token_headers, normal_user_headers):
        """GET /items/{id} — 超级用户可以查看任何 item"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "Anyone Item"},
        )
        item_id = create_resp.json()["id"]

        response = client.get(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Anyone Item"


class TestItemsUpdate:
    """Item 更新接口测试"""

    def test_update_item(self, client, normal_user_headers):
        """PUT /items/{id} — 更新自己的 item"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "Old Title", "description": "Old Desc"},
        )
        item_id = create_resp.json()["id"]

        response = client.put(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=normal_user_headers,
            json={"title": "New Title", "description": "New Desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "New Desc"

    def test_update_item_partial(self, client, normal_user_headers):
        """PUT /items/{id} — 部分更新"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "Partial"},
        )
        item_id = create_resp.json()["id"]

        response = client.put(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=normal_user_headers,
            json={"description": "Only desc"},
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Only desc"

    def test_update_other_user_item(self, client, normal_user_headers):
        """PUT /items/{id} — 不能更新别人的 item"""
        user_a = create_test_user(client, suffix="_update_a")
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=user_a["headers"],
            json={"title": "User A Item"},
        )
        item_id = create_resp.json()["id"]

        user_b = create_test_user(client, suffix="_update_b")
        response = client.put(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=user_b["headers"],
            json={"title": "Hacked"},
        )
        assert response.status_code == 403


class TestItemsDelete:
    """Item 删除接口测试"""

    def test_delete_item(self, client, normal_user_headers):
        """DELETE /items/{id} — 删除自己的 item"""
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_headers,
            json={"title": "To Delete"},
        )
        item_id = create_resp.json()["id"]

        response = client.delete(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=normal_user_headers,
        )
        assert response.status_code == 200

        # 确认已删除
        get_resp = client.get(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=normal_user_headers,
        )
        assert get_resp.status_code == 404

    def test_delete_item_not_found(self, client, normal_user_headers):
        """DELETE /items/{id} — 删除不存在的 item 返回 404"""
        response = client.delete(
            f"{settings.API_V1_STR}/items/00000000-0000-0000-0000-000000000000",
            headers=normal_user_headers,
        )
        assert response.status_code == 404

    def test_delete_other_user_item(self, client):
        """DELETE /items/{id} — 不能删除别人的 item"""
        user_a = create_test_user(client, suffix="_del_a")
        create_resp = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=user_a["headers"],
            json={"title": "User A Item"},
        )
        item_id = create_resp.json()["id"]

        user_b = create_test_user(client, suffix="_del_b")
        response = client.delete(
            f"{settings.API_V1_STR}/items/{item_id}",
            headers=user_b["headers"],
        )
        assert response.status_code == 403

    def test_read_items_as_superuser(self, client, superuser_token_headers):
        """GET /items/ — 超级用户可以看到所有 items"""
        response = client.get(
            f"{settings.API_V1_STR}/items/",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json()["data"], list)
