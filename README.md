# drf_table_builder

POC of backend for a db table builder app.

## Setup and run

1. create a `.env` from the `.env.example` file:
    ```bash
    cp .env.example .env
    ```
2. fill environment variables in `.env` file. This file will be user by `docker compose` or `django-environ`.
3. run project using `docker-compose`:
    1. run `docker-compose up` (configuration and scripts will do the rest):
        ```bash
        docker compose up
        ```

4. alternatively run project using `virualenv`:
    1. create a virtual environment:
        ```bash
        python3 -m venv venv
        ```
    2. activate virtual environment:
        ```bash
        source venv/bin/activate
        ```
    3. install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    4. run migrations:
        ```bash
        python manage.py migrate
        ```
    5. load fixtures:
        ```bash
        python manage.py loaddata fixtures.json
        ```
    6. run server:
        ```bash
        python manage.py runserver
        ```

## API

Project includes endpoints for authentication, user profile, registration, `"tables"` and `"rows"`.

Project uses swagger schema for documentation - check it out at `http://localhost:8000/api/schema/swagger-ui/`. Using this link you will find all the endpoints, but here I will list only required.

Project uses `TokenAuthentication` for authentication and `IsAuthenticatedOrReadOnly` as default permissions. To get a token, you need to log in using `POST /api/login/` endpoint. For non-safe methods, you need to pass the token in the `Authorization` header (don't forget to add `Token ` before token).


### Authentication

#### Login

```http
POST /api/login/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `username` | `string` | **Required**. User username |
| `password` | `string` | **Required**. User password |

### Tables

#### Get table

```http
GET /api/table/:id/
```

#### Get tables

```http
GET /api/table/
```

#### Create table (**Authorization required**)

```http
POST /api/table/
```

| Parameter | Type     | Description                |
|:----------| :------- |:---------------------------|
| `name`    | `string` | **Required**. Table name   |
| `columns` | `array` | **Required**. Table columns |

Columns are an array of objects with the following structure:

```json
{
    "name": "column_name",
    "field_type": "column_type" // one of: "Char", "Integer", "Boolean"
}
```

#### Update table (**Authorization required**)

```http
PUT /api/table/:id/
```

| Parameter | Type     | Description                |
|:----------| :------- |:---------------------------|
| `name`    | `string` | **Required**. Table name   |
| `columns` | `array` | **Required**. Table columns |

Columns are an array of objects with the following structure:

```json
{
    "pk": "column_id",  // optional, if not provided, new column will be created
    "name": "column_name",
    "field_type": "column_type" // one of: "Char", "Integer", "Boolean"
}
```
#### Delete table (**Authorization required**)

```http
DELETE /api/table/:id/
```

### Rows

#### Get rows

```http
GET /api/table/:id/rows/
```

#### Create row (**Authorization required**)

```http
POST /api/table/:id/row/
```

| Parameter         | Type                               | Description   |
|:------------------|:-----------------------------------|:--------------|
| **Not specified** | `string` or `integer` or `boolean` | **Required**. |
| ...               | ...                                | ...           |
| **Not specified** | `string` or `integer` or `boolean` | **Required**. |


## Tests

1. run tests using `docker-compose`:
    1. run `docker-compose up`:
        ```bash
        docker compose up
        ```
    2. run tests:
        ```bash
        docker compose exec app python manage.py test
        ```
2. alternatively run tests using `virualenv`:
   1. activate virtual environment:
       ```bash
       source venv/bin/activate
       ```
   2. run tests:
       ```bash
       python manage.py test
       ```
