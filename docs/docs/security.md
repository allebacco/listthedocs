# Security

*List The Docs* uses a token (`Api-Key`) to limit the access to the REST APIs
to only known users.

To enable the sececurity access, set

``` python
LOGIN_DISABLED = True
```

in the configuration file.

The administrator of the service is the `root` user that is allowed to create
and remove other users and manage their permissions on all the projects.<br>
Moreover, the `root` user can manage both projects and versions.


## Roles

The usage of the REST APIs form managing the projects is restricted to the users
by *roles*. The roles are assigned to users only to specific projects.

The following roles are available:

- `PROJECT_MANAGER`: The user can update/delete the project and add/update/remove versions
- `VERSION_MANAGER`: The user can add/update/remove versions