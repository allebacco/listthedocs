# Python Client

To simplify the interaction with the rest APIs, List The Docs provides a
Python client. The following line will load it and its entities.

``` python
from listthedocs.client import ListTheDocs, Project, Version
```

## Entities

The Python client defines two entities: ``Project`` and ``Version``.

### Project

The ``Project`` entity has the following fields:

| Field       | Type  | Description |
|:-----------:|:-----:|:-----------:|
| name        | *str* | The name of the project |
| description | *str* | The description of the project. Custom HTML is allowed. |
| logo        | *str* | The Logo of the project (optional). |
| versions    | *tuple[Version]* | The list of docuemntation versions |

!!! tip
    The *logo* field contains a string that can be used inside the ``src`` attribute
    of an HTML ``img`` tag. E.g.:

    - ``http://www.example.com/logo.png``: A link to an image
    - ``data:image/png;base64,<BASE64 of the image file>``: The image itself

### Version

The ``Version`` entity has the following fields:

| Field       | Type  | Description |
|:-----------:|:-----:|:-----------:|
| name        | *str* | The name of the docuemtation version (e.g. *1.0.0*). |
| url         | *str* | The url to the to the documentation files. |

## Client

The ``ListTheDocs`` class defines all the functions needed to manage
the ``Project`` and ``Version`` entities. Moreover, the client provides functionalities
for managing users and roles. 

Below example usages for managing projects and versions.

### Adding a Project

The following code will add a project:

``` python
from listthedocs.client import ListTheDocs, Project

# Instantiate the client with default service location
client = ListTheDocs()

# Add a project
project = client.add_project(Project('Project-Name', 'A long description'))

print(project)
```

### Reading a Project

The following code will read a project named *Project-Name*:

``` python
from listthedocs.client import ListTheDocs, Project

# Instantiate the client with default service location
client = ListTheDocs()

# Read a project
project = client.get_project('Project-Name')

print(project)
```

### Reading all the Projects

The following code will read all the projects:

``` python
from listthedocs.client import ListTheDocs, Project

# Instantiate the client with default service location
client = ListTheDocs()

# Read all the projects
projects = client.get_projects()

print(projects)
```

### Updating a Project

It is possible to update the *description* or the *logo* of a Project using the following
code:

``` python
from listthedocs.client import ListTheDocs, Project

# Instantiate the client with default service location
client = ListTheDocs()

project = # ... Create Project-Name project

# update both logo and description
project = client.update_project(
    'Project-Name', 
    description='new description',
    logo='http://www.example.com/log.png'
)

print(projects)
```

### Removing a Project

It is possible to remove a Project (and all its versions) using the following code:

``` python
from listthedocs.client import ListTheDocs, Project

# Instantiate the client with default service location
client = ListTheDocs()

project = # ... Create Project-Name project

# Remove the project
project = client.delete_project('Project-Name')
```

### Adding a new documentation Version to a Project

The following code will add a new documentation version to the *Project-Name*
project:

``` python
from listthedocs.client import ListTheDocs, Project, Version

# Instantiate the client with default service location
client = ListTheDocs()

project = # ... Create Project-Name project

# Add a project version
project = client.add_version(
    'Project-Name', 
    Version('1.0.0', 'http://www.example.com/doc/1.0.0/index.html')
)
```

Each Project can have multiple documentation versions.

### Updating a documentation Version

After adding a documentation version to a Project, it is possible to update
it (e.g. in case documentation has been moved to a different URL).

The *name* field can't be changed.

The following code will update the documentation URL:

``` python
from listthedocs.client import ListTheDocs, Project, Version

# Instantiate the client with default service location
client = ListTheDocs()

project = # ... Create Project-Name project
project = # ... Add a project version 1.0.0

# Update the project version URL
project = client.update_version(
    'Project-Name', '1.0.0', 
    url='http://www.example.com/new_doc/1.0.0/index.html'
)
```

### Removing a Version from a Project

It is possible to remove a Version from a Project using the following code:

``` python
from listthedocs.client import ListTheDocs, Project, Version

# Instantiate the client with default service location
client = ListTheDocs()

project = # ... Create Project-Name project
project = # ... Add a project version 1.0.0

# Delete project version
project = client.delete_version('Project-Name', '1.0.0')
```
