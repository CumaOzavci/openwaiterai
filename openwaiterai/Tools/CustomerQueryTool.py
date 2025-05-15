import os
import ast
import time
from typing import Optional

from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase


class CustomerQueryTool(BaseTool):
    """
    A LangChain tool for querying restaurant management.
    """

    debug: bool = False
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
        """
        super().__init__()
        self.debug = debug
        db_host = os.getenv("OPENWAITERAI_DB_HOST", "localhost")
        db_port = os.getenv("OPENWAITERAI_DB_PORT", "5432")
        db_name = os.getenv("OPENWAITERAI_DB_NAME", "example")
        db_user = os.getenv("OPENWAITERAI_DB_USER", "user")
        db_password = os.getenv("OPENWAITERAI_DB_PASSWORD", "password")

        connection_string = (
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        self.sql_database = SQLDatabase.from_uri(connection_string)

    def _run(self, query: str) -> str:
        """
        Ask a customer question and return the result as a string.

        Args:
            query (str): The customer question

        Returns:
            str: The query result.
        """
        if self.debug:
            print(f"DEBUG: Submitting question: {query}")

        # Submit the question to the SQL database
        query_id = self._submit_query(query)
        if self.debug:
            print(f"DEBUG: Submitted question ID: {query_id}")

        # Get the result of the question
        timeout = 30  # seconds
        interval = 1  # seconds between polls
        start_time = time.time()

        query_result = None
        while True:
            # Poll for the result
            query_result = self._get_query_result(query_id)

            # Check if the result is ready
            if query_result is not None:
                break

            # Check for timeout
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Query {query_id} timed out after {timeout} seconds"
                )

            # Sleep for a while before checking again
            if self.debug:
                print(f"DEBUG: result for query {query_id} not ready, waiting...")
            time.sleep(interval)

        if self.debug:
            print(f"DEBUG: Query result: {query_result}")
        return query_result

    async def _arun(self, query: str) -> str:
        """
        Asynchronously execute an SQL query. Not implemented in this tool.

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
        result = self.sql_database.run(insert_sql)

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
        result = self.sql_database.run(select_sql)

        if isinstance(result, list) and result:
            query_result = result[0][0]
        else:
            query_result = result

        if query_result is None:
            return None

        return str(query_result).strip()
