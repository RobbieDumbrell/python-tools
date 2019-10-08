import logging

import psycopg2
import psycopg2.extensions


class PostgresConnector:

    def __init__(self, db_name: str, port: int = 5432, host: str = 'localhost', user: str = '', password: str = '') \
            -> None:
        self.db_name = db_name
        self.port = port
        self.host = host
        self.user = user
        self.password = password

    def __enter__(self) -> psycopg2.extensions.connection:
        self.connection = self.open_connection()
        logging.info(f'Connected to postgres database --> {self.db_name}.')
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close_connection(self.connection)

    def open_connection(self) -> psycopg2.extensions.connection:
        # use in a with statement if method being called in isolation to ensure connection closes
        logging.debug("Opening a postgres connection.")
        try:
            return psycopg2.connect(dbname=self.db_name,
                                    user=self.user,
                                    password=self.password,
                                    host=self.host,
                                    port=self.port)
        except psycopg2.Error as e:
            logging.error(f"Failed to open connection to postgres --> {e}")
            raise ConnectionError

    def close_connection(self, connection: psycopg2.extensions.connection) -> None:
        if connection:
            connection.close()
            logging.info(f'Connection terminated to postgres database --> {self.db_name}.')
        else:
            logging.warning(f'No postgres connection found to close.')
