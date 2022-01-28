"""This is an example of how to implement a plugin in squirrel."""


class Plugin:
    name = 'sample'
    description = 'Sample description'
    # If the plugin needs a non-builtin module,
    # it should be defined here. And the plugin manager will
    # import them automatically
    requires = (
        'non_builtin_lib',
        ...
    )

    def get_count(files) -> int:
        ...
