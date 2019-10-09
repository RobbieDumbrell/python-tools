import unittest

import testing.postgresql

from tools.db.postgres.postgres_connector import PostgresConnector


class TestPostgresConnector(unittest.TestCase):
    PGFactory = testing.postgresql.PostgresqlFactory(port=5678,
                                                     cache_initialized_db=True)

    # ensures that the postgres database created and cached for this module is removed before next test module starts
    def tearDownModule(self):
        self.pg.clear_cache()

    def setUp(self):
        self.pg = self.PGFactory()
        self.pg_connector = PostgresConnector(db_name='test',
                                              port=5678,
                                              user='postgres')

    def tearDown(self):
        self.pg.stop()

    def test_open_connection_successful(self):
        good_pg_connection = self.pg_connector.open_connection()
        assert good_pg_connection is not None
        assert good_pg_connection.closed == 0

    def test_open_connection_raises_and_logs_error_on_failure(self):
        bad_pg_connection = PostgresConnector(db_name='test', port=5678, user='bad_user')
        with self.assertRaises(ConnectionError):
            with self.assertLogs() as log_watcher:
                bad_pg_connection.open_connection()

        assert log_watcher.records[0].msg == 'Failed to open connection to postgres -->' \
                                             ' FATAL:  role "bad_user" does not exist\n'
        assert log_watcher.records[0].levelname == 'ERROR'

    def test_close_connection_successful(self):
        good_pg_connection = self.pg_connector.open_connection()
        assert good_pg_connection.closed == 0
        self.pg_connector.close_connection(good_pg_connection)
        assert good_pg_connection.closed == 1

    def test_close_connection_raises_and_logs_error_on_failure(self):
        with self.assertLogs() as log_watcher:
            self.pg_connector.close_connection(None)

        assert log_watcher.records[0].msg == 'No postgres connection found to close.'
        assert log_watcher.records[0].levelname == 'WARNING'

    def test_opens_and_closes_connection_as_context_manager(self):
        with self.assertLogs() as log_watcher:
            with PostgresConnector(db_name='test',
                                   port=5678,
                                   user='postgres') as pg_conn:
                assert pg_conn is not None
                assert pg_conn.closed == 0
                assert log_watcher.records[0].msg == 'Connected to postgres database --> test.'

        assert pg_conn.closed == 1
        assert log_watcher.records[1].msg == 'Connection terminated to postgres database --> test.'
