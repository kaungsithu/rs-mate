import os
import argparse
from fasthtml.common import *
from app import initialize_database
from app.controllers import *

app, rt = fast_app()

# Home page route
@rt('/')
def get():
    return (
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
                            Div(
                                H5("Users", cls="card-title"),
                                P("Manage PostgreSQL database users and their privileges.", cls="card-text"),
                                A("Manage Users", href="/users", cls="btn btn-primary")
                            ),
                            cls="card-body"
                        ),
                        cls="card"
                    ),
                    cls="col-md-6"
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
    parser = argparse.ArgumentParser(description='PostgreSQL User and Group Management App')
    parser.add_argument('--dbname', type=str, required=True, help='PostgreSQL database name')
    parser.add_argument('--user', type=str, required=True, help='PostgreSQL username (requires superuser privileges)')
    parser.add_argument('--password', type=str, required=True, help='PostgreSQL password')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='PostgreSQL host (default: 0.0.0.0)')
    parser.add_argument('--port', type=str, default='5432', help='PostgreSQL port (default: 5432)')
    parser.add_argument('--app-port', type=int, default=50798, help='Application port (default: 50798)')
    
    args = parser.parse_args()
    
    # Initialize database
    if not initialize_database(args.dbname, args.user, args.password, args.host, args.port):
        print("Failed to initialize database. Exiting.")
        return
    
    # Run the application
    serve(host='0.0.0.0', port=args.app_port, allow_iframe=True, allow_cors=True)

if __name__ == '__main__':
    main()