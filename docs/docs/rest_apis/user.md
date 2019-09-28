# Project Management

List The Docs provides a set of REST APIs to manage the users and API access rights
to avoid malicious modifications.

The users REST APIs can be accdessed only from administrators, the users for which
`is_admin` is `true`.

## Root user

At first start, the service creates an administrator users named *root*.
To authenticate as *root* user, you should use the API-Key set in the 
`ROOT_API_KEY` configuration variable.

## Users

### Adding new user

It is possible to add a new user with the following call:

```http
POST /api/v2/users HTTP/1.1
Content-Type: application/json
Api-Key: f9bf78b9a18ce6d46a0cd2b0b86df9da

{
    "name": "bar",
    "is_admin": false
}
```

| Field       | Type  | Description |
|:-----------:|:-----:|:-----------:|
| name        | *str* | The name of the user |
| is_admin    | *bool* | `true` if the user is an administrator (optional, default `false`) |

The response contains the created user with its API-Key for authentication.

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
    "api_keys": [
        {
            "created_at": "2019-07-28T15:36:07.905314",
            "is_valid": true,
            "key": "JUGT4EbTWwqL9Lr5baSLgC4iYwylC5uCWvfDpHof-XQ"
        }
    ],
    "created_at": "2019-07-28T15:36:07.891430",
    "is_admin": false,
    "name": "bar",
    "roles": []
}
```

The API-Key that the new user should use for authentication is in the
`api_keys.key` field.


### Reading a user

It is possible to read an user using the following call:

```http
GET /api/v2/users/bar HTTP/1.1
Content-Type: application/json
Api-Key: f9bf78b9a18ce6d46a0cd2b0b86df9da
```

The response contains a list with all the users.


```http
HTTP/1.1 200 Ok
Content-Type: application/json

{
    "api_keys": [
        {
            "created_at": "2019-07-28T15:36:07.905314",
            "is_valid": true,
            "key": "18634317c8d7116237af1f82f03b9a26"
        }
    ],
    "created_at": "2019-07-28T15:36:07.891430",
    "is_admin": false,
    "name": "bar",
    "roles": []
}
```

### Reading all the users

It is possible to read all the users using the following call:

```http
GET /api/v2/users HTTP/1.1
Content-Type: application/json
Api-Key: f9bf78b9a18ce6d46a0cd2b0b86df9da
```

The response contains the requested user.

```http
HTTP/1.1 200 Ok
Content-Type: application/json

[
    {
        "api_keys": [
            {
                "created_at": "2019-07-28T15:37:15.786432",
                "is_valid": true,
                "key": "JUGT4EbTWwqL9Lr5baSLgC4iYwylC5uCWvfDpHof-XQ"
            }
        ],
        "created_at": "2019-07-28T15:37:15.786432",
        "is_admin": true,
        "name": "root",
        "roles": []
    },
    {
        "api_keys": [
            {
                "created_at": "2019-07-28T15:36:07.905314",
                "is_valid": true,
                "key": "18634317c8d7116237af1f82f03b9a26"
            }
        ],
        "created_at": "2019-07-28T15:36:07.891430",
        "is_admin": false,
        "name": "bar",
        "roles": []
    }
]
```

## Roles

The roles are used when the [security](../security.md) is enabled.

### Adding roles to user

It is possible to add a roles to a user using the following call:

```http
PATCH /api/v2/users/bar/roles HTTP/1.1
Content-Type: application/json
Api-Key: f9bf78b9a18ce6d46a0cd2b0b86df9da

[
    {
        "role_name": "PROJECT_MANAGER",
        "project_code": "project1"
    },
    {
        "role_name": "VERSION_MANAGER",
        "project_code": "project2"
    }
]
```

The response confirms the roles have been added to the user for the selected projects.

```http
HTTP/1.1 200 Ok
Content-Type: application/json

{
    "message": "Roles added to user"
}
```

### Removing roles from user

It is possible to remove a roles from a user using the following call:

```http
DELETE /api/v2/users/bar/roles HTTP/1.1
Content-Type: application/json
Api-Key: f9bf78b9a18ce6d46a0cd2b0b86df9da

[
    {
        "role_name": "PROJECT_MANAGER",
        "project_code": "project1"
    },
    {
        "role_name": "VERSION_MANAGER",
        "project_code": "project2"
    }
]
```

The response confirms the roles have been removed from the user for the selected projects.

```http
HTTP/1.1 200 Ok
Content-Type: application/json

{
    "message": "Roles removed from user"
}
```

### Reading user roles

It is possible to read the roles of an user using the following call:

```http
GET /api/v2/users/bar/roles HTTP/1.1
Content-Type: application/json
Api-Key: f9bf78b9a18ce6d46a0cd2b0b86df9da
```

The response contains the roles of the user.

```http
HTTP/1.1 200 Ok
Content-Type: application/json

[
    {
        "role_name": "PROJECT_MANAGER",
        "project_code": "project1"
    },
    {
        "role_name": "VERSION_MANAGER",
        "project_code": "project2"
    }
]
```