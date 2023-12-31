from fastapi import APIRouter, FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from bytepit_api.routers.admin import router as admin_router
from bytepit_api.routers.auth import router as auth_router
from bytepit_api.routers.problem import router as problem_router
from bytepit_api.routers.competition import router as competition_router

from pydantic import ValidationError


router = APIRouter(prefix="/api")
router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(competition_router)
router.include_router(problem_router)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://salmon-stone-0a40c2203.4.azurestaticapps.net",
        "https://bytepit.cloud",
        "https://dev.bytepit.cloud",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    formatted_errors = []
    error_details = exc.errors()
    for error in error_details:
        error_message = error["msg"]
        if "value is not a valid email address: " in error_message:
            error_message = error_message.replace("value is not a valid email address: ", "")
            formatted_message = f"{error_message}"
        else:
            error_field_name = error["loc"][1]
            formatted_message = f"{error_message}: {error_field_name}"
        formatted_errors.append(formatted_message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": formatted_errors},
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc):
    formatted_errors = []
    error_details = exc.errors()
    for error in error_details:
        error_message = error["msg"]
        formatted_message = error_message
        formatted_errors.append(formatted_message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": formatted_errors},
    )
