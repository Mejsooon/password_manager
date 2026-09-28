from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(title = "Password Manager", description = "REST API for Password Manager", version = "1.0.0")

    return app

app = create_app()

@app.get("/", tags=["root"])
def root():
    return {"message": "Password Manager is working"}