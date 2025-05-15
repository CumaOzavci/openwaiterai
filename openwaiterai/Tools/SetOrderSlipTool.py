from typing import Type, List

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class Order(BaseModel):
    id: int
    name: str
    quantity: int


class SetOrderSlipToolInput(BaseModel):
    order_slip: List[Order] = Field(
        description="List of ordered items",
        example=[
            {
                "id": 1,
                "name": "Pizza",
                "quantity": 2,
            },
            {
                "id": 2,
                "name": "Pasta",
                "quantity": 1,
            },
        ],
    )


class SetOrderSlipTool(BaseTool):
    """
    A LangChain tool for setting order slips in a restaurant management system.
    """

    debug: bool = False
    current_order_slip: List[Order] = []
    name: str = "SetOrderSlipTool"
    description: str = "A tool to set order slips in a restaurant management system."
    args_schema: Type[BaseModel] = SetOrderSlipToolInput

    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug

    def _run(self, order_slip: str) -> str:
        """
        Execute an SQL query and return the result as a string.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        self.current_order_slip = order_slip

        if self.debug:
            print(f"DEBUG: Setting Order Slip: {order_slip}")

        return self.current_order_slip

    async def _arun(self, query: str) -> str:
        """
        Asynchronously execute an SQL query. Not implemented in this tool.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        raise NotImplementedError("Async query is not supported.")
