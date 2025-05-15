import logging
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
    logger: logging.Logger = logging.getLogger(__name__)
    current_order_slip: List[Order] = []
    name: str = "SetOrderSlipTool"
    description: str = "A tool to set order slips in a restaurant management system."
    args_schema: Type[BaseModel] = SetOrderSlipToolInput

    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug
        self.logger.setLevel(logging.DEBUG)

    def _run(self, order_slip: List[Order]) -> List[Order]:
        """
        Set the current order slip and return it.

        Args:
            order_slip (List[Order]): The list of orders to set.

        Returns:
            List[Order]: The current order slip.
        """
        self.current_order_slip = order_slip

        if self.debug:
            self.logger.debug(f"Setting Order Slip: {order_slip}")

        return self.current_order_slip

    async def _arun(self, order_slip: List[Order]) -> List[Order]:
        """
        Asynchronously set the current order slip.
        """
        raise NotImplementedError("Async query is not supported.")
