from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.kennapartner_backend import auth, book, news, insight

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth)
app.include_router(book)
app.include_router(news)
app.include_router(insight)


@app.get("/", tags=["Health"])
def health_check():
    return JSONResponse(
        content={"message": "Backend Server is active"},
        status_code=200,
    )
