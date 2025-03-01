# PostgreSQL User and Group Management App

A web application built with FastHTML for managing PostgreSQL database users and groups.

## Features

- PostgreSQL User Management: Create, read, update, and delete PostgreSQL database users
- PostgreSQL Group Management: Create, read, update, and delete PostgreSQL database groups
- User Privileges: Set superuser, createdb, createrole, and other user privileges
- Group Membership: Assign users to groups and manage group memberships

## Requirements

- Python 3.8+
- PostgreSQL database with superuser access
- Required Python packages:
  - python-fasthtml
  - psycopg2-binary

## Installation

1. Clone the repository
2. Install the required packages:

```bash
pip install python-fasthtml psycopg2-binary
```

## Usage

Run the application with the following command:

```bash
./run.sh --dbname your_db_name --user your_db_user --password your_db_password [--host your_db_host] [--port your_db_port] [--app-port your_app_port]
```

Or directly with Python:

```bash
python app.py --dbname your_db_name --user your_db_user --password your_db_password [--host your_db_host] [--port your_db_port] [--app-port your_app_port]
```

### Command-line Arguments

- `--dbname`: PostgreSQL database name (required)
- `--user`: PostgreSQL username (required, must have superuser privileges)
- `--password`: PostgreSQL password (required)
- `--host`: PostgreSQL host (default: 0.0.0.0)
- `--port`: PostgreSQL port (default: 5432)
- `--app-port`: Application port (default: 50798)

## Important Notes

- The application requires superuser privileges to manage PostgreSQL users and groups
- It interacts directly with PostgreSQL system tables like `pg_user` and `pg_group`
- All operations are performed using SQL statements executed against the PostgreSQL database

## Project Structure

```
app/
├── __init__.py
├── controllers/
│   ├── __init__.py
│   ├── user_controller.py
│   └── group_controller.py
├── database/
│   ├── connection.py
│   └── init_db.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── role.py
└── templates/
app.py
README.md
run.sh
```

## License

MIT