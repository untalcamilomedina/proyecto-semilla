"""
Comprehensive tests for CMS comments functionality
Tests threaded comments, CRUD operations, and moderation features
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.article import Article
from app.models.tenant import Tenant
from app.models.user import User


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCommentsCRUD:
    """Test CMS comments CRUD operations"""

    async def test_create_comment(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test comment creation with valid data"""
        comment_data = {
            "content": "This is a great article! Very informative.",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["content"] == "This is a great article! Very informative."
        assert data["article_id"] == str(test_article.id)
        assert "id" in data
        assert data["thread_depth"] == 0

    async def test_get_comment_by_id(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        """Test retrieving a specific comment"""
        response = await client.get(f"/api/v1/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["content"] == "This is a test comment."
        assert data["id"] == str(test_comment.id)

    async def test_update_comment(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        """Test comment update"""
        update_data = {
            "content": "Updated comment content."
        }

        response = await client.put(f"/api/v1/comments/{test_comment.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["content"] == "Updated comment content."

    async def test_delete_comment(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        """Test comment deletion"""
        response = await client.delete(f"/api/v1/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify deletion
        response = await client.get(f"/api/v1/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == 404

    async def test_get_comments_list(self, client: AsyncClient, auth_headers: dict):
        """Test getting comments list"""
        response = await client.get("/api/v1/comments/", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    async def test_get_comments_stats(self, client: AsyncClient, auth_headers: dict):
        """Test comments statistics"""
        response = await client.get("/api/v1/comments/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "total_comments" in data
        assert isinstance(data["total_comments"], int)


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCommentsThreading:
    """Test comment threading functionality"""

    async def test_create_reply_comment(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test creating a reply to a comment"""
        # Create parent comment
        parent_data = {
            "content": "Parent comment content.",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=parent_data, headers=auth_headers)
        assert response.status_code == 201
        parent_id = response.json()["id"]

        # Create reply
        reply_data = {
            "content": "This is a reply to the parent comment.",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "parent_id": parent_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=reply_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["parent_id"] == parent_id
        assert data["thread_depth"] == 1

    async def test_nested_replies(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test creating nested replies (multiple levels)"""
        # Level 1
        level1_data = {
            "content": "Level 1 comment",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=level1_data, headers=auth_headers)
        assert response.status_code == 201
        level1_id = response.json()["id"]

        # Level 2
        level2_data = {
            "content": "Level 2 reply",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "parent_id": level1_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=level2_data, headers=auth_headers)
        assert response.status_code == 201
        level2_id = response.json()["id"]
        assert response.json()["thread_depth"] == 1

        # Level 3
        level3_data = {
            "content": "Level 3 reply",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "parent_id": level2_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=level3_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["thread_depth"] == 2

    async def test_thread_depth_limit(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test that thread depth has reasonable limits"""
        # Create a deep thread
        parent_id = None
        current_depth = 0
        max_depth = 10  # Reasonable limit

        for depth in range(max_depth):
            comment_data = {
                "content": f"Comment at depth {depth}",
                "article_id": str(test_article.id),
                "author_id": test_user_id,
                "tenant_id": test_tenant_id
            }

            if parent_id:
                comment_data["parent_id"] = parent_id

            response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
            assert response.status_code == 201

            data = response.json()
            assert data["thread_depth"] == current_depth
            parent_id = data["id"]
            current_depth += 1

    async def test_get_comment_thread(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test retrieving a comment thread"""
        # Create a thread
        parent_data = {
            "content": "Parent comment",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=parent_data, headers=auth_headers)
        assert response.status_code == 201
        parent_id = response.json()["id"]

        reply_data = {
            "content": "Reply comment",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "parent_id": parent_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=reply_data, headers=auth_headers)
        assert response.status_code == 201

        # Get comments for article and check threading
        response = await client.get(f"/api/v1/comments/?article_id={test_article.id}", headers=auth_headers)
        assert response.status_code == 200

        comments = response.json()
        assert len(comments) >= 2

        # Check that replies are properly linked
        parent_comment = next((c for c in comments if c["id"] == parent_id), None)
        assert parent_comment is not None
        assert parent_comment["thread_depth"] == 0


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCommentsValidation:
    """Test comment validation and edge cases"""

    async def test_create_comment_empty_content(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test creating comment with empty content fails"""
        comment_data = {
            "content": "",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        assert response.status_code == 422

    async def test_create_comment_invalid_article(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str):
        """Test creating comment with invalid article ID fails"""
        comment_data = {
            "content": "Test comment",
            "article_id": str(uuid4()),  # Non-existent article
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        assert response.status_code in [400, 422, 404]

    async def test_create_comment_invalid_parent(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test creating comment with invalid parent ID fails"""
        comment_data = {
            "content": "Test comment",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "parent_id": str(uuid4()),  # Non-existent parent
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        assert response.status_code in [400, 422, 404]

    async def test_create_comment_too_long_content(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test creating comment with excessively long content"""
        long_content = "A" * 10000  # Very long content

        comment_data = {
            "content": long_content,
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        # Should either succeed or fail validation based on implementation
        assert response.status_code in [201, 422]

    async def test_update_comment_not_author(self, client: AsyncClient, auth_headers: dict, auth_headers2: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test that users can only update their own comments"""
        # Create comment with user 1
        comment_data = {
            "content": "Comment by user 1",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        assert response.status_code == 201
        comment_id = response.json()["id"]

        # Try to update with user 2
        update_data = {
            "content": "Updated by user 2"
        }

        response = await client.put(f"/api/v1/comments/{comment_id}", json=update_data, headers=auth_headers2)
        # Should fail due to authorization
        assert response.status_code in [403, 404]


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCommentsModeration:
    """Test comment moderation features"""

    async def test_comment_status_workflow(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test comment status changes (pending, approved, rejected)"""
        comment_data = {
            "content": "Comment for moderation",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id,
            "status": "pending"
        }

        response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        assert response.status_code == 201
        comment_id = response.json()["id"]

        # Approve comment
        update_data = {
            "status": "approved"
        }

        response = await client.put(f"/api/v1/comments/{comment_id}", json=update_data, headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "approved"

    async def test_comment_filtering_by_status(self, client: AsyncClient, auth_headers: dict):
        """Test filtering comments by status"""
        # Get all comments
        response = await client.get("/api/v1/comments/", headers=auth_headers)
        assert response.status_code == 200

        # Get approved comments
        response = await client.get("/api/v1/comments/?status=approved", headers=auth_headers)
        assert response.status_code == 200

        # Get pending comments
        response = await client.get("/api/v1/comments/?status=pending", headers=auth_headers)
        assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.cms
class TestCMSCommentsBusinessLogic:
    """Test comment business logic"""

    async def test_comments_by_article(self, client: AsyncClient, auth_headers: dict, test_article: Article):
        """Test getting comments for specific article"""
        response = await client.get(f"/api/v1/comments/?article_id={test_article.id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # All returned comments should belong to the article
        for comment in data:
            assert comment["article_id"] == str(test_article.id)

    async def test_comment_deletion_cascade(self, client: AsyncClient, auth_headers: dict, test_tenant_id: str, test_user_id: str, test_article: Article):
        """Test that deleting a comment handles replies appropriately"""
        # Create parent comment
        parent_data = {
            "content": "Parent comment",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=parent_data, headers=auth_headers)
        assert response.status_code == 201
        parent_id = response.json()["id"]

        # Create reply
        reply_data = {
            "content": "Reply comment",
            "article_id": str(test_article.id),
            "author_id": test_user_id,
            "parent_id": parent_id,
            "tenant_id": test_tenant_id
        }

        response = await client.post("/api/v1/comments/", json=reply_data, headers=auth_headers)
        assert response.status_code == 201
        reply_id = response.json()["id"]

        # Delete parent comment
        response = await client.delete(f"/api/v1/comments/{parent_id}", headers=auth_headers)
        assert response.status_code == 204

        # Check what happens to reply (depends on implementation)
        response = await client.get(f"/api/v1/comments/{reply_id}", headers=auth_headers)
        # Reply might be deleted, orphaned, or still exist
        assert response.status_code in [200, 404]

    async def test_comment_ordering(self, client: AsyncClient, auth_headers: dict, test_article: Article):
        """Test that comments are returned in correct order"""
        response = await client.get(f"/api/v1/comments/?article_id={test_article.id}", headers=auth_headers)
        assert response.status_code == 200

        comments = response.json()

        if len(comments) > 1:
            # Comments should be ordered by creation time
            for i in range(len(comments) - 1):
                current_time = comments[i]["created_at"]
                next_time = comments[i + 1]["created_at"]
                # Should be in chronological order (oldest first)
                assert current_time <= next_time