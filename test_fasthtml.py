from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return Div("Hello World", cls="container")

if __name__ == "__main__":
    serve(host='0.0.0.0', port=50798)