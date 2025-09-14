# Permissions and Groups Setup

## Custom Permissions
Defined in `Book` model:
- `can_view`
- `can_create`
- `can_edit`
- `can_delete`

## Groups
- **Viewers** → `can_view`
- **Editors** → `can_view`, `can_create`, `can_edit`
- **Admins** → all permissions

## Usage in Views
We use `@permission_required("relationship_app.can_edit")` to restrict access.

## How to Setup
Run:
```bash
python manage.py setup_groups
