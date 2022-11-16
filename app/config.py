from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from routers.users import user_router
from routers.companies import company_router
from routers.tasks import task_router


def configure(app):
    origins = [
        "http://localhost",
        "http://localhost:8000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    add_pagination(app)
    app.include_router(user_router)
    app.include_router(company_router)
    app.include_router(task_router)
