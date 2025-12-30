import openai
from openai import OpenAI
import json
import os
import tiktoken
import asyncio
from datetime import datetime
import AI_Assistant

class Robot_Assistant(AI_Assistant.Assistant):
    classes=['bed', 'bookshelf', 'chair', 'closet', 'door', 'fridge', 'sofa', 'table', 'trashBin']
    SYSTEM_PROMPT = """
        You are an LLM for a drone indoor navigation system.
        Your task: Parse human natural-language commands and produce a JSON command
        that will be executed by the drone’s local controller.

        You must:
        1. ONLY output valid JSON, no explanations.
        2. Follow this JSON schema:

        {
        "intent": "<string>",    // move | search | inspect | report
        "target": "<string>",    // one of: bed, bookshelf, chair, closet, door, fridge, sofa, table, trashBin or null
        "direction": "<string>", // forward/backward/left/right/up/down or null
        "distance_cm": <number>, // integer or null
        "metadata": { }          // extra task info if needed
        }

        3. If user request is ambiguous or impossible, return:
        {
        "intent": "error",
        "message": "<error_reason>"
        }

        4. NEVER output text outside JSON.
        """
    async def answer(self, message) -> dict:#chat without history
        print(self.get_token_count(message))
        self.response = self.client.chat.completions.create(
            model=AI_Assistant.MODEL_NAME,
            messages=[
                {"role": "system",
                 "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": message
                },
            ],
            stream=False,
            response_format={
                'type': 'json_object'
            }
        )
        
        answer = self.getResponse()
        self.responses.append({'answer': self.response})
        return answer
        

if __name__=='__main__':
    bot=Robot_Assistant()
    answer = asyncio.run(bot.answer("Who won the world series in 2020? Please respond in the json format {winner: ...}"))
    print(answer)