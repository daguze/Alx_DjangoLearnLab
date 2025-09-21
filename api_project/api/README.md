Authentication:
- Token authentication is used for API requests
- Obtain a token by POSTing to /api-token-auth/ with username and password
- Include token in headers: Authorization: Token <your_token>

Permissions:
- Public endpoints: No authentication required (marked with AllowAny)
- List view: Anyone can view books list
- Create: Only authenticated users
- Update/Delete: Only object owners or admins
- Special actions: Varying permissions based on endpoint

Endpoints:
- GET /api/books/ - Public (list all books)
- POST /api/books/ - Authenticated users only (create book)
- GET/PUT/PATCH/DELETE /api/books/{id}/ - Owner or admin only
- GET /api/books/public_books/ - Public endpoint
- POST /api/books/{id}/mark_favorite/ - Authenticated users only

Error Responses:
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Valid token but insufficient permissions
- 400 Bad Request: Invalid data
"""