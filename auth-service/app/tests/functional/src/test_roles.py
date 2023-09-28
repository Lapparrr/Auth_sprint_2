import pytest

from src.models.role import Role


@pytest.mark.asyncio
async def test_post_role(make_post_request, make_get_request, make_role):
    await make_post_request('/api/v1/role/create', make_role)
    role_raw = await make_get_request('/api/v1/role/list', {})
    roles = [Role(**data) for data in role_raw]
    new_role = Role(**make_role)
    assert new_role in roles
