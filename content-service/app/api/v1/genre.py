from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from services.genre import GenreService, get_genre_service


router = APIRouter()


@router.get(
    "/{genre_id}",
)
async def ganre_by_id(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
):
    """
     Данный эндпоинт отдает жанры по uuid
    """
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre


@router.get("/")
async def all_genres(genre_service: GenreService = Depends(get_genre_service)):
    """
     Данный эндпоинт отдает все вохможные жанры
    """
    genre = await genre_service.get_genre()
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
    return genre
