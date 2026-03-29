from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_admin, get_db
from src.models.settings import GlobalSetting

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsOut(BaseModel):
    settings: dict[str, str]


class SettingsUpdate(BaseModel):
    settings: dict[str, str]


@router.get("", response_model=SettingsOut)
async def get_settings_api(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(GlobalSetting))
    settings = {s.key: s.value for s in result.scalars().all()}
    return SettingsOut(settings=settings)


@router.put("", response_model=SettingsOut)
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    for key, value in data.settings.items():
        stmt = select(GlobalSetting).where(GlobalSetting.key == key)
        result = await db.execute(stmt)
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            db.add(GlobalSetting(key=key, value=value))

    await db.commit()

    result = await db.execute(select(GlobalSetting))
    settings = {s.key: s.value for s in result.scalars().all()}
    return SettingsOut(settings=settings)
