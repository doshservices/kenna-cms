from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile
from .schema import BookSchema, QueryParamsSchema
from fastapi.responses import JSONResponse
from beanie.operators import RegEx
from fastapi.security import HTTPAuthorizationCredentials
from ...dependencies import get_current_user, FileValidator
from typing import Annotated
from .model import Book
from motor.motor_asyncio import AsyncIOMotorClient
from ...utils import connect_to_database
from ...services import upload_file_to_cloudinary
from datetime import datetime


book = APIRouter(prefix="/api/v1/books", tags=["Book"])


@book.post("/")
async def create_book(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    validated_request: BookSchema,
):
    book = await Book.find_one(Book.name == validated_request.name)
    if book:
        raise HTTPException(status_code=409, detail={"message": "Book already exist"})

    book = Book(**validated_request.model_dump(mode="json"))
    await book.insert()
    return JSONResponse(
        content={"data": {"book": book.model_dump(mode="json")}}, status_code=201
    )


@book.patch("/{id}/upload")
async def upload_file(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
    file: UploadFile,
    validate_file: Annotated[bool, Depends(FileValidator)],
):
    book = await Book.get(id)
    if book is None:
        raise HTTPException(status_code=404, detail={"message": "Book does not exist"})

    uploaded_file = upload_file_to_cloudinary(file)

    await book.set({Book.file_url: uploaded_file})
    return JSONResponse(
        content={"data": {"book": book.model_dump(mode="json")}}, status_code=200
    )


@book.get("/")
async def list_book(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    query_params: Annotated[QueryParamsSchema, Query()],
):
    filter = []
    if query_params.year:
        start = datetime(int(query_params.year), 1, 1)
        end = datetime(int(query_params.year) + 1, 1, 1)

        filter.append(Book.date >= start)
        filter.append(Book.date < end)

    if query_params.query:
        filter.append(RegEx(Book.name, query_params.query, options="i"))

    books = (
        await Book.find(*filter)
        .skip((query_params.page - 1) * query_params.limit)
        .limit(10)
        .to_list()
    )

    total_books = await Book.count()
    return JSONResponse(
        content={
            "data": {
                "book": [book.model_dump(mode="json") for book in books],
                "page": query_params.page,
                "limit": query_params.limit,
                "total_books": total_books,
            }
        },
        status_code=200,
    )


@book.get("/{id}")
async def get_book(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    id: Annotated[str, Path()],
):
    book = await Book.get(id)
    if book is None:
        raise HTTPException(status_code=404, detail={"message": "Book does not exist"})

    return JSONResponse(
        content={"data": {"book": book.model_dump(mode="json")}}, status_code=200
    )


@book.put("/{id}")
async def update_book(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
    validated_request: BookSchema,
):
    book = await Book.get(id)
    if book is None:
        raise HTTPException(status_code=404, detail={"message": "Book does not exist"})

    await book.set({**validated_request.model_dump(mode="json")})
    return JSONResponse(
        content={"data": {"book": book.model_dump(mode="json")}}, status_code=200
    )


@book.delete("/{id}")
async def delete_book(
    init_database: Annotated[AsyncIOMotorClient, Depends(connect_to_database)],
    current_user: Annotated[HTTPAuthorizationCredentials, Depends(get_current_user)],
    id: Annotated[str, Path()],
):
    book = await Book.get(id)
    if book is None:
        raise HTTPException(status_code=404, detail={"message": "Book does not exist"})

    await book.delete()
    return JSONResponse(content={"message": "Book deleted"}, status_code=200)
