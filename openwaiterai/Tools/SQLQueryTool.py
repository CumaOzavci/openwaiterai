import os
from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase


class SQLQueryTool(BaseTool):
    """
    A LangChain tool for querying a SQL database.
    """

    name: str = "SQLQueryTool"
    description: str = (
        "A tool to query a SQL database. Provide an SQL query as input, and it will return the results."
    )

    def __init__(self):
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
        db_host = os.getenv("OPENWAITERAI_DB_HOST", "localhost")
        db_port = os.getenv("OPENWAITERAI_DB_PORT", "5432")
        db_name = os.getenv("OPENWAITERAI_DB_NAME", "example")
        db_user = os.getenv("OPENWAITERAI_DB_USER", "user")
        db_password = os.getenv("OPENWAITERAI_DB_PASSWORD", "password")

        connection_string = (
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        self.sql_database = SQLDatabase.from_uri(connection_string)
        self.connection = self.sql_database.engine.connect()

    def _run(self, query: str) -> str:
        """
        Execute an SQL query and return the result as a string.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        try:
            result = self.connection.execute(query).fetchall()
            return str(result)
        except Exception as e:
            return f"Error executing query: {str(e)}"

    async def _arun(self, query: str) -> str:
        """
        Asynchronously execute an SQL query. Not implemented in this tool.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        raise NotImplementedError("Async query is not supported.")
