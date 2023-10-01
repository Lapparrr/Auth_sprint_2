Запуск всех контенеров
```bash
docker-compose up -d --build --force-recreate
```
Запуск admin-service
```bash
docker-compose up --build postgres_db admin_service
```
запуск content-service
```bash
docker-compose up --build redis_db content-service-migration content_service_elastic content_service_etl content_service_app postgres_db
```
Запуск auth-service
```bash
docker-compose up --build nginx auth_service_app postgres_db redis_db
```
Запуск nginx
```bash
docker-compose up --build nginx
```

http://0.0.0.0/admin/
http://0.0.0.0/auth/api/openapi
http://0.0.0.0/api/openapi
