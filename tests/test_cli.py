import sys
import os

# Dynamically add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openwaiterai import OpenWaiterAI

openwaiterai = OpenWaiterAI(
    model_name="gpt-4o-mini",
    system_instructions="./system_instructions.txt",
)

print("Welcome to the OpenWaiterAI Test CLI!")

while True:
    query = input("You: ")
    for response in openwaiterai.invoke(query):
        print(response)
