from string import Formatter


def parse_command_template(format_string):

    auto_numbering_error = ValueError(
        'cannot switch from automatic field numbering to manual field specification')

    index = 0
    auto_numbering = None

    for literal_text, field_name, spec, conversion in Formatter().parse(format_string):

        if field_name.isdigit():
            if auto_numbering is True:
                raise auto_numbering_error
            auto_numbering = False

        if field_name == '':
            if auto_numbering is False:
                raise auto_numbering_error
            auto_numbering = True
            field_name = index
            index += 1

        yield literal_text, field_name, spec, conversion
