import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_password_hash
from app.core.validators import validate_password
from app.models.user import User
from app.schemas.auth import (PasswordChange, PasswordReset,
                              PasswordResetRequest, RegisterResponse, Token)
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    login_service,
    create_token_for_user,
    register_user_service,
    password_reset_request_service,
    reset_password_service,
    change_password_service,
    get_user_by_token_service,
)

# 创建日志记录器
logger = logging.getLogger(__name__)

# OAuth2密码Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

router = APIRouter(prefix="/api/auth", tags=["auth"])


# 登录获取token
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="用户名和密码不能为空",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = login_service(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    access_token = create_token_for_user(user)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
    }



# 注册用户
@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate, session: Annotated[Session, Depends(get_session)]
):
    try:
        new_user = register_user_service(user_data, session)
        user_response = UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active,
            is_admin=new_user.is_admin,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at,
        )
        return user_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户注册失败，请重试",
        )


# 注册并直接登录
@router.post("/register-and-login", response_model=RegisterResponse)
async def register_and_login(
    user_data: UserCreate, session: Annotated[Session, Depends(get_session)]
):
    try:
        new_user = register_user_service(user_data, session)
        access_token = create_token_for_user(new_user)
        return {
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "access_token": access_token,
            "token_type": "bearer",
            "created_at": new_user.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"用户注册并登录失败: {e}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户注册并登录失败，请重试",
        )


# 请求密码重置
@router.post("/password-reset-request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    session: Annotated[Session, Depends(get_session)],
):
    return password_reset_request_service(reset_request, session)


# 重置密码
@router.post("/password-reset")
async def reset_password(
    reset_data: PasswordReset, session: Annotated[Session, Depends(get_session)]
):
    try:
        return reset_password_service(reset_data, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# 通过 token 获取当前用户
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
):
    user = get_user_by_token_service(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# 修改密码
@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    try:
        return change_password_service(password_data, current_user, session)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
