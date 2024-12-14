from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import utils, contacts, auth, users

app = FastAPI(
    title="My Application",
    description="This is the main entry point of the FastAPI application.",
    version="1.0.0",
)

origins = ["http://localhost:8000"]

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

app.include_router(utils.router, prefix=API_PREFIX)
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(contacts.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)


def main():
    """
    Run the FastAPI application using uvicorn.

    This function serves as the entry point when running the application directly.
    It launches uvicorn with the specified host, port, and reload settings.

    Returns:
        None
    """
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
