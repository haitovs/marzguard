from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_admin, get_db
from src.models.policy import Policy
from src.models.user import UserIPConfig
from src.schemas.policy import PolicyBatchAssign, PolicyCreate, PolicyOut, PolicyUpdate

router = APIRouter(prefix="/policies", tags=["policies"])


async def _policy_to_out(policy: Policy, db: AsyncSession) -> PolicyOut:
    count_stmt = (
        select(func.count())
        .select_from(UserIPConfig)
        .where(UserIPConfig.policy_id == policy.id)
    )
    result = await db.execute(count_stmt)
    user_count = result.scalar() or 0

    return PolicyOut(
        id=policy.id,
        name=policy.name,
        default_ip_limit=policy.default_ip_limit,
        auto_reenable=policy.auto_reenable,
        reenable_delay_sec=policy.reenable_delay_sec,
        notify_on_violation=policy.notify_on_violation,
        created_at=policy.created_at,
        user_count=user_count,
    )


@router.get("", response_model=list[PolicyOut])
async def list_policies(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Policy))
    policies = result.scalars().all()
    return [await _policy_to_out(p, db) for p in policies]


@router.post("", response_model=PolicyOut, status_code=201)
async def create_policy(
    data: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    existing = await db.execute(select(Policy).where(Policy.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Policy name already exists")

    policy = Policy(**data.model_dump())
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    return await _policy_to_out(policy, db)


@router.get("/{policy_id}", response_model=PolicyOut)
async def get_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return await _policy_to_out(policy, db)


@router.put("/{policy_id}", response_model=PolicyOut)
async def update_policy(
    policy_id: int,
    data: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(policy, key, value)

    await db.commit()
    await db.refresh(policy)
    return await _policy_to_out(policy, db)


@router.delete("/{policy_id}")
async def delete_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Policy).where(Policy.id == policy_id))
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    await db.delete(policy)
    await db.commit()
    return {"status": "deleted", "id": policy_id}


@router.post("/batch-assign")
async def batch_assign_policy(
    data: PolicyBatchAssign,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Policy).where(Policy.id == data.policy_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Policy not found")

    updated = 0
    for username in data.usernames:
        stmt = select(UserIPConfig).where(UserIPConfig.username == username)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        if config:
            config.policy_id = data.policy_id
            updated += 1

    await db.commit()
    return {"updated": updated, "total": len(data.usernames)}
