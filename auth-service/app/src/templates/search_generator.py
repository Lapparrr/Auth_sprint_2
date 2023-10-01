FILMS_SEARCH_TEMPLATE_GENRE = {
    "query": {"nested": {"path": 'genre', "query": {"term": {"genre.name": None}}}},
    "sort": [{"imdb_rating": "desc"}],
    "from": None,
    "size": None,
}


FILMS_SEARCH_TEMPLATE = {
    "query": {"match_all": {}},
    "sort": [{"imdb_rating": "desc"}],
    "from": None,
    "size": None,
}


PERSON_SEARCH_TEMPLATE = {
    "query": {"bool": {"must": {"match": {"full_name": None}}}},
    "sort": [],
    "from": None,
    "size": None,
}

FIML_TITLE_SEARCH_TEMPLATE = {
    "query": {"bool": {"must": {"match": {"title": None}}}},
    "sort": [],
    "from": None,
    "size": None,
}


FIML_GENRE_TEMPLATE = {
    "query": {"match_all": {}},
    "sort": [],
    "from": None,
    "size": None,
}
