from string import Formatter


def parse_command_template(format_string):

    auto_numbering_error = ValueError(
        'cannot switch from automatic field numbering to manual field specification')

    index = 0
    auto_numbering = None

    for literal_text, field_name, spec, conversion in Formatter().parse(format_string):
        if field_name is not None:
            if field_name.isdigit():
                field_name = int(field_name)
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


def format_original_field(field_name, spec, conversion):
    return (
        f'{field_name}'
        + (f'!{conversion}' if conversion is not None else '')
        + (f':{spec}' if spec != '' else '')
    )


def format_error_message(missing_positional_args, missing_keyword_args):

    if missing_positional_args:
        n = missing_positional_args
        return f"Command() missing {n} required positional argument{'s' if n > 1 else ''}"

    if missing_keyword_args:
        n = len(missing_keyword_args)
        first, *rest = (f"'{key}'" for key in missing_keyword_args)
        if rest:
            *most, last = rest
            missing_fields = f"{', '.join([first, *most])} and {last}"
        else:
            missing_fields = first
        return f"Command() missing {n} required keyword-only argument{'s' if n > 1 else ''}: {missing_fields}"


def apply_template(format_string, *args, **kwargs):

    missing_positional_args = 0
    missing_keyword_args = set()

    data = []
    for literal_text, field, spec, conversion in parse_command_template(format_string):

        # extract literal commands
        for command in literal_text.strip().split(' '):
            if command:
                data.append(command)

        # process templated field
        if field is not None:

            if spec != '' or conversion is not None:
                raise ValueError(f'{format_original_field(field, spec, conversion)} is not valid as placeholder')

            if isinstance(field, int):  # positonal argument
                try:
                    value = args[field]
                except IndexError:
                    missing_positional_args += 1
                    continue
            else:  # keyword argument
                try:
                    value = kwargs[field]
                except KeyError:
                    missing_keyword_args.add(field)
                    continue

            data.append(value)

    if missing_positional_args or missing_keyword_args:
        raise TypeError(format_error_message(missing_positional_args, missing_keyword_args))

    return data
