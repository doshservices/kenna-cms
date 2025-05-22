from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile
from .schema import InsightSchema, QueryParamsSchema
from fastapi.responses import JSONResponse
from beanie.operators import RegEx
from fastapi.security import HTTPAuthorizationCredentials
from ...dependencies import get_current_user, FileValidator
from typing import Annotated
from .model import Insight, InsightAuthor
from motor.motor_asyncio import AsyncIOMotorClient
from ...utils import connect_to_database
from ...services import upload_file_to_cloudinary
from datetime import datetime


insight = APIRouter(prefix="/api/v1/insights", tags=["Insight"])


@insight.post("/")
async def create_insight(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    validated_request: InsightSchema,
):

    insight_authors = []
    for data in validated_request.authors:
        author = await InsightAuthor.find_one(InsightAuthor.email == data.email)
        if not author:
            author = InsightAuthor(**data.model_dump(mode="json"))
            await author.insert()
            insight_authors.append(author)

    insight = await Insight.find_one(Insight.title == validated_request.title)
    if insight:
        raise HTTPException(
            status_code=409, detail={"message": "Insight already exist"}
        )

    insight = Insight(
        title=validated_request.title,
        content=validated_request.content,
        authors=insight_authors,
    )
    await insight.insert()
    return JSONResponse(
        content={"data": {"insight": insight.model_dump(mode="json")}}, status_code=201
    )


@insight.patch("/{id}/upload")
async def upload_insight_file(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
    file: UploadFile,
    validate_file: Annotated[bool, Depends(FileValidator)],
):
    insight = await Insight.get(id, fetch_links=True)
    if insight is None:
        raise HTTPException(
            status_code=404, detail={"message": "Insight does not exist"}
        )

    uploaded_file = upload_file_to_cloudinary(file)
    await insight.set({Insight.file_url: uploaded_file})

    return JSONResponse(
        content={"data": {"insight": insight.model_dump(mode="json")}}, status_code=200
    )


@insight.patch("/{insight_id}/authors/{author_id}/upload")
async def upload_insight_author_file(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    insight_id: Annotated[str, Path()],
    author_id: Annotated[str, Path()],
    file: UploadFile,
    validate_file: Annotated[bool, Depends(FileValidator)],
):
    insight = await Insight.get(insight_id, fetch_links=True)
    if insight is None:
        raise HTTPException(
            status_code=404, detail={"message": "Insight does not exist"}
        )

    insight_author = await InsightAuthor.get(author_id, fetch_links=True)
    if insight_author is None:
        raise HTTPException(
            status_code=404, detail={"message": "Author does not exist"}
        )

    uploaded_file = upload_file_to_cloudinary(file)
    await insight_author.set({InsightAuthor.file_url: uploaded_file})

    return JSONResponse(
        content={"data": {"insight": insight.model_dump(mode="json")}}, status_code=200
    )


@insight.get("/")
async def list_insight(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    query_params: Annotated[QueryParamsSchema, Query()],
):
    filter = []
    if query_params.year:
        start = datetime(int(query_params.year), 1, 1)
        end = datetime(int(query_params.year) + 1, 1, 1)

        filter.append(Insight.created_at >= start)
        filter.append(Insight.created_at < end)

    if query_params.query:
        filter.append(RegEx(Insight.title, query_params.query, options="i"))

    insights = (
        await Insight.find(*filter, fetch_links=True)
        .skip((query_params.page - 1) * query_params.limit)
        .limit(10)
        .to_list()
    )

    total_insight = await Insight.count()
    return JSONResponse(
        content={
            "data": {
                "insight": [insight.model_dump(mode="json") for insight in insights],
                "page": query_params.page,
                "limit": query_params.limit,
                "total_insight": total_insight,
            }
        },
        status_code=200,
    )


@insight.get("/{id}")
async def get_insight(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    id: Annotated[str, Path()],
):
    insight = await Insight.get(id, fetch_links=True)
    if insight is None:
        raise HTTPException(
            status_code=404, detail={"message": "Insight does not exist"}
        )

    return JSONResponse(
        content={"data": {"insight": insight.model_dump(mode="json")}}, status_code=200
    )


@insight.put("/{insight_id}/authors/{author_id}")
async def update_insight(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    insight_id: Annotated[str, Path()],
    author_id: Annotated[str, Path()],
    validated_request: InsightSchema,
):
    insight = await Insight.get(insight_id)
    if insight is None:
        raise HTTPException(
            status_code=404, detail={"message": "Insight does not exist"}
        )
    
    

    await insight.set({**validated_request.model_dump(mode="json")})
    return JSONResponse(
        content={"data": {"insight": insight.model_dump(mode="json")}}, status_code=200
    )


@insight.delete("/{id}")
async def delete_insight(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
):
    insight = await Insight.get(id)
    if insight is None:
        raise HTTPException(
            status_code=404, detail={"message": "Insight does not exist"}
        )

    await insight.delete()
    return JSONResponse(content={"message": "Insight deleted"}, status_code=200)
