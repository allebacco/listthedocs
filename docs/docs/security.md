# Security

*List The Docs* uses a token (`Api-Key`) to limit the access to the REST APIs
to only known users.

The administrator of the service is the `root` user that is allowed to create
and remove other users and manage their permissions on all the projects.

## Roles

The usage of the REST APIs form managing the projects is restricted to the users
by *roles*. The roles are assigned to users only to specific projects.

The following roles are available:

- `UPDATE_PROJECT`: The user can update a project
- `REMOVE_PROJECT`: The user can remove the project
- `ADD_VERSION`: The user can ad a new documentation version to the project
- `UPDATE_VERSION`: The user can update a documentaton version on the project
- `REMOVE_VERSION`: The user can remove a documentation version from the project