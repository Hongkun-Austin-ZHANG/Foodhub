from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from api.dependencies import (
    get_menu_parser,
    get_themealdb_client,
    get_unknown_dish_resolver,
)
from main import app
from schemas.dish import ExternalDishCandidate, ParsedDish
from schemas.menu import MenuParseResult
from schemas.unknown_dish import (
    FallbackDishBatchRequest,
    FallbackDishBatchResponse,
    UnknownDishAnalysisResponse,
)
from services.database.base import Base
from services.database.session import get_session


class FakeTheMealDBClient:
    async def search_by_name(
        self,
        canonical_name_en: str,
    ) -> list[ExternalDishCandidate]:
        return [
            ExternalDishCandidate(
                external_id="test-1",
                name=canonical_name_en,
                image_url="https://example.com/dish.jpg",
                ingredients=["Chicken", "Peanuts", "Soy Sauce"],
            )
        ]


class EmptyTheMealDBClient:
    async def search_by_name(
        self,
        canonical_name_en: str,
    ) -> list[ExternalDishCandidate]:
        return []


class FakeMenuParser:
    def __init__(self) -> None:
        self.output_languages: list[str] = []
        self.batch_sizes: list[int] = []

    async def parse(
        self,
        image: bytes,
        content_type: str,
        output_language: str = "en",
    ) -> MenuParseResult:
        self.output_languages.append(output_language)
        return MenuParseResult(
            source_language="fr",
            output_language=output_language,
            dishes=[
                ParsedDish(
                    original_name="Le Mystère au Beurre",
                    translated_name="黄油神秘菜",
                    canonical_name_en="Mystery Butter Dish",
                    explicit_ingredients=[],
                    extraction_confidence=0.9,
                )
            ],
        )

    async def parse_many(
        self,
        images: list[tuple[bytes, str]],
        output_language: str = "en",
    ) -> MenuParseResult:
        self.batch_sizes.append(len(images))
        return await self.parse(images[0][0], images[0][1], output_language)


class FakeUnknownDishResolver:
    def __init__(self) -> None:
        self.calls: list[FallbackDishBatchRequest] = []

    async def resolve_batch(
        self,
        request: FallbackDishBatchRequest,
    ) -> FallbackDishBatchResponse:
        self.calls.append(request)
        return FallbackDishBatchResponse(
            batch_id=request.batch_id,
            results=[
                UnknownDishAnalysisResponse(
                    request_id=dish.request_id,
                    canonical_name_en=dish.canonical_name_en,
                    description="A generic butter-based mystery dish.",
                    cuisine=None,
                    inferred_ingredients=[
                        {
                            "name": "Butter",
                            "confidence": 0.8,
                            "reasoning": "Common in the traditional preparation.",
                        }
                    ],
                    overall_confidence=0.8,
                    model_id="fake-b-model",
                )
                for dish in request.dishes
            ],
        )


@pytest_asyncio.fixture
async def api_client() -> AsyncIterator[AsyncClient]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.pop(get_session, None)
    await engine.dispose()


async def register_user(client: AsyncClient) -> dict[str, object]:
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "mao@example.com",
            "username": "mao26",
            "password": "StrongPassword_2026!",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_register_login_and_logout(api_client: AsyncClient) -> None:
    registration = await register_user(api_client)
    token = str(registration["access_token"])
    headers = {"Authorization": f"Bearer {token}"}

    me_response = await api_client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "mao@example.com"

    duplicate_response = await api_client.post(
        "/api/auth/register",
        json={
            "email": "MAO@example.com",
            "username": "another-name",
            "password": "StrongPassword_2026!",
        },
    )
    assert duplicate_response.status_code == 409

    wrong_login = await api_client.post(
        "/api/auth/login",
        json={"identifier": "mao26", "password": "wrong-password"},
    )
    assert wrong_login.status_code == 401

    login_response = await api_client.post(
        "/api/auth/login",
        json={
            "identifier": "MAO@EXAMPLE.COM",
            "password": "StrongPassword_2026!",
        },
    )
    assert login_response.status_code == 200

    logout_response = await api_client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json() == {"logged_out": True}

    expired_me_response = await api_client.get("/api/auth/me", headers=headers)
    assert expired_me_response.status_code == 401


