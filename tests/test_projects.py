import pytest


def test_get_missing_project(client):

    response = client.get('/api/v2/projects/test_project')
    assert response.status_code == 404


def test_get_project_when_none_exists(client):

    response = client.get('/api/v2/projects')
    assert response.status_code == 200

    projects = response.get_json()
    assert len(projects) == 0


def test_add_project_creates_and_returns_the_project(client):

    response = client.post('/api/v2/projects', json={'title': 'Test Project', 'description': 'A very long string'})
    assert response.status_code == 201

    project = response.get_json()
    assert project['name'] == 'test-project'
    assert project['title'] == 'Test Project'
    assert project['description'] == 'A very long string'
    assert 'logo' in project


def test_get_project_returns_the_project(client):

    response = client.post('/api/v2/projects', json={'title': 'Test Project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.get('/api/v2/projects/test-project')
    assert response.status_code == 200

    project = response.get_json()
    assert project['name'] == 'test-project'
    assert project['title'] == 'Test Project'
    assert project['description'] == 'A very long string'
    assert 'logo' in project


def test_get_projects_returns_all_the_projects(client):

    response = client.post('/api/v2/projects', json={'title': 'Test Project 1', 'description': 'Tests description 1'})
    assert response.status_code == 201

    response = client.post('/api/v2/projects', json={'title': 'Test Project 2', 'description': 'Tests description 2'})
    assert response.status_code == 201

    response = client.get('/api/v2/projects')
    assert response.status_code == 200

    projects = response.get_json()
    assert isinstance(projects, list)
    assert projects[0]['name'] == 'test-project-1'
    assert projects[0]['title'] == 'Test Project 1'
    assert projects[0]['description'] == 'Tests description 1'
    assert projects[1]['name'] == 'test-project-2'
    assert projects[1]['title'] == 'Test Project 2'
    assert projects[1]['description'] == 'Tests description 2'


def test_update_project_description(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.patch('/api/v2/projects/test_project', json={'description': 'Short string'})
    assert response.status_code == 200

    project = response.get_json()
    assert 'name' in project
    assert project['name'] == 'test_project'
    assert project['title'] == 'test_project'
    assert project['description'] == 'Short string'
    assert 'logo' in project


def test_update_project_logo(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.patch('/api/v2/projects/test_project', json={'logo': 'image.jpg'})
    assert response.status_code == 200

    project = response.get_json()
    assert project['name'] == 'test_project'
    assert project['title'] == 'test_project'
    assert project['description'] == 'A very long string'
    assert project['logo'] == 'image.jpg'


def test_update_project_title(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.patch('/api/v2/projects/test_project', json={'title': 'Test Project'})
    assert response.status_code == 200

    project = response.get_json()
    assert project['name'] == 'test_project'
    assert project['title'] == 'Test Project'
    assert project['description'] == 'A very long string'
    assert 'logo' in project


def test_delete_project(client):

    # Add a project
    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    # Add a version
    response = client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/index.html'}
    )
    assert response.status_code == 201

    response = client.delete('/api/v2/projects/test_project')
    assert response.status_code == 200

    response = client.get('/api/v2/projects/test_project')
    assert response.status_code == 404


def test_add_version(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/index.html'}
    )
    assert response.status_code == 201

    project = response.get_json()
    assert project['name'] == 'test_project'
    assert project['title'] == 'test_project'
    assert project['description'] == 'A very long string'
    assert 'logo' in project
    assert project['versions'][0]['name'] == '1.0.0'
    assert project['versions'][0]['url'] == 'www.example.com/index.html'


def test_remove_version(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201


    # Add multiple versions
    response = client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/1.0.0/index.html'}
    )
    assert response.status_code == 201

    response = client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '2.0.0', 'url': 'www.example.com/2.0.0/index.html'}
    )
    assert response.status_code == 201

    # Remove a version
    response = client.delete('/api/v2/projects/test_project/versions/2.0.0')
    assert response.status_code == 200

    response = client.get('/api/v2/projects/test_project')
    assert response.status_code == 200

    project = response.get_json()
    assert project['name'] == 'test_project'
    assert project['title'] == 'test_project'
    assert project['description'] == 'A very long string'
    assert 'logo' in project
    assert isinstance(project['versions'], list)
    assert len(project['versions']) == 1
    assert project['versions'][0]['name'] == '1.0.0'
    assert project['versions'][0]['url'] == 'www.example.com/1.0.0/index.html'


def test_update_version_link(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project', 'description': 'A very long string'})
    assert response.status_code == 201

    # Add multiple versions
    response = client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/1.0.0/index.html'}
    )
    assert response.status_code == 201

    response = client.post(
        '/api/v2/projects/test_project/versions',
        json={'name': '2.0.0', 'url': 'www.example.com/2.0.0/index.html'}
    )
    assert response.status_code == 201

    # Patch a version link
    response = client.patch(
        '/api/v2/projects/test_project/versions/2.0.0',
        json={'url': 'www.newexample.com/2.0.0/index.html'}
    )
    assert response.status_code == 200

    project = response.get_json()
    assert project['name'] == 'test_project'
    assert project['title'] == 'test_project'
    assert project['description'] == 'A very long string'
    assert 'logo' in project
    assert isinstance(project['versions'], list)
    assert project['versions'][0]['name'] == '1.0.0'
    assert project['versions'][0]['url'] == 'www.example.com/1.0.0/index.html'
    assert project['versions'][1]['name'] == '2.0.0'
    assert project['versions'][1]['url'] == 'www.newexample.com/2.0.0/index.html'


def test_add_same_version_name_to_different_projects(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project1', 'description': 'A very long string'})
    assert response.status_code == 201

    response = client.post('/api/v2/projects', json={'title': 'test_project2', 'description': 'A very long string'})
    assert response.status_code == 201

    # Add version 1.0.0 to test_project1
    response = client.post(
        '/api/v2/projects/test_project1/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/1.0.0/index.html'}
    )
    assert response.status_code == 201

    # Add version 1.0.0 to test_project2
    response = client.post(
        '/api/v2/projects/test_project2/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/1.0.0/index.html'}
    )
    assert response.status_code == 201


def test_add_same_version_name_multiple_time_to_project_fails(client):

    response = client.post('/api/v2/projects', json={'title': 'test_project1', 'description': 'A very long string'})
    assert response.status_code == 201

    # Add version 1.0.0 to test_project1
    response = client.post(
        '/api/v2/projects/test_project1/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/1.0.0/index.html'}
    )
    assert response.status_code == 201

    # Add version 1.0.0 to test_project1 twice, fail
    response = client.post(
        '/api/v2/projects/test_project1/versions',
        json={'name': '1.0.0', 'url': 'www.example.com/1.0.0/index.html'}
    )
    assert response.status_code == 409
