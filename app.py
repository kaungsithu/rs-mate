import os
import argparse
from fasthtml.common import *
from dataclasses import dataclass

app, rt = fast_app()

from app import initialize_database
from app.controllers import *

@dataclass
class DatabaseConnection:
    host: str
    dbname: str
    user: str
    password: str

# Home page route
@rt('/old-home-page')
def get():
    return Div(
        Title("PostgreSQL User and Group Management"),
        picolink,
        Div(
            Div(
                H1("PostgreSQL User and Group Management", cls="display-4"),
                P("A simple application to manage PostgreSQL database users and groups.", cls="lead"),
                Hr(cls="my-4"),
                P("Use the navigation below to manage your PostgreSQL database entities."),
                Div(
                    Div(
                        Div(
                            H5("Users", cls="card-title"),
                            P("Manage PostgreSQL database users and their privileges.", cls="card-text"),
                            A("Manage Users", href="/users", cls="btn btn-primary")
                        ),
                        cls="card-body"
                    ),
                    cls="card col-md-6"
                ),
                Div(
                    Div(
                        Div(
                            H5("Groups", cls="card-title"),
                            P("Manage PostgreSQL database groups and their members.", cls="card-text"),
                            A("Manage Groups", href="/groups", cls="btn btn-primary")
                        ),
                        cls="card-body"
                    ),
                    cls="card col-md-6"
                ),
                cls="row mt-4"
            ),
            cls="jumbotron"
        ),
        cls="container mt-5"
    )

@rt('/')
def get():
    return Div(
        Title("Connect to PostgreSQL Database"),
        Div(
            Div(
                H1("Connect to PostgreSQL Database", cls="display-4"),
                P("Please enter the database connection details to continue.", cls="lead"),
                Hr(cls="my-4"),
                Form(
                    Div(
                        Label("Database Host", cls="form-label"),
                        Input(type="text", name="host", cls="form-control", placeholder="localhost")
                    ),
                    Div(
                        Label("Database Name", cls="form-label"),
                        Input(type="text", name="dbname", cls="form-control", placeholder="postgres")
                    ),
                    Div(
                        Label("Username", cls="form-label"),
                        Input(type="text", name="user", cls="form-control", placeholder="postgres")
                    ),
                    Div(
                        Label("Password", cls="form-label"),
                        Input(type="password", name="password", cls="form-control")
                    ),
                    Div(
                        Button("Connect", type="submit", cls="btn btn-primary")
                    ),
                    hx_post="/connect",
                    hx_target="#result"
                ),
                Div(id="result"),
                cls="jumbotron"
            ),
            cls="container mt-5"
        )
    )

@rt('/connect')
def post(db_conn: DatabaseConnection):
    # Initialize database
    if not initialize_database(db_conn.dbname, db_conn.user, db_conn.password, db_conn.host, '5439'):
        return Div(
            Title("Connection Failed"),
            H1("Failed to connect to database", cls="display-4"),
            P("Please check the connection details and try again.", cls="lead"),
            id="result",
            cls="jumbotron container mt-5"
        )

    # Redirect to the db-home page
    return db_home()

@rt('/db-home')
def db_home():
    return Div(
        Title("PostgreSQL User and Group Management"),
        picolink,
        Div(
            Div(
                H1("PostgreSQL User and Group Management", cls="display-4"),
                P("A simple application to manage PostgreSQL database users and groups.", cls="lead"),
                Hr(cls="my-4"),
                P("Use the navigation below to manage your PostgreSQL database entities."),
                Div(
                    Div(
                        Div(
                            H5("Users", cls="card-title"),
                            P("Manage PostgreSQL database users and their privileges.", cls="card-text"),
                            A("Manage Users", href="/users", cls="btn btn-primary")
                        ),
                        cls="card-body"
                    ),
                    cls="card col-md-6"
                ),
                Div(
                    Div(
                        Div(
                            H5("Groups", cls="card-title"),
                            P("Manage PostgreSQL database groups and their members.", cls="card-text"),
                            A("Manage Groups", href="/groups", cls="btn btn-primary")
                        ),
                        cls="card-body"
                    ),
                    cls="card col-md-6"
                ),
                cls="row mt-4"
            ),
            cls="jumbotron"
        ),
        cls="container mt-5"
    )

def main():
    # parser = argparse.ArgumentParser(description='PostgreSQL User and Group Management App')
    # parser.add_argument('--dbname', type=str, required=True, help='PostgreSQL database name')
    # parser.add_argument('--user', type=str, required=True, help='PostgreSQL username (requires superuser privileges)')
    # parser.add_argument('--password', type=str, required=True, help='PostgreSQL password')
    # parser.add_argument('--host', type=str, default='0.0.0.0', help='PostgreSQL host (default: 0.0.0.0)')
    # parser.add_argument('--port', type=str, default='5432', help='PostgreSQL port (default: 5432)')
    # parser.add_argument('--app-port', type=int, default=50798, help='Application port (default: 50798)')
    
    # args = parser.parse_args()
    
    # # Initialize database
    # if not initialize_database(args.dbname, args.user, args.password, args.host, args.port):
    #     print("Failed to initialize database. Exiting.")
    #     return
    
    # Run the application
    serve()

if __name__ == '__main__':
    main()
