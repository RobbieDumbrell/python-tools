from setuptools import setup, find_packages

from tools.packaging.pipenv_tools import get_requirements_from_pipfile_lock, get_path_to_pipfile_lock

path_to_pipfile_lock = get_path_to_pipfile_lock()
pipfile_lock_requirements = get_requirements_from_pipfile_lock(path_to_pipfile_lock,
                                                               include_dev_packages=False)

setup(
    name='Generic Python Tools',
    author='Robbie Dumbrell',
    version='0.1',
    packages=find_packages(),
    install_requires=pipfile_lock_requirements
)