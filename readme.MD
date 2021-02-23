# Django Schema Simulator API

The objective is to create a SQL-like schema simulator.
The implementation is up to developer.

### Installation

```sh
$  pip install -r requirements/local.txt
```

#### Migrations

```sh
$ python manage.py makemigrations
```

```sh
$ python manage.py migrate
```

```sh
$ python manage.py runserver
```

**If you need to runserver in a specific port**

```sh
$ python manage.py runserver localhost:9000
```

#### Create Super User

```sh
$ python manage.py createsuperuser
```

## Endpoints

**Create table:**

- METHOD: POST
- URL: server:port/api/table/
- Payload:

```
{
    "name": "movies",
    "fields": [
        {
            "name": "title",
            "attr_type": "str",
            "unique": true,
            "required": true
        },
        {
            "name": "genre",
            "attr_type": "str"
        },
        {
            "name": "release_date",
            "attr_type": "datetime"
        }
    ]
}
```

**Delete table:**

- METHOD: DELETE
- URL: server:port/api/table/id

**Get table schema:**

- METHOD: GET
- URL: server:port/api/tables/id/get_schema/

**Get one table:**

- METHOD: GET
- URL: server:port/api/table/id

**Get table list:**

- METHOD: GET
- URL: server:port/table/
- Query params (optional for filtering):

```
Can filter by attribute value.
Ex. ?title=Die Hard
```

**Insert data into table:**

- METHOD: POST
- URL: server:port/api/tables/id/insert_data/
- Payload:

```
{
    "title": "Inception",
    "rating": 9.1
}
```
