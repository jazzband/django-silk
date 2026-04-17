import re

_pattern = re.compile(' +')
_file_location_pattern = re.compile(r'^(?P<src>.+):(?P<line>\d+)\((?P<func>.+)\)$')


def _normalize_function_location(function):
    """
    cProfile usually emits one of:
    - <string>:1(<module>)
    - {built-in method builtins.print}
    - package/module.py:123(function)

    Canonicalise real file locations to the angle-bracket form expected by the
    rest of the parser/tests while leaving builtins and already-normalised
    values untouched.
    """
    if not function or function[0] in '<{':
        return function

    match = _file_location_pattern.match(function)
    if match:
        return '<{src}>:{line}({func})'.format(**match.groupdict())
    return function


def parse_profile(output):
    """
    Parse the output of cProfile to a list of tuples.
    """
    if isinstance(output, str):
        output = output.split('\n')
    for i, line in enumerate(output):
        # ignore n function calls, total time and ordered by and empty lines
        line = line.strip()
        if i > 3 and line:
            columns = _pattern.split(line)[0:]
            function = _normalize_function_location(' '.join(columns[5:]))
            columns = columns[:5] + [function]
            yield columns
