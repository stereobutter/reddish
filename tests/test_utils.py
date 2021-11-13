import pytest
from reddish._utils import uppercase_template_string


@pytest.mark.parametrize(
    "template, expected",
    [
        ('echo {data}', 'ECHO {data}'),
        ('echo', 'ECHO'),
        ('echo {}', 'ECHO {}')
    ]
)
def test_uppercase_template_string(template, expected):
    assert expected == uppercase_template_string(template)
