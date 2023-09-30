-- Active: 1682087492546@@127.0.0.1@5432@postgres
CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    file_path TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone,
    CONSTRAINT fk_person
        FOREIGN KEY(person_id)
        REFERENCES content.person (id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL,
    film_work_id uuid NOT NULL,
    created timestamp with time zone,
    CONSTRAINT fk_person
        FOREIGN KEY(genre_id)
        REFERENCES content.genre (id)
        ON DELETE CASCADE
);
--Индекс по дате создания фильмов
CREATE INDEX IF NOT EXISTS film_work_creation_date_idx ON content.film_work(creation_date);

--Индекс по рейтингу
CREATE INDEX IF NOT EXISTS film_work_rating_inx ON content.film_work(rating);

--Индекс по типу
CREATE INDEX IF NOT EXISTS film_work_type_inx ON content.film_work(type);

--Создание уникальный унидексов по участникам фильма и жанру
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);
CREATE UNIQUE INDEX IF NOT EXISTS genre_film_work_inx ON content.genre_film_work(film_work_id, genre_id);
