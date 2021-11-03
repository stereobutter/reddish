from reddish._templating import parse_command_template


def test_positional_args():
    # (text, field, spec, conversion)
    assert [('', 0, '', None), ('', 1, '', None)] == list(parse_command_template('{}{}'))


def test_keyword_args():
    # (text, field, spec, conversion)
    assert [('', 'foo', '', None), ('', 'bar', '', None)] == list(parse_command_template('{foo}{bar}'))
