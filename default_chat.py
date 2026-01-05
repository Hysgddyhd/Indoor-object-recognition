import json
import asyncio
from openai import OpenAI
from Robot_Assistant import Robot_Assistant



# Initialize the chatbot
chatbot = Robot_Assistant()

# Initialize a session object to store the conversation history
conversation = []  # Local storage for the conversation
user_name = "User123"  # Hardcoded user name for this example


async def chat():
    """Main chat loop"""
    print("-" * 40)  # Print the separator before the conversation starts
    print("🤖 Robot Assistant - Ready!")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.")
    print("-" * 40)

    try:
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nExiting the conversation. Goodbye!")
                break

            # Append the user's input to the local conversation history
            conversation.append({"role": "user", "content": user_input})

            try:
                # Send the user's input to the chatbot
                response_data = await chatbot.chat(user_input)

                # Append the assistant's response to the local conversation history
                conversation.append({"role": "assistant", "content": json.dumps(response_data)})

                print("-" * 40)  # Separator after user input
                print("🤖 Assistant:")

                # Display the response in a formatted way
                if response_data.get("intent") == "error":
                    print(f"❌ Error: {response_data.get('message', 'Unknown error')}")
                else:
                    print(f"✅ Intent: {response_data.get('intent')}")
                    if response_data.get('target'):
                        print(f"🎯 Target: {response_data.get('target')}")
                    if response_data.get('direction'):
                        print(f"🧭 Direction: {response_data.get('direction')}")
                    if response_data.get('distance_cm'):
                        print(f"📏 Distance: {response_data.get('distance_cm')} cm")
                    if response_data.get('metadata'):
                        print(f"📝 Metadata: {json.dumps(response_data.get('metadata'), indent=2)}")

                print("-" * 40)  # Separator after response

            except ConnectionError:
                # Handle errors like the server being down
                print("❌ Error: Could not connect to the server. Please check if Ollama is running.")
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\nConversation interrupted by user.")

    finally:
        # Save the conversation when the chat ends or is interrupted
        print("\n" + "=" * 40)
        print("👋 Bye!")
        print(f"📊 Total tokens processed: {chatbot.token_count}")
        print(f"💬 Total messages exchanged: {len(conversation)}")
        print("=" * 40)

        # Optional: Save conversation to file
        save_conversation()


def save_conversation():
    """Save the conversation history to a JSON file"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "user": user_name,
                "timestamp": timestamp,
                "conversation": conversation,
                "total_tokens": chatbot.token_count
            }, f, indent=2, ensure_ascii=False)

        print(f"💾 Conversation saved to: {filename}")
    except Exception as e:
        print(f"⚠️  Failed to save conversation: {str(e)}")


if __name__ == "__main__":
    asyncio.run(chat())
