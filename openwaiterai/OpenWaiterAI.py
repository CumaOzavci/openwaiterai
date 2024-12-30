from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from .Tools import SQLQueryTool


class OpenWaiterAI:
    def __init__(
        self,
        model_name: str,
        system_instructions: str,
        temperature: float = 1.0,
        max_tokens: int = 4096,
        debug: bool = False,
    ):
        self.debug = debug

        # Tools
        sql_tool = SQLQueryTool(debug=self.debug)
        self.tools = [sql_tool]

        # Initialize system message
        try:
            with open(system_instructions, "r", encoding="utf-8") as file:
                self.system_instructions = file.read()
        except IOError as e:
            print(f"Error reading file {system_instructions}: {e}")

        self.schema_description = sql_tool.get_schema_description()
        self.menu_description = sql_tool.get_menu_description()

        self.system_message = (
            self.system_instructions
            + "\n\n"
            + self.schema_description
            + "\n\n"
            + self.menu_description
        )

        # Model settings
        self.model = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=None,
            max_retries=2,
        )

        self.model = self.model.bind_tools(self.tools)

        # Initialize history
        self.session_store = {}
        self.session_id = "openwaiterai"

        # Add system message
        self.session_store[self.session_id] = InMemoryChatMessageHistory()
        self.session_store[self.session_id].add_message(
            SystemMessage(self.system_message)
        )

        self.model_with_history = RunnableWithMessageHistory(
            self.model,
            self.get_session_history,
        )

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.session_store:
            self.session_store[session_id] = InMemoryChatMessageHistory()
            self.session_store[self.session_id].add_message(
                SystemMessage(self.system_message)
            )
        return self.session_store[session_id]

    def invoke(
        self,
        prompt: str = None,
        messages: List[BaseMessage] = None,
    ):
        # Invoke the model with the appropriate input
        input_messages = [HumanMessage(prompt)] if prompt else messages
        response = self.model_with_history.invoke(
            input_messages,
            config={"configurable": {"session_id": self.session_id}},
        )

        yield response

        # Handle tool calls if present in the response
        if response.tool_calls:
            tool_responses = []

            for tool_call in response.tool_calls:
                # Find the corresponding tool and invoke it
                matching_tool = next(
                    (tool for tool in self.tools if tool.name == tool_call["name"]),
                    None,
                )

                if matching_tool:
                    tool_response = matching_tool.invoke(tool_call)
                    tool_responses.append(tool_response)
                    yield tool_response

            # Recursively invoke with the tool responses
            yield from self.invoke(messages=tool_responses)
