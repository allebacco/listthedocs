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
    "name": "foo",
    "is_admin": false
}
```

The response contains the created user with its API-Key for authentication.