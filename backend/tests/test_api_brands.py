import uuid
import pytest
from httpx import AsyncClient

from tests.test_helpers import create_test_es256_jwt


@pytest.fixture
def user_a_id() -> uuid.UUID:
    return uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


@pytest.fixture
def user_b_id() -> uuid.UUID:
    return uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


@pytest.fixture
def auth_headers_user_a(user_a_id) -> dict:
    token = create_test_es256_jwt(user_id=user_a_id, email="user_a@vigilx.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user_b(user_b_id) -> dict:
    token = create_test_es256_jwt(user_id=user_b_id, email="user_b@vigilx.com")
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Brand Profile Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_brand_success(client: AsyncClient, auth_headers_user_a: dict, user_a_id: uuid.UUID):
    payload = {
        "name": "Nike",
        "website": "https://www.nike.com",
        "logo_url": "https://example.com/logo.png",
    }
    response = await client.post("/api/v1/brands", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Nike"
    assert data["normalized_name"] == "nike"
    assert data["website"] == "https://www.nike.com"
    assert data["logo_url"] == "https://example.com/logo.png"
    assert data["owner_id"] == str(user_a_id)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_brand_invalid_input(client: AsyncClient, auth_headers_user_a: dict):
    # Name too short (< 2 chars)
    response = await client.post("/api/v1/brands", json={"name": "N"}, headers=auth_headers_user_a)
    assert response.status_code == 422

    # Missing name
    response = await client.post("/api/v1/brands", json={"website": "https://test.com"}, headers=auth_headers_user_a)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_brand_unauthorized(client: AsyncClient):
    response = await client.post("/api/v1/brands", json={"name": "Acme Corp"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_brands_and_pagination(client: AsyncClient, auth_headers_user_a: dict):
    # Create 3 brands for User A
    for name in ["Brand One", "Brand Two", "Brand Three"]:
        await client.post("/api/v1/brands", json={"name": name}, headers=auth_headers_user_a)

    response = await client.get("/api/v1/brands?page=1&page_size=2", headers=auth_headers_user_a)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 2
    assert data["pagination"]["total_items"] == 3
    assert data["pagination"]["total_pages"] == 2


@pytest.mark.asyncio
async def test_list_brands_user_isolation(
    client: AsyncClient,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict,
):
    await client.post("/api/v1/brands", json={"name": "User A Brand"}, headers=auth_headers_user_a)
    await client.post("/api/v1/brands", json={"name": "User B Brand"}, headers=auth_headers_user_b)

    # User A list
    res_a = await client.get("/api/v1/brands", headers=auth_headers_user_a)
    names_a = [b["name"] for b in res_a.json()["items"]]
    assert "User A Brand" in names_a
    assert "User B Brand" not in names_a

    # User B list
    res_b = await client.get("/api/v1/brands", headers=auth_headers_user_b)
    names_b = [b["name"] for b in res_b.json()["items"]]
    assert "User B Brand" in names_b
    assert "User A Brand" not in names_b


@pytest.mark.asyncio
async def test_get_brand_by_id_success(client: AsyncClient, auth_headers_user_a: dict):
    create_res = await client.post("/api/v1/brands", json={"name": "Target Brand"}, headers=auth_headers_user_a)
    brand_id = create_res.json()["id"]

    get_res = await client.get(f"/api/v1/brands/{brand_id}", headers=auth_headers_user_a)
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == brand_id
    assert data["name"] == "Target Brand"
    assert data["official_social_count"] == 0
    assert data["official_app_count"] == 0


@pytest.mark.asyncio
async def test_get_brand_by_id_not_found(client: AsyncClient, auth_headers_user_a: dict):
    random_id = uuid.uuid4()
    response = await client.get(f"/api/v1/brands/{random_id}", headers=auth_headers_user_a)
    assert response.status_code == 404
    assert response.json()["message"] == "Brand not found"


@pytest.mark.asyncio
async def test_get_brand_by_id_forbidden_cross_user(
    client: AsyncClient,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict,
):
    create_res = await client.post("/api/v1/brands", json={"name": "Private Brand A"}, headers=auth_headers_user_a)
    brand_id = create_res.json()["id"]

    # User B attempts to access User A's brand
    response = await client.get(f"/api/v1/brands/{brand_id}", headers=auth_headers_user_b)
    assert response.status_code == 403
    assert response.json()["message"] == "Not authorized to access this brand"


# ============================================================================
# Official Social Account Tests
# ============================================================================

@pytest.mark.asyncio
async def test_add_social_account_success_and_normalization(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Adidas"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    payload = {
        "platform": "x",
        "raw_handle": "@AdidasOriginals",
        "url": "https://x.com/AdidasOriginals",
        "is_verified": True,
    }
    response = await client.post(f"/api/v1/brands/{brand_id}/social-accounts", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 201
    data = response.json()
    assert data["platform"] == "x"
    assert data["raw_handle"] == "@AdidasOriginals"
    assert data["handle"] == "adidasoriginals"  # Normalized lowercase without @
    assert data["url"] == "https://x.com/AdidasOriginals"
    assert data["is_verified"] is True
    assert data["brand_id"] == brand_id


@pytest.mark.asyncio
async def test_add_social_account_duplicate_conflict(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Puma"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    payload = {
        "platform": "instagram",
        "raw_handle": "@puma",
    }
    res1 = await client.post(f"/api/v1/brands/{brand_id}/social-accounts", json=payload, headers=auth_headers_user_a)
    assert res1.status_code == 201

    # Attempt to post duplicate account (different casing, with/without @)
    dup_payload = {
        "platform": "instagram",
        "raw_handle": "PUMA",
    }
    res2 = await client.post(f"/api/v1/brands/{brand_id}/social-accounts", json=dup_payload, headers=auth_headers_user_a)
    assert res2.status_code == 409
    assert "already registered" in res2.json()["message"]


@pytest.mark.asyncio
async def test_add_social_account_cross_user_forbidden(
    client: AsyncClient,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict,
):
    brand_res = await client.post("/api/v1/brands", json={"name": "Reebok"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    payload = {"platform": "x", "raw_handle": "@reebok"}
    response = await client.post(f"/api/v1/brands/{brand_id}/social-accounts", json=payload, headers=auth_headers_user_b)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_social_account_brand_not_found(client: AsyncClient, auth_headers_user_a: dict):
    random_id = uuid.uuid4()
    payload = {"platform": "x", "raw_handle": "@nobody"}
    response = await client.post(f"/api/v1/brands/{random_id}/social-accounts", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_and_delete_social_account(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Under Armour"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    # Add account
    acc_res = await client.post(
        f"/api/v1/brands/{brand_id}/social-accounts",
        json={"platform": "tiktok", "raw_handle": "@underarmour"},
        headers=auth_headers_user_a,
    )
    acc_id = acc_res.json()["id"]

    # List accounts
    list_res = await client.get(f"/api/v1/brands/{brand_id}/social-accounts", headers=auth_headers_user_a)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Delete account
    del_res = await client.delete(f"/api/v1/brands/{brand_id}/social-accounts/{acc_id}", headers=auth_headers_user_a)
    assert del_res.status_code == 204

    # List again -> 0
    list_res2 = await client.get(f"/api/v1/brands/{brand_id}/social-accounts", headers=auth_headers_user_a)
    assert len(list_res2.json()) == 0


@pytest.mark.asyncio
async def test_delete_social_account_not_found_and_forbidden(
    client: AsyncClient,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict,
):
    brand_res = await client.post("/api/v1/brands", json={"name": "New Balance"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    acc_res = await client.post(
        f"/api/v1/brands/{brand_id}/social-accounts",
        json={"platform": "x", "raw_handle": "@newbalance"},
        headers=auth_headers_user_a,
    )
    acc_id = acc_res.json()["id"]

    # User B forbidden
    res_b = await client.delete(f"/api/v1/brands/{brand_id}/social-accounts/{acc_id}", headers=auth_headers_user_b)
    assert res_b.status_code == 403

    # Delete nonexistent account returns 404
    random_acc_id = uuid.uuid4()
    res_404 = await client.delete(f"/api/v1/brands/{brand_id}/social-accounts/{random_acc_id}", headers=auth_headers_user_a)
    assert res_404.status_code == 404


# ============================================================================
# Official Mobile App Tests
# ============================================================================

@pytest.mark.asyncio
async def test_add_official_app_success(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Asics"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    payload = {
        "name": "ASICS Runkeeper",
        "package_id": "com.fitnesskeeper.runkeeper.pro",
        "developer_name": "ASICS Digital, Inc.",
        "store": "google_play",
        "store_url": "https://play.google.com/store/apps/details?id=com.fitnesskeeper.runkeeper.pro",
    }
    response = await client.post(f"/api/v1/brands/{brand_id}/apps", json=payload, headers=auth_headers_user_a)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ASICS Runkeeper"
    assert data["package_id"] == "com.fitnesskeeper.runkeeper.pro"
    assert data["developer_name"] == "ASICS Digital, Inc."
    assert data["store"] == "google_play"
    assert data["brand_id"] == brand_id


@pytest.mark.asyncio
async def test_add_official_app_validation_errors(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Converse"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    # Invalid store enum
    bad_store_payload = {
        "name": "Converse App",
        "developer_name": "Converse Inc",
        "store": "windows_store",
    }
    res1 = await client.post(f"/api/v1/brands/{brand_id}/apps", json=bad_store_payload, headers=auth_headers_user_a)
    assert res1.status_code == 422

    # Missing developer_name
    no_dev_payload = {
        "name": "Converse App",
        "store": "app_store",
    }
    res2 = await client.post(f"/api/v1/brands/{brand_id}/apps", json=no_dev_payload, headers=auth_headers_user_a)
    assert res2.status_code == 422


@pytest.mark.asyncio
async def test_list_and_delete_official_app(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Vans"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    # Add app
    app_res = await client.post(
        f"/api/v1/brands/{brand_id}/apps",
        json={"name": "Vans Family", "developer_name": "Vans, A VF Company", "store": "app_store"},
        headers=auth_headers_user_a,
    )
    app_id = app_res.json()["id"]

    # List apps
    list_res = await client.get(f"/api/v1/brands/{brand_id}/apps", headers=auth_headers_user_a)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Delete app
    del_res = await client.delete(f"/api/v1/brands/{brand_id}/apps/{app_id}", headers=auth_headers_user_a)
    assert del_res.status_code == 204

    # List apps -> 0
    list_res2 = await client.get(f"/api/v1/brands/{brand_id}/apps", headers=auth_headers_user_a)
    assert len(list_res2.json()) == 0


@pytest.mark.asyncio
async def test_delete_official_app_not_found_and_forbidden(
    client: AsyncClient,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict,
):
    brand_res = await client.post("/api/v1/brands", json={"name": "Fila"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    app_res = await client.post(
        f"/api/v1/brands/{brand_id}/apps",
        json={"name": "Fila Shop", "developer_name": "Fila Korea", "store": "google_play"},
        headers=auth_headers_user_a,
    )
    app_id = app_res.json()["id"]

    # User B cannot delete User A's app
    res_b = await client.delete(f"/api/v1/brands/{brand_id}/apps/{app_id}", headers=auth_headers_user_b)
    assert res_b.status_code == 403

    # Delete nonexistent app returns 404
    random_app_id = uuid.uuid4()
    res_404 = await client.delete(f"/api/v1/brands/{brand_id}/apps/{random_app_id}", headers=auth_headers_user_a)
    assert res_404.status_code == 404


# ============================================================================
# Security & Correctness Regression Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_brand_whitespace_only_rejected(client: AsyncClient, auth_headers_user_a: dict):
    # Whitespace-only names must be rejected with 422
    for blank_name in ["  ", "   ", "\t  \n"]:
        res = await client.post("/api/v1/brands", json={"name": blank_name}, headers=auth_headers_user_a)
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_brand_trimmed_normalization(client: AsyncClient, auth_headers_user_a: dict):
    res = await client.post("/api/v1/brands", json={"name": "  Trimmed Brand  "}, headers=auth_headers_user_a)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Trimmed Brand"
    assert data["normalized_name"] == "trimmed brand"


@pytest.mark.asyncio
async def test_add_social_account_invalid_handles_rejected(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Handle Test Brand"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    for invalid_handle in ["", "   ", "@", "@@@", "  @  "]:
        payload = {"platform": "x", "raw_handle": invalid_handle}
        res = await client.post(f"/api/v1/brands/{brand_id}/social-accounts", json=payload, headers=auth_headers_user_a)
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_add_official_app_whitespace_only_developer_rejected(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "App Test Brand"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    payload = {
        "name": "Legit App",
        "developer_name": "   ",
        "store": "google_play",
    }
    res = await client.post(f"/api/v1/brands/{brand_id}/apps", json=payload, headers=auth_headers_user_a)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_brand_detail_counts_with_assets(client: AsyncClient, auth_headers_user_a: dict):
    brand_res = await client.post("/api/v1/brands", json={"name": "Counted Brand"}, headers=auth_headers_user_a)
    brand_id = brand_res.json()["id"]

    # Initial counts -> 0, 0
    res0 = await client.get(f"/api/v1/brands/{brand_id}", headers=auth_headers_user_a)
    assert res0.json()["official_social_count"] == 0
    assert res0.json()["official_app_count"] == 0

    # Add 1 social account
    await client.post(
        f"/api/v1/brands/{brand_id}/social-accounts",
        json={"platform": "x", "raw_handle": "@CountedOfficial"},
        headers=auth_headers_user_a,
    )

    # Add 1 app
    await client.post(
        f"/api/v1/brands/{brand_id}/apps",
        json={"name": "Counted App", "developer_name": "Counted Corp", "store": "google_play"},
        headers=auth_headers_user_a,
    )

    # Re-query detail
    res1 = await client.get(f"/api/v1/brands/{brand_id}", headers=auth_headers_user_a)
    assert res1.status_code == 200
    assert res1.json()["official_social_count"] == 1
    assert res1.json()["official_app_count"] == 1


@pytest.mark.asyncio
async def test_cross_brand_asset_deletion_not_found(client: AsyncClient, auth_headers_user_a: dict):
    # User A owns Brand 1 and Brand 2
    b1_res = await client.post("/api/v1/brands", json={"name": "User Brand One"}, headers=auth_headers_user_a)
    brand_1_id = b1_res.json()["id"]

    b2_res = await client.post("/api/v1/brands", json={"name": "User Brand Two"}, headers=auth_headers_user_a)
    brand_2_id = b2_res.json()["id"]

    # Add assets to Brand 2
    acc_res = await client.post(
        f"/api/v1/brands/{brand_2_id}/social-accounts",
        json={"platform": "instagram", "raw_handle": "@brand2insta"},
        headers=auth_headers_user_a,
    )
    b2_acc_id = acc_res.json()["id"]

    app_res = await client.post(
        f"/api/v1/brands/{brand_2_id}/apps",
        json={"name": "Brand 2 App", "developer_name": "Brand 2 Dev", "store": "app_store"},
        headers=auth_headers_user_a,
    )
    b2_app_id = app_res.json()["id"]

    # Attempt to delete Brand 2 assets via Brand 1 URL endpoint -> must return 404
    del_acc_res = await client.delete(
        f"/api/v1/brands/{brand_1_id}/social-accounts/{b2_acc_id}",
        headers=auth_headers_user_a,
    )
    assert del_acc_res.status_code == 404
    assert del_acc_res.json()["message"] == "Official social account not found"

    del_app_res = await client.delete(
        f"/api/v1/brands/{brand_1_id}/apps/{b2_app_id}",
        headers=auth_headers_user_a,
    )
    assert del_app_res.status_code == 404
    assert del_app_res.json()["message"] == "Official app not found"


@pytest.mark.asyncio
async def test_list_brands_pagination_invalid_bounds(client: AsyncClient, auth_headers_user_a: dict):
    # page=0 is invalid (< 1)
    res_page_0 = await client.get("/api/v1/brands?page=0", headers=auth_headers_user_a)
    assert res_page_0.status_code == 422

    # page_size=0 is invalid (< 1)
    res_size_0 = await client.get("/api/v1/brands?page_size=0", headers=auth_headers_user_a)
    assert res_size_0.status_code == 422

    # page_size=101 is invalid (> 100)
    res_size_101 = await client.get("/api/v1/brands?page_size=101", headers=auth_headers_user_a)
    assert res_size_101.status_code == 422

