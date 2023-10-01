from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Union, Annotated

import logging

from services.acsess_checker import security_jwt
from services.person import PersonService, get_person_service
from services.film import FilmService, get_film_service
from api.v1.mixin import create_page

router = APIRouter()


class Films(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class PersonParams(BaseModel):
    page_number: Optional[int] = 1
    page_size: Optional[int] = 50


@router.get(
    "/{person_id}",
)
async def person_by_id(
        user: Annotated[dict, Depends(security_jwt)],
        person_id: str,
        person_service: PersonService = Depends(get_person_service),
):
    """
     Данный эндпоинт отдает персонажей по uuid
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person


@router.get(
    "/{person_id}/films",
)
async def person_details(
        user: Annotated[dict, Depends(security_jwt)],
        person_id: str,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service),
):
    """
     Данный эндпоинт отдает персонажей по uuid
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    person = await person_service.get_by_id(person_id)
    films_data = list()
    for film in person.films:
        _film = await film_service.get_by_id(film["uuid"])
        films_data.append(
            Films(uuid=_film.uuid, title=_film.title, imdb_rating=_film.imdb_rating)
        )
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return films_data


@router.get("/")
async def all_presons(
        user: Annotated[dict, Depends(security_jwt)],
        page_params: PersonParams = Depends(),
        person_service: PersonService = Depends(get_person_service),
):
    """
     Данный эндпоинт отдает всех персонажей
    - **page_number**: номер страницы
    - **page_size**: число фильмов на одной странице
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    person, total = await person_service.get_person(page_params)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return create_page(person, total, page_params)


@router.get("/search/", response_model=Page)
async def search_persons(
        user: Annotated[dict, Depends(security_jwt)],
        query: str,
        person_service: PersonService = Depends(get_person_service)
):
    """
     Данный эндпоинт отдает персонажей с гибким поисковиком, поиск происходит по полю full_name
    - **query**: что нужно найти
    - **page**: номер страницы
    - **size**: число персонажей на одной странице
    """
    if not user:
        raise HTTPException(status_code=403, detail='available only to registered users')
    try:
        fields = ["uuid", "full_name", "films"]
        search_results = await person_service.search_persons(
            index="persons", query=query, fields=fields
        )
        return paginate(search_results)
    except ValidationError as e:
        logging.info("Validation error:", e)
        raise e  # HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=e.errors())
