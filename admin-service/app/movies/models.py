import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = _('genre_film_work')
        constraints = [
            models.UniqueConstraint(fields=['genre', 'film_work'],
                                    name='genre_film_work_inx')
        ]


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_('Full_name'), max_length=255)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')


class PersonFilmwork(UUIDMixin):
    class RoleType(models.TextChoices):
        actor = 'actor', _('Actor')
        writer = 'writer', _('Writer')
        director = 'director', _('Director')

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.CharField(_('Role'), max_length=15, blank=True,
                            choices=RoleType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = _('person_film_work')
        constraints = [
            models.UniqueConstraint(fields=['role', 'person', 'film_work'],
                                    name='film_work_person_idx')
        ]


class Filmwork(UUIDMixin, TimeStampedMixin):
    TYPE_CHOICES = [('MOV', _('movie')), ('TVS', _('tv_show'))]
    title = models.CharField(_('title'), max_length=255)
    creation_date = models.DateField(_('Creation_date'), null=True)
    description = models.TextField(_('description'), blank=True)
    rating = models.FloatField(_('Rating'), null=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])
    file_path = models.TextField(_('file_path'), blank=True)
    type = models.CharField(_("type"), choices=TYPE_CHOICES, blank=True,
                            max_length=30)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworks')
