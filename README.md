# personal-notes-manager-209712-209724

Backend: Django + DRF

Quickstart:
- Install deps:
  pip install -r notes_backend/requirements.txt

- Apply migrations:
  cd notes_backend
  python manage.py migrate

- Create superuser (optional):
  python manage.py createsuperuser

- Run server (port unchanged by this task, default 8000 unless your environment specifies otherwise):
  python manage.py runserver 0.0.0.0:8000

API:
- Health: GET /api/health/ -> {"status":"ok"}

Auth:
- Signup: POST /api/auth/signup/ with { "username": "...", "password": "...", "email": "..." }
  -> returns {"id": ..., "username": "...", "token": "..."}

- Login: POST /api/auth/login/ with { "username": "...", "password": "..." }
  -> returns {"token": "..."}

Use the token:
- Add header Authorization: Token <token>

Notes:
- List: GET /api/notes/?q=search&is_archived=true|false&page=1&page_size=10
- Create: POST /api/notes/ { "title": "...", "content": "...", "is_archived": false }
- Retrieve: GET /api/notes/{id}/
- Update: PUT/PATCH /api/notes/{id}/
- Delete: DELETE /api/notes/{id}/

Behavior:
- Only authenticated users can access notes.
- Users can only see and modify their own notes.
- Default ordering by updated_at desc.
- Pagination enabled.