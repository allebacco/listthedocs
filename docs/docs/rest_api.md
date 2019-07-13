# Rest APIs

List The Docs provides a set of REST APIs to manage the projects and the docuemntation versions.

Currently there is no authorization control, so anybody can interact with these APIs.

## Adding a Project

The following call will add a project:

    POST /api/v1/projects
    Content-Type: application/json

    {
        "name": "Project-Name",
        "description": "A not too long description of the project",
        "logo": "http://www.projectname.com/logo.png"
    }

The *logo* field is optional.

The response has the following format:

    HTTP/1.1 201 Created
    Content-Type: application/json
    
    {
        "name": "Project-Name",
        "description": "A not too long description of the project",
        "logo": "http://www.projectname.com/logo.png",
        "versions": []
    }


## Reading a Project

The following call will read a project named *Project-Name*:

    GET /api/v1/projects/Project-Name

If the project exists, the following response will returns:

    HTTP/1.1 200 Ok
    Content-Type: application/json
    
    {
        "name": "Project-Name",
        "description": "A not too long description of the project",
        "logo": "http://www.projectname.com/logo.png",
        "versions": []
    }

If the project does not exists, a 404 response code will be returned.

## Reading all the Projects

The following call will read all the projects:

    GET /api/v1/projects

The following response will returns:

    HTTP/1.1 200 Ok
    Content-Type: application/json
    
    [
        {
            "name": "Project-Name-1",
            "description": "A not too long description of the project 1",
            "logo": "http://www.projectname1.com/logo.png",
            "versions": []
        },
        {
            "name": "Project-Name-2",
            "description": "A not too long description of the project 2",
            "logo": "http://www.projectname2.com/logo.png",
            "versions": []
        }
    ]

## Updating a Project

It is possible to update the *description* or the *logo* of a Project using the following
call:

    PATCH /api/v1/projects/Project-Name
    Content-Type: application/json

    {
        "description": "An optional new description",
        "logo": "http://www.projectname.com/an-optional-new-logo.png"
    }

It is possible to update only the *logo* or only the *description*.

The response has the following format:

    HTTP/1.1 200 Ok
    Content-Type: application/json
    
    {
        "name": "Project-Name",
        "description": "An optional new description",
        "logo": "http://www.projectname.com/an-optional-new-logo.png",
        "versions": []
    }