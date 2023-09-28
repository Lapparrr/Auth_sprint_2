import pytest


@pytest.mark.asyncio
async def test_post_user(make_post_request, make_get_request, make_user):
    response = await make_post_request(f'/api/v1/auth/signup', make_user)
    new_user = await make_get_request(f'/api/v1/user/', {"user_id": response["id"]})
    assert new_user["email"] == make_user["email"]
    assert new_user["login"] == make_user["login"]
    assert new_user["first_name"] == make_user["first_name"]
    assert new_user["last_name"] == make_user["last_name"]
