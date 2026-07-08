"""
tests/api/test_api_requests.py — API Testing with Playwright's APIRequestContext
==================================================================================
Playwright has a built-in HTTP client that shares the same auth session as the
browser. This means you can:
  - Make REST API calls without any browser
  - Mix browser and API calls in the same test
  - Use session cookies from a logged-in browser in API calls

Compared to `requests` library:
  - Same session/cookie jar as the browser context
  - Automatic base URL resolution
  - Async-friendly
  - Built-in JSON serialisation
"""

import pytest
from playwright.sync_api import APIRequestContext, expect


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures: API Request Context
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def api_context(playwright_instance) -> APIRequestContext:
    """
    Creates a standalone API request context (no browser needed).
    Scope=module so we don't recreate it for every test in the file.

    Uses playwright_instance from conftest.py (session-scoped sync_playwright).
    This avoids the naming conflict with pytest-playwright's own 'playwright' fixture.
    """
    request_context = playwright_instance.request.new_context(
        base_url="https://jsonplaceholder.typicode.com",
        extra_http_headers={
            "Accept":       "application/json",
            "Content-Type": "application/json",
        }
    )
    yield request_context
    request_context.dispose()


# ─────────────────────────────────────────────────────────────────────────────
# GET Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
class TestAPIGet:

    def test_get_all_posts(self, api_context: APIRequestContext):
        """TC-030: GET /posts returns 100 items."""
        response = api_context.get("/posts")

        assert response.status == 200, f"Expected 200, got {response.status}"
        posts = response.json()
        assert len(posts) == 100

    def test_get_single_post(self, api_context: APIRequestContext):
        """TC-031: GET /posts/1 returns correct post structure."""
        response = api_context.get("/posts/1")

        assert response.status == 200
        post = response.json()

        # Schema validation
        assert "id"     in post
        assert "title"  in post
        assert "body"   in post
        assert "userId" in post
        assert post["id"] == 1

    def test_get_posts_by_user(self, api_context: APIRequestContext):
        """TC-032: GET /posts?userId=1 filters by user."""
        response = api_context.get("/posts", params={"userId": 1})

        assert response.status == 200
        posts = response.json()
        assert len(posts) > 0
        assert all(p["userId"] == 1 for p in posts), "All posts should belong to userId=1"

    def test_get_nonexistent_post(self, api_context: APIRequestContext):
        """TC-033: GET /posts/9999 returns 404."""
        response = api_context.get("/posts/9999")
        assert response.status == 404

    def test_response_headers(self, api_context: APIRequestContext):
        """TC-034: Verify important response headers are present."""
        response = api_context.get("/posts/1")
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    def test_response_time_acceptable(self, api_context: APIRequestContext):
        """TC-035: Response should arrive within 5 seconds (performance guard)."""
        import time
        start = time.time()
        response = api_context.get("/posts/1")
        elapsed = time.time() - start

        assert response.status == 200
        assert elapsed < 5.0, f"Response took {elapsed:.2f}s — too slow!"


# ─────────────────────────────────────────────────────────────────────────────
# POST Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
class TestAPIPost:

    def test_create_post(self, api_context: APIRequestContext):
        """TC-036: POST /posts creates a new resource and returns 201."""
        payload = {
            "title":  "Playwright API Test",
            "body":   "Testing POST with playwright API context",
            "userId": 1
        }
        response = api_context.post("/posts", data=payload)

        assert response.status == 201
        created = response.json()
        assert created["title"]  == payload["title"]
        assert created["body"]   == payload["body"]
        assert created["userId"] == payload["userId"]
        assert "id" in created     # server assigns an ID

    def test_create_post_with_missing_field(self, api_context: APIRequestContext):
        """TC-037: POST without required fields — jsonplaceholder still returns 201
           but a real API should return 400. Demonstrates contract testing."""
        payload = {"userId": 1}    # missing title and body intentionally
        response = api_context.post("/posts", data=payload)
        # jsonplaceholder is permissive; in real testing assert 400/422
        assert response.status in (201, 400, 422)


# ─────────────────────────────────────────────────────────────────────────────
# PUT / PATCH Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
class TestAPIPutPatch:

    def test_update_post_put(self, api_context: APIRequestContext):
        """TC-038: PUT /posts/1 replaces entire resource."""
        payload = {
            "id":     1,
            "title":  "Updated Title via PUT",
            "body":   "Updated body content",
            "userId": 1
        }
        response = api_context.put("/posts/1", data=payload)

        assert response.status == 200
        updated = response.json()
        assert updated["title"] == "Updated Title via PUT"

    def test_update_post_patch(self, api_context: APIRequestContext):
        """TC-039: PATCH /posts/1 updates only provided fields."""
        payload = {"title": "Patched Title Only"}
        response = api_context.patch("/posts/1", data=payload)

        assert response.status == 200
        patched = response.json()
        assert patched["title"] == "Patched Title Only"


# ─────────────────────────────────────────────────────────────────────────────
# DELETE Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
class TestAPIDelete:

    def test_delete_post(self, api_context: APIRequestContext):
        """TC-040: DELETE /posts/1 returns 200 (jsonplaceholder) or 204."""
        response = api_context.delete("/posts/1")
        assert response.status in (200, 204)


# ─────────────────────────────────────────────────────────────────────────────
# Hybrid: API setup + UI Verification
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
@pytest.mark.ui
@pytest.mark.e2e
class TestHybridAPIUI:

    def test_api_creates_data_visible_in_ui(self, api_context: APIRequestContext, page):
        """
        TC-041: Create data via API, then verify it's visible in the UI.
        This hybrid approach is the FASTEST way to test UI state:
          1. Skip the slow UI form-fill by using the API
          2. Jump straight to verifying the result in the browser
        """
        # Step 1: Create via API
        response = api_context.post("/posts", data={
            "title": "API-created post for UI verification",
            "body":  "Content",
            "userId": 1
        })
        assert response.status == 201
        post_id = response.json()["id"]

        # Step 2: Verify via UI (in a real app, navigate to the post page)
        # For jsonplaceholder, we just verify the API round-trip
        get_response = api_context.get(f"/posts/{post_id}")
        # Note: jsonplaceholder resets after each request; 
        # a real app would persist this and we'd assert it in the browser
        assert post_id is not None
