from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import (CurrentActiveUser, SessionDep)
from app.models.post import Post
from app.schemas.post import (PostCreate, PostListResponse, PostResponse,
                              PostUpdate)
from app.services.post_service import (
    get_posts_service,
    get_post_service,
    create_post_service,
    update_post_service,
    delete_post_service,
)

router = APIRouter(prefix="/api/posts", tags=["posts"])


# 获取文章列表
@router.get("/", response_model=PostListResponse)
async def get_posts(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    categoryId: Optional[int] = None,
    tagId: Optional[int] = None,
    published: Optional[bool] = None,
):
    """获取文章列表"""
    total, posts = get_posts_service(
        session=session,
        skip=skip,
        limit=limit,
        search=search,
        categoryId=categoryId,
        tagId=tagId,
        published=published,
    )
    return PostListResponse(total=total, posts=posts)


# 获取文章详情
@router.get("/{postId}", response_model=PostResponse)
async def get_post(postId: int, session: SessionDep):
    """获取文章详情"""
    post = get_post_service(postId, session)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return post


# 创建文章（需要登录）
@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate, session: SessionDep, current_user: CurrentActiveUser
):
    """创建文章"""
    new_post = create_post_service(post_data, session, current_user.id)
    return new_post


# 更新文章（需要作者本人或管理员权限）
@router.put("/{postId}", response_model=PostResponse)
async def update_post(
    postId: int,
    post_data: PostUpdate,
    session: SessionDep,
    current_user: CurrentActiveUser,
):
    """更新文章"""
    post = session.get(Post, postId)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="没有权限更新此文章"
        )
    updated_post = update_post_service(post, post_data, session)
    return updated_post


# 删除文章（需要作者本人或管理员权限）
@router.delete("/{postId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    postId: int, session: SessionDep, current_user: CurrentActiveUser
):
    """删除文章"""
    post = session.get(Post, postId)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="没有权限删除此文章"
        )
    delete_post_service(post, session)
