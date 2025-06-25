from datetime import datetime
from typing import Optional

import markdown
from sqlmodel import Session, select

from app.core.config import settings
from app.models.post import Post
from app.models.tag import Tag
from app.schemas.post import PostCreate, PostUpdate

# 业务逻辑：获取文章列表
def get_posts_service(
    session: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    categoryId: Optional[int] = None,
    tagId: Optional[int] = None,
    published: Optional[bool] = None,
):
    """获取文章列表业务逻辑"""
    query = select(Post)
    if search:
        query = query.filter(
            Post.title.contains(search) | Post.content_markdown.contains(search)
        )
    if categoryId:
        query = query.filter(Post.category_id == categoryId)
    if tagId:
        query = query.join(Post.tags).filter(Tag.id == tagId)
    if published is not None:
        query = query.filter(Post.published == published)
    total = len(session.exec(query).all())
    query = query.order_by(Post.created_at.desc()).offset(skip).limit(limit)
    posts = session.exec(query).all()
    return total, posts

# 业务逻辑：获取文章详情
def get_post_service(postId: int, session: Session):
    """获取文章详情业务逻辑"""
    return session.get(Post, postId)

# 业务逻辑：创建文章
def create_post_service(post_data: PostCreate, session: Session, user_id: int):
    """创建文章业务逻辑"""
    html_content = markdown.markdown(
        post_data.content_markdown, extensions=settings.MARKDOWN_EXTENSIONS.split(",")
    )
    new_post = Post(
        title=post_data.title,
        content_markdown=post_data.content_markdown,
        content_html=html_content,
        summary=post_data.summary,
        published=post_data.published,
        author_id=user_id,
        category_id=post_data.category_id,
    )
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    if post_data.tag_ids:
        tags = session.exec(select(Tag).where(Tag.id.in_(post_data.tag_ids))).all()
        for tag in tags:
            new_post.tags.append(tag)
        session.commit()
        session.refresh(new_post)
    return new_post

# 业务逻辑：更新文章
def update_post_service(post: Post, post_data: PostUpdate, session: Session):
    """更新文章业务逻辑"""
    if post_data.title:
        post.title = post_data.title
    if post_data.content_markdown:
        post.content_markdown = post_data.content_markdown
        post.content_html = markdown.markdown(
            post_data.content_markdown,
            extensions=settings.MARKDOWN_EXTENSIONS.split(","),
        )
    if post_data.summary is not None:
        post.summary = post_data.summary
    if post_data.published is not None:
        post.published = post_data.published
    if post_data.category_id is not None:
        post.category_id = post_data.category_id
    post.updated_at = datetime.utcnow()
    session.add(post)
    session.commit()
    if post_data.tag_ids is not None:
        post.tags = []
        session.commit()
        if post_data.tag_ids:
            tags = session.exec(select(Tag).where(Tag.id.in_(post_data.tag_ids))).all()
            for tag in tags:
                post.tags.append(tag)
    session.commit()
    session.refresh(post)
    return post

# 业务逻辑：删除文章
def delete_post_service(post: Post, session: Session):
    """删除文章业务逻辑"""
    session.delete(post)
    session.commit() 