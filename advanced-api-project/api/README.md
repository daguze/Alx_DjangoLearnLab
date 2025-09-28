## Book API — Generic Views

- **GET /api/books/** → `BookListView` (ListAPIView): public read, supports `?search=`, `?ordering=`, `?author=`, `?year=`.
- **GET /api/books/<pk>/** → `BookDetailView` (RetrieveAPIView): public read.
- **POST /api/books/create/** → `BookCreateView` (CreateAPIView): authenticated; `perform_create` hook.
- **PATCH/PUT /api/books/<pk>/update/** → `BookUpdateView` (UpdateAPIView): authenticated; `perform_update` hook.
- **DELETE /api/books/<pk>/delete/** → `BookDeleteView` (DestroyAPIView): authenticated.

### Permissions
- Read: `AllowAny` for list/detail.
- Write: `IsAuthenticated` (optionally staff-only inside hooks).
- Alternative: `IsAuthenticatedOrReadOnly` across all views.

### Validation
- `BookSerializer` rejects `publication_year` in the future.

### Filters
- Query params: `?search=<text>`, `?ordering=publication_year|title|id`, `?author=<id>`, `?year=<int>`.
