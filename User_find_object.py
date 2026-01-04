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
<<<<<<< HEAD
                # Send the user's input to the server
                response_data = await chatbot.answer(user_input)
                
                # Update local conversation history
                chatbot_response = chatbot.response.choices[0].message.content
                conversation.append({"role": "assistant", "content": chatbot_response})
                
                print("-" * 40)
                # Display the friendly response to the user
                chatbot.printResponse()
                
                # Extract and process the command
                if "command" in response_data and response_data["command"]:
                    command = response_data["command"]
                    intent = command.get("intent")
                    
                    # Logic to handle different intents
                    if intent == "guide":
                        # Guide is handled by the text reply, no physical action needed
                        pass 
                    elif intent == "check_status":
                        # Placeholder for actual status check logic
                        # In a real scenario, this would query the drone's telemetry
                        print(f"\n[System] Drone Status: Battery 85%, Location (0,0,0), Mode: IDLE")
                    elif intent == "view_camera":
                        # Placeholder for camera feed logic
                        print(f"\n[System] Opening camera feed...")
                        # logic to open video stream would go here
                    elif intent == "search":
                        target = command.get("target")
                        print(f"\n[System] Initiating search protocol for: {target}")
                        # Call search function here
                    elif intent == "organize":
                         target = command.get("target")
                         print(f"\n[System] Starting organization task for: {target}")
                         # Call organize function here
                    elif intent == "move":
                        direction = command.get("direction")
                        distance = command.get("distance_cm")
                        print(f"\n[System] Moving {direction} by {distance}cm")
                        # Call movement function here
                    elif intent == "stop":
                        print(f"\n[System] Emergency Stop Triggered")
                        # Call stop function here
                
                print("-" * 40)
=======
                # Send the user's input to the server, including the hardcoded user name
                await chatbot.answer(user_input)
                
                chatbot_response = chatbot.response
                # Append the assistant's response to the local conversation history
                conversation.append({"role": "assistant", "content": chatbot_response})
                
                print("-" * 40)  # Separator after user input
                print("Deepseek: ")
                chatbot.printResponse()
                print("-" * 40)  # Separator after Streamy's response
>>>>>>> 6b3d3f6b5d8a5ad1120d6a6d362fb16fccbee894

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
