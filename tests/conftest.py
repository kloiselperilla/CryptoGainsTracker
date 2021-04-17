import sys


def pytest_configure(config):
    sys.path.insert(0, f'{config.rootdir}/src')
