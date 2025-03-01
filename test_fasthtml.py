from fasthtml.common import *

app = FastHTML()

@app.get('/')
def index():
    return Div("Hello World", cls="container")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=50798)