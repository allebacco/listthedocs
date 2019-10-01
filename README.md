# List The Docs

List The Docs allows you to collect in the same page the documentation of
different projects hosted on different servers.

See the full project documentation [here](https://allebacco.github.io/listthedocs/).

List The Docs does not (actually) provide documentation hosting, but it only
serves a web page with a nice list of project and documentation links.

This work has been inspired from [Host the Docs](https://github.com/rgalanakis/hostthedocs),
but change in the aim of the project has lead to a complete rewrite of the
source code.

The project is written in Python using Flask.

## Start the server

Since List The Docs has been developed using Flask, it can be executed with
the following commands:

```bash
export FLASK_APP=listthedocs
flask run
* Running on http://127.0.0.1:5000/
```

For Windows commandline use:

```bat
set FLASK_APP=listthedocs
```

And for Windows Powershell use:

```powershell
$env:FLASK_APP="listthedocs"
```

### Configuration

The service can be configured with a Python file `config.py`, that can be placed
in the app's [*instance_path*](https://flask.palletsprojects.com/en/1.0.x/config/#instance-folders).

The *instance_path* can be customized by setting the *INSTANCE_PATH* to an
absolute path.

The configuration is loaded from the `config.py` in the *instance_path*:

- **DATABASE_URI**: Database connection URI. Defaults to an SQLite database.
- **COPYRIGHT**: The copyright footer message. HTML is allowed.
- **TITLE**: The title of the web pages.
- **HEADER**: The header of the web page. HTML is allowed.
- **READONLY**: Set to true to disable the write REST APIs.
- **LOGIN_DISABLED**: Disable the login and security.
- **ROOT_API_KEY**: The Api-Key for the `root` user. Default `ROOT-API-KEY`.

### Usage

The service provides a set of REST APIs to manage projects and versions.

#### Build and Host documentation

Before using the APIs, you should build the documentation to be loaded (e.g.
with Sphinx, MkDocs, Doxygen, ...) and host it on a web server. List The Docs
does not provide documentation hosting service.

#### Collect documentations in List The Docs

After deploying a project's documentation on your favourite hosting service,
you can visualize it in List The Docs through the following steps:

1. Add the project (if not already present)
2. Add the new version to the project

##### Add a project to List The Docs

Adding a project to List The Docs can be achieved through the following
REST API:

``` python
import requests

response = requests.post(
    'http://localhost:5000/api/v1/projects',
    json={
        'title': 'Project Title',
        'description': 'The description of the project',
    }
)
```

The response contains the `name` of the project

##### Add a documentation version link to List The Docs

Adding a version for a project documentation to List The Docs can be achieved
through the following REST API:

``` python
import requests

requests.post(
    'http://localhost:5000/api/v1/projects/<project-name>/versions',
    json={
        'name': '1.0.0',
        'url': 'http://www.example.com/doc/1.0.0/index.html',
    }
)
```

### Python Client

To simplify the management of the projects, List The Docs provides a
simple Python client:

``` python
from listthedocs.client import ListTheDocs, Project, Version

client = ListTheDocs()
project = client.add_project(
    Project(title='Project Title', description='description')
)
client.add_version(
    project,
    Version('1.0.0', 'http://www.example.com/doc/1.0.0/index.html')
)
```
