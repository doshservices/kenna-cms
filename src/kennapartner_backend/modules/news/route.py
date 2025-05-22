from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile
from .schema import BookSchema, QueryParamsSchema
from fastapi.responses import JSONResponse
from beanie.operators import RegEx
from fastapi.security import HTTPAuthorizationCredentials
from ...dependencies import get_current_user, FileValidator
from typing import Annotated
from .model import News
from motor.motor_asyncio import AsyncIOMotorClient
from ...utils import connect_to_database
from ...services import upload_file_to_cloudinary
from datetime import datetime


news = APIRouter(prefix="/api/v1/news", tags=["News"])


@news.post("/")
async def create_news(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    validated_request: BookSchema,
):
    news = await News.find_one(News.title == validated_request.title)
    if news:
        raise HTTPException(status_code=409, detail={"message": "News already exist"})

    news = News(**validated_request.model_dump(mode="json"))
    await news.insert()
    return JSONResponse(content={"data": {"news": news.model_dump(mode="json")}}, status_code=201)


@news.patch("/{id}/upload")
async def upload_file(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
    file: UploadFile,
    validate_file: Annotated[bool, Depends(FileValidator)],
):
    news = await News.get(id)
    if news is None:
        raise HTTPException(status_code=404, detail={"message": "News does not exist"})

    uploaded_file = upload_file_to_cloudinary(file)

    await news.set({News.file_url: uploaded_file})
    return JSONResponse(
        content={"data": {"news": news.model_dump(mode="json")}}, status_code=200
    )


@news.get("/")
async def list_news(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    query_params: Annotated[QueryParamsSchema, Query()],
):
    filter = []
    if query_params.year:
        start = datetime(int(query_params.year), 1, 1)
        end = datetime(int(query_params.year) + 1, 1, 1)

        filter.append(News.created_at >= start)
        filter.append(News.created_at < end)

    if query_params.query:
        filter.append(RegEx(News.title, query_params.query, options="i"))

    news = (
        await News.find(*filter)
        .skip((query_params.page - 1) * query_params.limit)
        .limit(10)
        .to_list()
    )

    total_news = await News.count()
    return JSONResponse(
        content={
            "data": {
                "news": [news_.model_dump(mode="json") for news_ in news],
                "page": query_params.page,
                "limit": query_params.limit,
                "total_news": total_news,
            }
        },
        status_code=200,
    )


@news.get("/{id}")
async def get_news(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    id: Annotated[str, Path()],
):
    news = await News.get(id)
    if news is None:
        raise HTTPException(status_code=404, detail={"message": "News does not exist"})

    return JSONResponse(
        content={"data": {"news": news.model_dump(mode="json")}}, status_code=200
    )


@news.put("/{id}")
async def update_news(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
    validated_request: BookSchema,
):
    news = await News.get(id)
    if news is None:
        raise HTTPException(status_code=404, detail={"message": "News does not exist"})

    await news.set({**validated_request.model_dump(mode="json")})
    return JSONResponse(
        content={"data": {"news": news.model_dump(mode="json")}}, status_code=200
    )


@news.delete("/{id}")
async def delete_news(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
):
    news = await News.get(id)
    if news is None:
        raise HTTPException(status_code=404, detail={"message": "News does not exist"})

    await news.delete()
    return JSONResponse(content={"message": "News deleted"}, status_code=200)
