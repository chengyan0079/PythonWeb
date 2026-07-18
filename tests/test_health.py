from app.core.config import settings


def test_health_check(client):
    """GET /api/v1/utils/health-check/ — 健康检查返回 true"""
    response = client.get(f"{settings.API_V1_STR}/utils/health-check/")
    assert response.status_code == 200
    assert response.json() is True


def test_openapi_schema(client):
    """openapi.json 可正常访问并包含关键路径"""
    response = client.get(f"{settings.API_V1_STR}/openapi.json")
    assert response.status_code == 200
    data = response.json()
    paths = data.get("paths", {})
    assert f"{settings.API_V1_STR}/login/access-token" in paths
    assert f"{settings.API_V1_STR}/users/signup" in paths
    assert f"{settings.API_V1_STR}/utils/health-check/" in paths
