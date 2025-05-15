from langchain.tools import BaseTool


class SetOrderSlipTool(BaseTool):
    """
    A LangChain tool for setting order slips in a restaurant management system.
    """

    debug: bool = False
    name: str = "SetOrderSlipTool"
    description: str = "A tool to set order slips in a restaurant management system. "

    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug
        self.order_slip = None

    def _run(self, query: str) -> str:
        """
        Execute an SQL query and return the result as a string.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        pass

    async def _arun(self, query: str) -> str:
        """
        Asynchronously execute an SQL query. Not implemented in this tool.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        raise NotImplementedError("Async query is not supported.")
