import os
import unittest

from tools.packaging.pipenv_tools import get_requirements_from_pipfile_lock


class TestPipenvTools(unittest.TestCase):
    test_path_to_pipfile_lock = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                             'pipfile_lock_fixtures/test_pipfile_lock')

    def test_get_requirements_from_pipfile_lock_default(self):
        expected_requirements = [
            "dep_1==1.1.1",
            "dep_2==2.2.2"
        ]
        requirements = get_requirements_from_pipfile_lock(self.test_path_to_pipfile_lock)
        self.assertListEqual(expected_requirements, requirements)

    def test_get_requirements_from_pipfile_lock_include_dev_packages(self):
        expected_requirements = [
            "dep_1==1.1.1",
            "dep_2==2.2.2",
            "dev_dep_1==1.1.1",
            "dev_dep_2==2.2.2",
        ]
        requirements = get_requirements_from_pipfile_lock(self.test_path_to_pipfile_lock,
                                                          include_dev_packages=True)
        self.assertListEqual(expected_requirements, requirements)

    def test_get_requirements_from_pipfile_lock_handles_no_pipfile_lock(self):
        with self.assertRaises(FileNotFoundError):
            with self.assertLogs() as log_watcher:
                get_requirements_from_pipfile_lock()

        assert log_watcher.records[0].msg == "Failed to find a Pipfile.lock to read package requirements."
        assert log_watcher.records[0].levelname == "ERROR"
