from langchain_openai import ChatOpenAI

from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.runnables.history import RunnableWithMessageHistory


class OpenWaiterAI:
    def __init__(
        self,
        model_name: str,
        system_instructions: str,
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ):
        # Model settings
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=None,
            max_retries=2,
        )

        # Initialize system message
        try:
            with open(system_instructions, "r", encoding="utf-8") as file:
                self.system_instructions = file.read()
        except IOError as e:
            print(f"Error reading file {system_instructions}: {e}")

        self.system_message = self.system_instructions

        # Initialize history
        self.session_store = {}
        self.session_id = "openwaiterai"

        # Add system message
        self.session_store[self.session_id] = InMemoryChatMessageHistory()
        self.session_store[self.session_id].add_message(
            SystemMessage(self.system_message)
        )

        self.model_with_history = RunnableWithMessageHistory(
            self.llm,
            self.get_session_history,
        )

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.session_store:
            self.session_store[session_id] = InMemoryChatMessageHistory()
            self.session_store[self.session_id].add_message(
                SystemMessage(self.system_message)
            )
        return self.session_store[session_id]

    def invoke(self, prompt: str) -> BaseMessage:
        response = self.model_with_history.invoke(
            [HumanMessage(prompt)],
            config={"configurable": {"session_id": self.session_id}},
        )

        return response.content
