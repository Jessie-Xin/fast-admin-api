from datetime import datetime
from typing import List, Optional

import markdown
from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.dependencies import CurrentActiveUser, CurrentAdminUser, SessionDep
from app.models.post import Post
from app.models.tag import Tag
from app.schemas.post import (PostCreate, PostListResponse, PostResponse,
                             PostUpdate)

router = APIRouter(prefix="/api/posts", tags=["posts"])


# 获取文章列表
@router.get("/", response_model=PostListResponse)
async def get_posts(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    tag_id: Optional[int] = None,
    published: Optional[bool] = None
):
    """获取文章列表"""
    query = select(Post)
    
    # 搜索
    if search:
        query = query.filter(Post.title.contains(search) | Post.content_markdown.contains(search))
    
    # 按分类筛选
    if category_id:
        query = query.filter(Post.category_id == category_id)
    
    # 按标签筛选
    if tag_id:
        query = query.join(Post.tags).filter(Tag.id == tag_id)
    
    # 按发布状态筛选
    if published is not None:
        query = query.filter(Post.published == published)
    
    # 查询总数
    total = session.exec(query).count()
    
    # 分页查询结果
    query = query.order_by(Post.created_at.desc()).offset(skip).limit(limit)
    posts = session.exec(query).all()
    
    return PostListResponse(total=total, posts=posts)


# 获取文章详情
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    session: SessionDep
):
    """获取文章详情"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    return post


# 创建文章（需要登录）
@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    session: SessionDep,
    current_user: CurrentActiveUser
):
    """创建文章"""
    # 生成HTML内容
    html_content = markdown.markdown(
        post_data.content_markdown,
        extensions=settings.MARKDOWN_EXTENSIONS.split(",")
    )
    
    # 创建文章
    new_post = Post(
        title=post_data.title,
        content_markdown=post_data.content_markdown,
        content_html=html_content,
        summary=post_data.summary,
        published=post_data.published,
        author_id=current_user.id,
        category_id=post_data.category_id
    )
    
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    
    # 处理标签关系
    if post_data.tag_ids:
        tags = session.exec(select(Tag).where(Tag.id.in_(post_data.tag_ids))).all()
        for tag in tags:
            new_post.tags.append(tag)
        session.commit()
        session.refresh(new_post)
    
    return new_post


# 更新文章（需要作者本人或管理员权限）
@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    session: SessionDep,
    current_user: CurrentActiveUser
):
    """更新文章"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限（作者或管理员）
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此文章"
        )
    
    # 更新标题
    if post_data.title:
        post.title = post_data.title
    
    # 更新内容
    if post_data.content_markdown:
        post.content_markdown = post_data.content_markdown
        post.content_html = markdown.markdown(
            post_data.content_markdown,
            extensions=settings.MARKDOWN_EXTENSIONS.split(",")
        )
    
    # 更新摘要
    if post_data.summary is not None:
        post.summary = post_data.summary
    
    # 更新发布状态
    if post_data.published is not None:
        post.published = post_data.published
    
    # 更新分类
    if post_data.category_id is not None:
        post.category_id = post_data.category_id
    
    # 更新时间
    post.updated_at = datetime.utcnow()
    
    session.add(post)
    session.commit()
    
    # 更新标签关系
    if post_data.tag_ids is not None:
        # 清除现有标签
        post.tags = []
        session.commit()
        
        # 添加新标签
        if post_data.tag_ids:
            tags = session.exec(select(Tag).where(Tag.id.in_(post_data.tag_ids))).all()
            for tag in tags:
                post.tags.append(tag)
    
    session.commit()
    session.refresh(post)
    
    return post


# 删除文章（需要作者本人或管理员权限）
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: SessionDep,
    current_user: CurrentActiveUser
):
    """删除文章"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查权限（作者或管理员）
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此文章"
        )
    
    session.delete(post)
    session.commit() 