from json import dumps


def foo():
    print('1')
    print('2')
    print('3')


def foo2():
    print('1')
    print('2')
    print('3')


def wild_one():
    pass


def wild_two():
    # ``dumps`` is imported, so it must not be matched by wildcards
    return dumps({})


def _unrelated():
    pass


class Greeter:
    def hello(self):
        pass

    def help(self):
        pass

    def goodbye(self):
        pass

    @staticmethod
    def static():
        pass


class Other:
    def hello(self):
        pass
