import os
import ast
import time
import logging
from typing import Optional

from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase


class CustomerQueryTool(BaseTool):
    """
    A LangChain tool for querying restaurant management.
    """

    timeout: int = 30
    interval: int = 1
    debug: bool = False
    logger: logging.Logger = logging.getLogger(__name__)
    name: str = "CustomerQueryTool"
    description: str = (
        "A tool to query restaurant management. Provide a question as input, and it will return the answer of restaurant management."
    )
    sql_database: Optional[SQLDatabase] = None

    def __init__(self, debug: bool = False):
        """
        Initializes the SQLQueryTool with a database connection string from environment variables.

        The following environment variables are used:
        - OPENWAITERAI_DB_HOST: The database host.
        - OPENWAITERAI_DB_PORT: The database port.
        - OPENWAITERAI_DB_NAME: The database name.
        - OPENWAITERAI_DB_USER: The database username.
        - OPENWAITERAI_DB_PASSWORD: The database password.
        - OPENWAITERAI_QUERY_TIMEOUT: The timeout for the query in seconds.
        - OPENWAITERAI_POLL_INTERVAL: The interval for polling the query result in seconds.
        """
        super().__init__()
        self.debug = debug
        self.logger.setLevel(logging.DEBUG)

        # Configurable timeout and polling interval
        self.timeout = int(os.getenv("OPENWAITERAI_QUERY_TIMEOUT", "30"))
        self.interval = int(os.getenv("OPENWAITERAI_POLL_INTERVAL", "1"))

        # Database connection string
        db_host = os.getenv("OPENWAITERAI_DB_HOST", "localhost")
        db_port = os.getenv("OPENWAITERAI_DB_PORT", "5432")
        db_name = os.getenv("OPENWAITERAI_DB_NAME", "example")
        db_user = os.getenv("OPENWAITERAI_DB_USER", "user")
        db_password = os.getenv("OPENWAITERAI_DB_PASSWORD", "password")

        connection_string = (
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        try:
            self.sql_database = SQLDatabase.from_uri(connection_string)
        except Exception as e:
            self.logger.error("Failed to connect to database", exc_info=e)
            raise

    def _run(self, query: str) -> str:
        """
        Ask a customer question and return the result as a string.

        Args:
            query (str): The customer question

        Returns:
            str: The query result.
        """
        if self.debug:
            self.logger.debug("Submitting question: %s", query)

        # Submit the question to the SQL database
        query_id = self._submit_query(query)
        if self.debug:
            self.logger.debug("Submitted question ID: %s", query_id)

        # Get the result of the question
        start_time = time.time()

        query_result = None
        while True:
            # Poll for the result
            query_result = self._get_query_result(query_id)

            # Check if the result is ready
            if query_result is not None:
                break

            # Check for timeout
            if time.time() - start_time > self.timeout:
                raise TimeoutError(
                    f"Query {query_id} timed out after {self.timeout} seconds"
                )

            # Sleep for a while before checking again
            if self.debug:
                self.logger.debug("Result for query %s not ready, waiting...", query_id)
            time.sleep(self.interval)

        if self.debug:
            self.logger.debug("Query result: %s", query_result)
        return query_result

    async def _arun(self, query: str) -> str:
        """
        Asynchronously execute an SQL query.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        raise NotImplementedError("Async query is not supported.")

    def _submit_query(self, query: str) -> str:
        """
        Submit a query to the SQL database and return the result.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        safe_q = query.replace("'", "''")
        insert_sql = (
            f"INSERT INTO CustomerManagementQueries (question_text) "
            f"VALUES ('{safe_q}') RETURNING id;"
        )
        try:
            result = self.sql_database.run(insert_sql)
        except Exception as e:
            self.logger.error("Failed to submit query", exc_info=e)
            raise

        # Parse string result into Python object if needed
        if isinstance(result, str):
            try:
                result = ast.literal_eval(result)
            except Exception:
                pass

        # Extract the ID – `result` may be a list of tuples or a raw value
        if isinstance(result, list) and result:
            inserted_id = result[0][0]
        else:
            inserted_id = result
        return str(inserted_id).strip()

    def _get_query_result(self, query_id: str) -> str:
        """
        Get the result of a query by its ID.

        Args:
            query_id (str): The ID of the query.
        Returns:
            str: The query result.
        """
        select_sql = (
            f"SELECT answer_text FROM CustomerManagementQueries "
            f"WHERE id = {query_id};"
        )
        try:
            result = self.sql_database.run(select_sql)
        except Exception as e:
            self.logger.error("Failed to fetch query result", exc_info=e)
            raise

        # Parse string result into Python object if needed
        if isinstance(result, str):
            try:
                result = ast.literal_eval(result)
            except Exception:
                pass

        if isinstance(result, list) and result:
            query_result = result[0][0]
        else:
            query_result = result

        if query_result is None:
            return None

        return str(query_result).strip()
