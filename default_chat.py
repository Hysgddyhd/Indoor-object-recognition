import json
import os
from datetime import datetime
import asyncio
import AI_Assistant
import Robot_Assistant

SERVER_ENDPOINT = "http://127.0.0.1:5000/api/chat"
chatbot=Robot_Assistant.Robot_Assistant()

# Initialize a session object to store the conversation history
conversation = []  # Local storage for the conversation
user_name = "User123"  # Hardcoded user name for this example

async def chat():
    print("-" * 40)  # Print the separator before the conversation starts
    try:
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nExiting the conversation. Goodbye!")
                break

            # Append the user's input to the local conversation history
            conversation.append({"role": "user", "content": user_input})

            try:
                # Send the user's input to the server, including the hardcoded user name
                await chatbot.chat(user_input)
                
                chatbot_response = chatbot.response
                # Append the assistant's response to the local conversation history
                conversation.append({"role": "assistant", "content": chatbot_response})
                
                print("-" * 40)  # Separator after user input
                print("Deepseek: ")
                chatbot.printResponse()
                print("-" * 40)  # Separator after Streamy's response

            except ConnectionError:
                # Handle errors like the server being down
                print("Error: Could not connect to the server. Please check if the server is running.")

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nConversation interrupted by user.")

    finally:
        # Save the conversation when the chat ends or is interrupted
        print("Bye")
        print("Total token: ",chatbot.token_count)

        #save_conversation()


if __name__ == "__main__":
    asyncio.run(chat())
