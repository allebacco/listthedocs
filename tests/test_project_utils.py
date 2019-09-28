import pytest

from listthedocs.controllers.utils import validate_project_name, create_project_name
from listthedocs.controllers.exceptions import InvalidProjectName

@pytest.mark.parametrize('name,is_valid', [
    ('project', True),
    ('-project1', True),
    ('1pro-ject', True),
    ('_project_', True),
    ('344-project_3434-', True),
    ('344-Project_3434-', False),
    ('pr', False),
    ('projec/t', False),
    ('projec.t', False),
    ('proj,ect', False),
    ('proj:ect', False),
    ('proj;ect', False),
])
def test_validate_project_name(name, is_valid):

    if is_valid:
        validate_project_name(name)
    else:
        with pytest.raises(InvalidProjectName):
            validate_project_name(name)


@pytest.mark.parametrize('name,expected', [
    ('project', 'project'),
    ('344-Project_3434-', '344-project_3434-'),
    ('projec/t', 'projec-t'),
    ('projec.t', 'projec-t'),
    ('proj,ect', 'proj-ect'),
    ('proj:ect', 'proj-ect'),
    ('proj;ect', 'proj-ect'),
])
def test_create_project_name(name, expected):

    assert expected == create_project_name(name)
