from fastapi import APIRouter

from app.core.dependencies import (CurrentActiveUser, SessionDep)
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# 获取仪表盘摘要数据
@router.get("/summary", response_model=DashboardSummary)
async def get_summary(session: SessionDep, current_user: CurrentActiveUser):
    """获取仪表盘摘要数据"""
    return get_dashboard_summary_service(session)
