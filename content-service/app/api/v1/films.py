from http import HTTPStatus
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from pydantic import BaseModel

from api.v1.mixin import create_page
from services.acsess_checker import security_jwt
from services.film import FilmService, get_film_service

router = APIRouter()


class FilmParams(BaseModel):
    sort: Optional[str] = ""
    genre: Optional[str] = ""
    page_number: Optional[int] = 1
    page_size: Optional[int] = 50


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    "/{film_uuid}",
)
async def film_by_id(
        user: Annotated[dict, Depends(security_jwt)],
        film_uuid: str,
        film_service: FilmService = Depends(get_film_service),
):
    """
     Данный эндпоинт отдает фильм по uuid
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    film = await film_service.get_by_id(film_uuid)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать

    return film


@router.get("/")
async def sorted_films(
        user: Annotated[dict, Depends(security_jwt)],
        params: FilmParams = Depends(),
        film_service: FilmService = Depends(get_film_service),
):
    """
     Данный эндпоинт отдает фильмы с сортировкой и фильтрацией по жанрам
    - **sort**: тип сортировки, например imdb_rating
    - **genre**: фильтр по жанрам, вернет фильмы только этого жанра
    - **page_number**: номер страницы
    - **page_size**: число фильмов на одной странице
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    film, total = await film_service.get_by_filter(params)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    film_dict = [
        mod.dict(
            exclude={
                "genre": True,
                "actors": True,
                "writers": True,
                "director": True,
                "actors_names": True,
                "writers_names": True,
                "description": True,
            }
        )
        for mod in film
    ]
    return create_page(film_dict, total, params)


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/search/", response_model=Page)
async def search_films(
        user: Annotated[dict, Depends(security_jwt)],
        query: str,
        film_service: FilmService = Depends(get_film_service),
):
    """
     Данный эндпоинт отдает фильмы с гибким поисковиком, поиск происходит по полю title
    - **query**: что нужно найти
    - **page**: номер страницы
    - **size**: число фильмов на одной странице
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    fields = ["uuid", "title", "imdb_rating"]
    search_results = await film_service.search_films(query=query, fields=fields)
    return paginate(search_results)
