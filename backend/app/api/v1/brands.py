import math
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.brand import Brand
from app.models.official_asset import OfficialApp, OfficialSocialAccount
from app.models.user import User
from app.schemas.brand import BrandCreate, BrandDetailResponse, BrandResponse
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.official_asset import (
    OfficialAppCreate,
    OfficialAppResponse,
    OfficialSocialAccountCreate,
    OfficialSocialAccountResponse,
)

router = APIRouter(prefix="/brands", tags=["Brand Profiles & Official Assets"])


async def get_brand_with_ownership_check(
    brand_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> Brand:
    """Helper to verify brand existence and ownership; raises 404 or 403."""
    brand = await db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    if brand.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this brand",
        )
    return brand


# ============================================================================
# Brand Profile Endpoints
# ============================================================================

@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Brand Profile",
    description="Creates a brand profile assigned to the authenticated user.",
)
async def create_brand(
    brand_in: BrandCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Brand:
    name_clean = brand_in.name.strip()
    normalized_name = name_clean.lower()

    brand = Brand(
        id=uuid.uuid4(),
        owner_id=current_user.id,
        name=name_clean,
        normalized_name=normalized_name,
        website=str(brand_in.website).strip() if brand_in.website else None,
        logo_url=str(brand_in.logo_url).strip() if brand_in.logo_url else None,
    )
    db.add(brand)
    try:
        await db.commit()
        await db.refresh(brand)
    except Exception:
        await db.rollback()
        raise
    return brand


@router.get(
    "",
    response_model=PaginatedResponse[BrandResponse],
    summary="List Brand Profiles",
    description="Returns paginated list of brands owned by the authenticated user.",
)
async def list_brands(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[BrandResponse]:
    # Total count
    count_query = select(func.count(Brand.id)).where(Brand.owner_id == current_user.id)
    total_result = await db.execute(count_query)
    total_items = total_result.scalar_one()

    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0

    # Paged query
    items_query = (
        select(Brand)
        .where(Brand.owner_id == current_user.id)
        .order_by(Brand.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    return PaginatedResponse[BrandResponse](
        items=[BrandResponse.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/{brand_id}",
    response_model=BrandDetailResponse,
    summary="Get Brand Profile by ID",
    description="Retrieves a single brand profile with asset summary counts.",
)
async def get_brand(
    brand_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BrandDetailResponse:
    brand = await get_brand_with_ownership_check(brand_id, current_user.id, db)
    return BrandDetailResponse(
        id=brand.id,
        owner_id=brand.owner_id,
        name=brand.name,
        normalized_name=brand.normalized_name,
        website=brand.website,
        logo_url=brand.logo_url,
        logo_phash=brand.logo_phash,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        official_social_count=len(brand.social_accounts),
        official_app_count=len(brand.official_apps),
    )


def is_social_unique_violation(exc: IntegrityError) -> bool:
    """
    Checks if an IntegrityError was caused by uq_official_social_brand_platform_handle.
    Supports asyncpg (PostgreSQL constraint_name attribute) and SQLite fallback.
    """
    orig = getattr(exc, "orig", None)
    if hasattr(orig, "constraint_name") and orig.constraint_name:
        return orig.constraint_name == "uq_official_social_brand_platform_handle"

    err_str = f"{str(orig)} {str(exc)}".lower()
    if "uq_official_social_brand_platform_handle" in err_str:
        return True
    if "unique constraint failed" in err_str and "official_social_accounts" in err_str:
        return True

    return False


# ============================================================================
# Official Social Account Endpoints
# ============================================================================

@router.post(
    "/{brand_id}/social-accounts",
    response_model=OfficialSocialAccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Official Social Account",
    description="Registers an official social media account for brand impersonation exclusion.",
)
async def add_social_account(
    brand_id: uuid.UUID,
    account_in: OfficialSocialAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OfficialSocialAccount:
    await get_brand_with_ownership_check(brand_id, current_user.id, db)

    raw_handle = account_in.raw_handle.strip()
    normalized_handle = raw_handle.lstrip("@").strip().lower()

    # Pre-check for duplicate constraint (brand_id, platform, handle)
    dup_query = select(OfficialSocialAccount.id).where(
        OfficialSocialAccount.brand_id == brand_id,
        OfficialSocialAccount.platform == account_in.platform.value,
        OfficialSocialAccount.handle == normalized_handle,
    )
    dup_result = await db.execute(dup_query)
    if dup_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Official social account already registered for this platform and handle",
        )

    account = OfficialSocialAccount(
        id=uuid.uuid4(),
        brand_id=brand_id,
        platform=account_in.platform.value,
        handle=normalized_handle,
        raw_handle=raw_handle,
        url=str(account_in.url).strip() if account_in.url else None,
        is_verified=account_in.is_verified,
    )
    db.add(account)
    try:
        await db.commit()
        await db.refresh(account)
    except IntegrityError as exc:
        await db.rollback()
        if is_social_unique_violation(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Official social account already registered for this platform and handle",
            )
        raise

    return account


@router.get(
    "/{brand_id}/social-accounts",
    response_model=List[OfficialSocialAccountResponse],
    summary="List Official Social Accounts",
    description="Lists all official social accounts registered for the specified brand.",
)
async def list_social_accounts(
    brand_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OfficialSocialAccount]:
    await get_brand_with_ownership_check(brand_id, current_user.id, db)

    query = (
        select(OfficialSocialAccount)
        .where(OfficialSocialAccount.brand_id == brand_id)
        .order_by(OfficialSocialAccount.created_at.asc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.delete(
    "/{brand_id}/social-accounts/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Official Social Account",
    description="Removes an official social account from the brand profile.",
)
async def delete_social_account(
    brand_id: uuid.UUID,
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await get_brand_with_ownership_check(brand_id, current_user.id, db)

    query = select(OfficialSocialAccount).where(
        OfficialSocialAccount.id == account_id,
        OfficialSocialAccount.brand_id == brand_id,
    )
    result = await db.execute(query)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Official social account not found",
        )

    await db.delete(account)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ============================================================================
# Official Mobile App Endpoints
# ============================================================================

@router.post(
    "/{brand_id}/apps",
    response_model=OfficialAppResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Official Mobile App",
    description="Registers an official mobile app store listing for impersonation exclusion.",
)
async def add_official_app(
    brand_id: uuid.UUID,
    app_in: OfficialAppCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OfficialApp:
    await get_brand_with_ownership_check(brand_id, current_user.id, db)

    package_id = app_in.package_id.strip() if app_in.package_id else None

    app_record = OfficialApp(
        id=uuid.uuid4(),
        brand_id=brand_id,
        name=app_in.name.strip(),
        package_id=package_id,
        developer_name=app_in.developer_name.strip(),
        store=app_in.store.value,
        store_url=str(app_in.store_url).strip() if app_in.store_url else None,
        logo_url=str(app_in.logo_url).strip() if app_in.logo_url else None,
    )
    db.add(app_record)
    try:
        await db.commit()
        await db.refresh(app_record)
    except Exception:
        await db.rollback()
        raise
    return app_record


@router.get(
    "/{brand_id}/apps",
    response_model=List[OfficialAppResponse],
    summary="List Official Mobile Apps",
    description="Lists all official mobile apps registered for the specified brand.",
)
async def list_official_apps(
    brand_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OfficialApp]:
    await get_brand_with_ownership_check(brand_id, current_user.id, db)

    query = (
        select(OfficialApp)
        .where(OfficialApp.brand_id == brand_id)
        .order_by(OfficialApp.created_at.asc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.delete(
    "/{brand_id}/apps/{app_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Official Mobile App",
    description="Removes an official mobile app from the brand profile.",
)
async def delete_official_app(
    brand_id: uuid.UUID,
    app_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await get_brand_with_ownership_check(brand_id, current_user.id, db)

    query = select(OfficialApp).where(
        OfficialApp.id == app_id,
        OfficialApp.brand_id == brand_id,
    )
    result = await db.execute(query)
    app_record = result.scalar_one_or_none()

    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Official app not found",
        )

    await db.delete(app_record)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
