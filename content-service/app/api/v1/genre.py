from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from services.acsess_checker import security_jwt
from services.genre import GenreService, get_genre_service


router = APIRouter()


@router.get(
    "/{genre_id}",
)
async def ganre_by_id(
        user: Annotated[dict, Depends(security_jwt)],
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
):
    """
     Данный эндпоинт отдает жанры по uuid
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre


@router.get("/")
async def all_genres(
        user: Annotated[dict, Depends(security_jwt)],
        genre_service: GenreService = Depends(get_genre_service)
):
    """
     Данный эндпоинт отдает все вохможные жанры
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    genre = await genre_service.get_genre()
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre
