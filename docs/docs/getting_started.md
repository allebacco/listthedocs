# Getting Started

Since List The Docs is writte using Flask it can be execute with the follwing
commands:

    export FLASK_APP=listthedocs
    flask run
    * Running on http://127.0.0.1:5000/

For Windows commandline use:

    set FLASK_APP=listthedocs

And for Windows Powershell use:

    $env:FLASK_APP="listthedocs"

### Configuration

The service can be configured with a Python file 'config.py' that can be placed in the app
["instance_path"](https://flask.palletsprojects.com/en/1.0.x/config/#instance-folders).

The *instance_path* can be customized by setting the *INSTANCE_PATH* to an absolute path.

The configuration is loaded from the 'config.py' in the *instance_path*:

- **DATABASE**: The path to the SQLite database. Defualt to *instance_path/listthedocs.sqlite*.
- **COPYRIGHT**: The copyright footer message. HTML is allowed.
- **TITLE**: The title of the web pages.
- **HEADER**: The header of the web page. HTML is allowed.
- **READONLY**: Set to true to disable the write REST APIs.

### Usage

The service provides a set of REST APIs to manage projects and versions.

#### Build and Host documentation

Before using the APIs, you should build the documentation (e.g. with Sphinx, MkDocs, 
Doxygen, ...) and host it on a web server. List The Docs does not actuallt provides 
docuemntation hosting services.

#### Collect documentations in List The Docs

After deploying a (new) project documentation on a hosting service, you can visualize
it in List The Docs:

1. Add the project (if not already present)
2. Add the version to the project

##### Add a project to List The Docs

Adding a project to List The Docs can be done using the following REST API:

    import requests

    requests.post(
        'http://localhost:5000/api/v1/projects', 
        json={
            'name': 'project-name',
            'description': 'The description of the project',
        }
    )


##### Add a documentation version link to List The Docs

Adding a version for a project documentation to List The Docs can be done 
using the following REST API:

    import requests

    requests.post(
        'http://localhost:5000/api/v1/projects/<project-name>/versions', 
        json={
            'name': '1.0.0',
            'url': 'http://www.example.com/doc/1.0.0/index.html',
        }
    )


### Python Client

To simplify the management of the projects, List The Docs provides a 
simple Python client:

    from listthedocs.client import ListTheDocs, Project, Version

    client = ListTheDocs()
    client.add_project(Project('project-name', 'description'))
    client.add_version(
        'project-name', 
        Version('1.0.0', 'http://www.example.com/doc/1.0.0/index.html')
    )
