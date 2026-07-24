from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from routers import news, users, favorite
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handlers

# app = FastAPI()
app = FastAPI(docs_url=None)  # 关掉默认的

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="FastAPI",
        swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.17.14/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.17.14/swagger-ui.min.css",
    )

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware, # type: ignore[arg-type]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "This is root page"}


app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)