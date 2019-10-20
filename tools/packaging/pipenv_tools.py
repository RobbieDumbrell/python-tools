import json
import logging
import os
from typing import List


def get_path_to_pipfile_lock() -> str:
    """
    Function to be called within setup.py, where both setup.py and Pipfile.lock sit in the same level of the project.
    :return: string containing the path to the Pipfile.lock
    """
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Pipfile.lock')


def get_requirements_from_pipfile_lock(path_to_pipfile_lock: str = None,
                                       include_dev_packages: bool = False) -> List[str]:
    """
    Function to read the package's requirements and return a list of strings with the versions as defined in the
    Pipfile.lock. This allows a package using Pipenv to be installed e.g. via GitHub as a Pipfile package itself, and
    all of its sub-dependencies are installed along with it.
    :param path_to_pipfile_lock: specified path to a Pipfile.lock - defaulted to None, presumes it will sit in same
                                root directory as the file the function is being called from.
    :param include_dev_packages: boolean to include or exclude dev only packages (defaulted to False)
    :return: List of strings that specify the requirements as per the Pipfile.lock.
    """

    if not path_to_pipfile_lock:  # then just assume setup.py is in the same directory as Pipfile.lock
        path_to_pipfile_lock = get_path_to_pipfile_lock()

    try:
        with open(path_to_pipfile_lock, 'r') as pipfile_lock:
            pipfile_lock_as_dict = json.load(pipfile_lock)
    except FileNotFoundError as e:
        logging.error("Failed to find a Pipfile.lock to read package requirements.")
        raise e

    requirements_as_dict_packages = pipfile_lock_as_dict['default']

    if include_dev_packages:
        requirements_as_dict_dev_packages = pipfile_lock_as_dict['develop']
        all_requirements_as_dict = dict(requirements_as_dict_packages, **requirements_as_dict_dev_packages)
    else:
        all_requirements_as_dict = requirements_as_dict_packages

    requirements = [req + all_requirements_as_dict[req]['version'] for req in all_requirements_as_dict]

    return requirements
