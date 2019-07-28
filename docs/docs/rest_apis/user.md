# Project Management

List The Docs provides a set of REST APIs to manage the users and API access rights
to avoid malicious modifications.

The users REST APIs can be accdessed only from administrators, the users for which
`is_admin` is `true`.

## Root user

At first start, the service creates an administrator users named *root*.
To authenticate as *root* user, you should use the API-Key set in the 
`ROOT_API_KEY` configuration variable.

## Adding new user

It is possible to add a new user with the following call:

```http
POST /api/v1/users HTTP/1.1
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


## Reading an user

It is possible to read an user using the following call:

```http
GET /api/v1/users HTTP/1.1
Content-Type: application/json
Api-Key: f9bf78b9a18ce6d46a0cd2b0b86df9da
```

The response contains the requested user.


```http
HTTP/1.1 201 Ok
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