from setuptools import setup, find_packages


def version():
    with open('gstat_classroom/VERSION') as f:
        return f.read().strip()


def readme():
    with open('README.md') as f:
        return f.read().strip()


def requirements():
    with open('requirements.txt') as f:
        return f.read().split('\n')


setup(
    name='gstat-classroom',
    author='Mirko Mälicke',
    author_email='mirko.maelicke@kit.edu',
    license='MIT License',
    install_requires=requirements(),
    version=version()
)