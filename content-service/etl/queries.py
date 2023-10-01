SQL_MOVIES =  """SELECT
            fw.id,
            fw.rating AS imdb_rating,
            fw.title,
            fw.description,
            COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'person_role', pfw.role,
                        'person_id', p.id,
                        'person_name', p.full_name
                    )
                ) FILTER (WHERE p.id is not null),
                '[]'
            ) as persons,
            COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'uuid', gfw.genre_id,
                        'name', g.name
                    )
                ) FILTER (WHERE g.id is not null),
                '[]'
            ) as genre
                    FROM content.film_work fw
                    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                    LEFT JOIN content.person p ON p.id = pfw.person_id
                    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                    LEFT JOIN content.genre g ON g.id = gfw.genre_id
                    WHERE fw.modified >= %s
                    GROUP BY fw.id
                    ORDER BY fw.modified;
    """
SQL_PERSONS = """SELECT
            fw.id,
            fw.rating AS imdb_rating,
            fw.title,
            fw.description,
            COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'person_role', pfw.role,
                        'person_id', p.id,
                        'person_name', p.full_name
                    )
                ) FILTER (WHERE p.id is not null),
                '[]'
            ) as persons,
            COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'uuid', gfw.genre_id,
                        'name', g.name
                    )
                ) FILTER (WHERE g.id is not null),
                '[]'
            ) as genre
                    FROM content.person p 
                    LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id 
                    LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
                    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                    LEFT JOIN content.genre g ON g.id = gfw.genre_id
                    WHERE p.modified >= %s
                    GROUP BY fw.id;
    """

SQL_GENRES = """SELECT
            fw.id,
            fw.rating AS imdb_rating,
            fw.title,
            fw.description,
            COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'person_role', pfw.role,
                        'person_id', p.id,
                        'person_name', p.full_name
                    )
                ) FILTER (WHERE p.id is not null),
                '[]'
            ) as persons,
            COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'uuid', gfw.genre_id,
                        'name', g.name
                    )
                ) FILTER (WHERE g.id is not null),
                '[]'
            ) as genre
                    FROM content.genre g   
                    LEFT JOIN content.genre_film_work gfw ON g.id = gfw.genre_id
                    LEFT JOIN content.film_work fw ON gfw.film_work_id = fw.id
                    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                    LEFT JOIN content.person p ON p.id = pfw.person_id
                    WHERE g.modified >= %s
                    GROUP BY fw.id;
    """
SQL_GENRES_GENRES = """SELECT
    g.id,
    g.name,
    g.description,
    COALESCE (
                json_agg(
                    DISTINCT jsonb_build_object(
                        'id_film', fw.id,
                        'rating', fw.rating
                    )
                ) FILTER (WHERE g.id is not null),
                '[]'
            ) as films
    FROM content.genre g   
    LEFT JOIN content.genre_film_work gfw ON g.id = gfw.genre_id
    LEFT JOIN content.film_work fw ON gfw.film_work_id = fw.id
    WHERE g.modified >=  %s
    GROUP BY g.id; 
"""
SQL_PERSONS_PERSONS = """SELECT
    p.id,
    p.full_name,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'uuid', fw.id,
                'roles', pfw.role
                
            )
        ) FILTER (WHERE p.id is not null),
        '[]'
    ) as films
    FROM content.person p 
    LEFT JOIN content.person_film_work pfw ON pfw.person_id =p.id
    LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
    WHERE p.modified >=  %s
    GROUP BY p.id;                       
    """
SCHEMA_JSON_MOVIES = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "uuid": {
                "type": "keyword"
            },
            "imdb_rating": {
                "type": "float"
            },
            "genre": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "uuid": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "title": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {
                    "raw": {
                        "type": "keyword"
                    }
                }
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "director": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "uuid": {
                        "type": "keyword"
                    },
                    "full_name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "actors_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "writers_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "actors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "uuid": {
                        "type": "keyword"
                    },
                    "full_name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "writers": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "uuid": {
                        "type": "keyword"
                    },
                    "full_name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            }
        }
    }
}


SCHEMA_JSON_GENRES = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "uuid": {
                "type": "keyword"
            },
            "name": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "imdb_rating": {
                "type": "float"
            },
            "films": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id_film": {
                        "type": "keyword"
                    },
                     "rating": {
                        "type": "float"
                    }
                }
            },
        }
    }
}

SCHEMA_JSON_PERSONS = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "uuid": {
                "type": "keyword"
            },
            "full_name": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "films": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "uuid": {
                        "type": "keyword"
                    },
                    "roles": {
                        "type": "text"
                    }
                }
            },
        }
    }
}