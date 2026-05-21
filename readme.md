# Circlo

Circlo is a project designed to manage and facilitate community interactions and posts. This application provides a structured way to handle user authentication, database interactions, and various community-related functionalities.

## Features
- User authentication
- Community management
- Post creation and management
- Database integration

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Circlo
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Environment variables
Create a `.env` file in the project root with the following:

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | yes | — | SQLAlchemy connection string. |
| `JWT_SECRET_KEY` | yes | — | Signing key for JWT access tokens. Use a long random string. |
| `JWT_ALGORITHM` | no | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | no | `1440` | Access token lifetime, in minutes. |
| `DEBUG_SEED_TOKEN` | yes (for `/debug/seed`) | — | Shared secret required as `X-Debug-Token` header to call the seed endpoint. |

## Usage
To run the application, execute:
```bash
uvicorn app.main:app --reload
```

### Auth flow
1. `POST /debug/seed` with header `X-Debug-Token: <token>` once to create the seed community + admin user.
2. `POST /login` with `{"email": "...", "password": "..."}` → returns `{access_token, token_type, user}`.
3. Send `Authorization: Bearer <access_token>` on subsequent calls.
4. `GET /users/me` returns the authenticated user.

## Directory Structure
```
.
├── app/
│   ├── auth.py
│   ├── database.py
│   ├── deps.py
│   ├── main.py
│   ├── models.py
│   ├── routers/
│   │   ├── communities.py
│   │   ├── debug.py
│   │   ├── posts.py
│   │   └── users.py
│   └── schemas.py
├── create_tables.py
└── commands.txt
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Thanks to all contributors and the open-source community for their support.