@pytest.mark.asyncio
async def test_frontend_register_and_login_payloads(api_client: AsyncClient) -> None:
    registration = await api_client.post(
        "/api/auth/register",
        json={
            "name": "Mao",
            "email": "frontend@example.com",
            "password": "StrongPassword_2026!",
            "preferred_language": "Chinese",
        },
    )
    assert registration.status_code == 201
    body = registration.json()
    assert body["user"]["username"].startswith("user_")

    headers = {"Authorization": f"Bearer {body['access_token']}"}
    profile = await api_client.get("/api/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["display_name"] == "Mao"
    assert profile.json()["preferred_language"] == "zh"

    login = await api_client.post(
        "/api/auth/login",
        json={
            "email": "frontend@example.com",
            "password": "StrongPassword_2026!",
        },
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_profile_and_preference_crud(api_client: AsyncClient) -> None:
    registration = await register_user(api_client)
    headers = {"Authorization": f"Bearer {registration['access_token']}"}

    profile_response = await api_client.get("/api/profile", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["preferred_language"] == "en"

    updated_profile = await api_client.patch(
        "/api/profile",
        headers=headers,
        json={
            "display_name": "Mao",
            "gender": "prefer_not_to_say",
            "religion": "none",
            "preferred_language": "zh-CN",
            "timezone": "Australia/Sydney",
        },
    )
    assert updated_profile.status_code == 200
    assert updated_profile.json()["display_name"] == "Mao"
    assert updated_profile.json()["timezone"] == "Australia/Sydney"

    created_preference = await api_client.post(
        "/api/preferences",
        headers=headers,
        json={
            "code": "Tree Nuts",
            "kind": "allergy",
            "strength": "hard",
            "enabled": True,
        },
    )
    assert created_preference.status_code == 201
    assert created_preference.json()["code"] == "tree_nuts"

    duplicate_preference = await api_client.post(
        "/api/preferences",
        headers=headers,
        json={
            "code": "tree-nuts",
            "kind": "allergy",
            "strength": "hard",
        },
    )
    assert duplicate_preference.status_code == 409

    preferences = await api_client.get("/api/preferences", headers=headers)
    assert preferences.status_code == 200
    assert len(preferences.json()) == 1

    updated_preference = await api_client.patch(
        "/api/preferences/tree-nuts",
        headers=headers,
        json={"enabled": False},
    )
    assert updated_preference.status_code == 200
    assert updated_preference.json()["enabled"] is False

    deleted = await api_client.delete(
        "/api/preferences/tree_nuts",
        headers=headers,
    )
    assert deleted.status_code == 204

    empty_preferences = await api_client.get("/api/preferences", headers=headers)
    assert empty_preferences.json() == []


@pytest.mark.asyncio
async def test_private_endpoints_require_bearer_token(
    api_client: AsyncClient,
) -> None:
    assert (await api_client.get("/api/auth/me")).status_code == 401
    assert (await api_client.get("/api/profile")).status_code == 401
    assert (await api_client.get("/api/preferences")).status_code == 401
    assert (await api_client.get("/api/preferences/profile")).status_code == 401


@pytest.mark.asyncio
async def test_grouped_preference_profile_accepts_frontend_codes(
    api_client: AsyncClient,
) -> None:
    registration = await register_user(api_client)
    headers = {"Authorization": f"Bearer {registration['access_token']}"}
    payload = {
        "allergies": [
            "peanuts",
            "eggs",
            "sulphites",
            "molluscs",
            "mustard",
            "celery",
        ],
        "dietary_restrictions": ["vegan"],
        "religious_restrictions": ["halal_required"],
        "preferred_proteins": ["chicken"],
        "preferred_flavours": ["savoury"],
        "preferred_textures": ["crispy"],
        "spice_level": "medium",
        "disliked_ingredients": ["mushroom"],
    }

    replaced = await api_client.put(
        "/api/preferences/profile",
        headers=headers,
        json=payload,
    )

    assert replaced.status_code == 200
    body = replaced.json()
    assert body["allergies"] == [
        "celery",
        "egg",
        "molluscs",
        "mustard",
        "peanut",
        "sulfites",
    ]
    assert body["preferred_proteins"] == ["chicken"]
    assert body["spice_level"] == "medium"

    loaded = await api_client.get("/api/preferences/profile", headers=headers)
    assert loaded.status_code == 200
    assert loaded.json() == body

    stored = await api_client.get("/api/preferences", headers=headers)
    stored_by_code = {item["code"]: item for item in stored.json()}
    assert stored_by_code["peanut"]["kind"] == "allergy"
    assert stored_by_code["peanut"]["strength"] == "hard"
    assert stored_by_code["protein_chicken"]["kind"] == "preference"
    assert stored_by_code["mushroom"]["strength"] == "soft"


@pytest.mark.asyncio
async def test_analyze_loads_sql_preferences_and_keeps_evidence_separate(
    api_client: AsyncClient,
) -> None:
    registration = await register_user(api_client)
    headers = {"Authorization": f"Bearer {registration['access_token']}"}
    preference_response = await api_client.post(
        "/api/preferences",
        headers=headers,
        json={
            "code": "peanut",
            "kind": "allergy",
            "strength": "hard",
            "enabled": True,
        },
    )
    assert preference_response.status_code == 201

    async def override_themealdb() -> FakeTheMealDBClient:
        return FakeTheMealDBClient()

    app.dependency_overrides[get_themealdb_client] = override_themealdb
    try:
        response = await api_client.post(
            "/api/recommendation/analyze",
            headers=headers,
            json={
                "menu": {
                    "source_language": "en",
                    "dishes": [
                        {
                            "original_name": "Chicken Satay",
                            "canonical_name_en": "Chicken Satay",
                            "explicit_ingredients": ["Chicken"],
                            "extraction_confidence": 0.95,
                        }
                    ],
                },
                "daily_overrides": [],
            },
        )
    finally:
        app.dependency_overrides.pop(get_themealdb_client, None)

    assert response.status_code == 200
    body = response.json()
    assert body["analysis_complete"] is True
    assert body["effective_preferences"][0]["code"] == "peanut"
    analyzed = body["dishes"][0]
    assert analyzed["resolution_status"] == "themealdb_match"
    assert analyzed["evidence"]["explicit_ingredients"] == ["Chicken"]
    assert analyzed["evidence"]["reference_ingredients"] == [
        "Chicken",
        "Peanuts",
        "Soy Sauce",
    ]
    assert analyzed["evidence"]["inferred_ingredients"] == []
    assessments = {
        item["code"]: item for item in analyzed["evidence"]["allergen_assessments"]
    }
    assert assessments["peanut"] == {
        "code": "peanut",
        "status": "may_contain",
        "evidence_source": "reference_recipe",
        "confidence": 0.7,
        "reasoning": "A generic reference recipe includes: Peanuts",
    }
    assert assessments["soy"]["status"] == "may_contain"
    assert analyzed["decision"]["status"] == "check_with_staff"


@pytest.mark.asyncio
async def test_image_pipeline_uses_profile_language_fallback_and_cache(
    api_client: AsyncClient,
) -> None:
    registration = await register_user(api_client)
    headers = {"Authorization": f"Bearer {registration['access_token']}"}
    profile = await api_client.patch(
        "/api/profile",
        headers=headers,
        json={"preferred_language": "zh"},
    )
    assert profile.status_code == 200
    preference = await api_client.post(
        "/api/preferences",
        headers=headers,
        json={
            "code": "milk",
            "kind": "allergy",
            "strength": "hard",
            "enabled": True,
        },
    )
    assert preference.status_code == 201

    parser = FakeMenuParser()
    fallback = FakeUnknownDishResolver()

    async def override_themealdb() -> EmptyTheMealDBClient:
        return EmptyTheMealDBClient()

    def override_menu_parser() -> FakeMenuParser:
        return parser

    def override_fallback() -> FakeUnknownDishResolver:
        return fallback

    app.dependency_overrides[get_themealdb_client] = override_themealdb
    app.dependency_overrides[get_menu_parser] = override_menu_parser
    app.dependency_overrides[get_unknown_dish_resolver] = override_fallback
    try:
        first = await api_client.post(
            "/api/recommendation/analyze-image",
            headers=headers,
            files={"image": ("menu.png", b"fake-image", "image/png")},
        )
        second = await api_client.post(
            "/api/recommendation/analyze-image",
            headers=headers,
            files={"image": ("menu.png", b"fake-image", "image/png")},
        )
    finally:
        app.dependency_overrides.pop(get_themealdb_client, None)
        app.dependency_overrides.pop(get_menu_parser, None)
        app.dependency_overrides.pop(get_unknown_dish_resolver, None)

    assert first.status_code == 200
    first_body = first.json()
    assert first_body["target_language"] == "zh"
    assert first_body["analysis_complete"] is True
    assert first_body["dishes"][0]["dish"]["translated_name"] == "黄油神秘菜"
    assert first_body["dishes"][0]["resolution_status"] == "llm_fallback"
    assert first_body["dishes"][0]["decision"]["status"] == "check_with_staff"
    assert first_body["fallback_batch_request"] is None
    assert parser.output_languages == ["zh", "zh"]
    assert len(fallback.calls) == 1
    assert second.status_code == 200
    assert second.json()["dishes"][0]["resolution_status"] == "local_fallback"


@pytest.mark.asyncio
async def test_multi_image_scan_is_persisted_and_can_be_ranked(
    api_client: AsyncClient,
) -> None:
    registration = await api_client.post(
        "/api/auth/register",
        json={
            "name": "Mao",
            "email": "scan@example.com",
            "password": "StrongPassword_2026!",
            "preferred_language": "Chinese",
        },
    )
    assert registration.status_code == 201
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    preference = await api_client.post(
        "/api/preferences",
        headers=headers,
        json={
            "code": "milk",
            "kind": "allergy",
            "strength": "hard",
            "enabled": True,
        },
    )
    assert preference.status_code == 201

    parser = FakeMenuParser()
    fallback = FakeUnknownDishResolver()

    async def override_themealdb() -> EmptyTheMealDBClient:
        return EmptyTheMealDBClient()

    app.dependency_overrides[get_themealdb_client] = override_themealdb
    app.dependency_overrides[get_menu_parser] = lambda: parser
    app.dependency_overrides[get_unknown_dish_resolver] = lambda: fallback
    try:
        scan = await api_client.post(
            "/api/menu/scan",
            headers=headers,
            files=[
                ("menu_images", ("page-1.png", b"image-one", "image/png")),
                ("menu_images", ("page-2.jpg", b"image-two", "image/jpeg")),
            ],
        )
        assert scan.status_code == 200
        scan_body = scan.json()
        assert scan_body["target_language"] == "zh"
        assert parser.batch_sizes == [2]

        recommendations = await api_client.post(
            "/api/recommendations",
            headers=headers,
            json={
                "menu_id": scan_body["menu_id"],
                "current_preference": {
                    "preferred_flavours": ["creamy"],
                },
            },
        )
    finally:
        app.dependency_overrides.pop(get_themealdb_client, None)
        app.dependency_overrides.pop(get_menu_parser, None)
        app.dependency_overrides.pop(get_unknown_dish_resolver, None)

    assert recommendations.status_code == 200
    body = recommendations.json()
    assert body["menu_id"] == scan_body["menu_id"]
    assert body["target_language"] == "zh"
    assert body["effective_current_preference"]["preferred_flavours"] == ["creamy"]
    item = body["recommendations"][0]
    assert item["rank"] == 1
    assert item["preference_score"] == 1.0
    assert item["decision"]["status"] == "check_with_staff"
    assert any("风味" in reason for reason in item["decision"]["reasons"])
