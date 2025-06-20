from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from app.core.dependencies import CurrentActiveUser, CurrentAdminUser, SessionDep
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import (CommentCreate, CommentListResponse,
                               CommentResponse, CommentUpdate)

router = APIRouter(prefix="/api/comments", tags=["comments"])


# 获取评论列表
@router.get("/", response_model=CommentListResponse)
async def get_comments(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    post_id: int = None
):
    """获取评论列表，可按文章ID筛选"""
    query = select(Comment)
    
    # 按文章筛选
    if post_id:
        query = query.filter(Comment.post_id == post_id)
    
    # 查询总数
    total = session.exec(query).count()
    
    # 分页查询结果
    query = query.order_by(Comment.created_at.desc()).offset(skip).limit(limit)
    comments = session.exec(query).all()
    
    return CommentListResponse(total=total, comments=comments)


# 获取评论详情
@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    session: SessionDep
):
    """获取评论详情"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    return comment


# 创建评论（需要登录）
@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    session: SessionDep,
    current_user: CurrentActiveUser
):
    """创建评论"""
    # 检查文章是否存在
    post = session.get(Post, comment_data.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 创建评论
    new_comment = Comment(
        content=comment_data.content,
        author_id=current_user.id,
        post_id=comment_data.post_id
    )
    
    session.add(new_comment)
    session.commit()
    session.refresh(new_comment)
    
    return new_comment


# 更新评论（作者本人或管理员）
@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    session: SessionDep,
    current_user: CurrentActiveUser
):
    """更新评论"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限（作者或管理员）
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此评论"
        )
    
    # 更新内容
    comment.content = comment_data.content
    
    # 更新时间
    comment.updated_at = datetime.utcnow()
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return comment


# 删除评论（作者本人或管理员）
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    session: SessionDep,
    current_user: CurrentActiveUser
):
    """删除评论"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 检查权限（作者或管理员）
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此评论"
        )
    
    session.delete(comment)
    session.commit() 