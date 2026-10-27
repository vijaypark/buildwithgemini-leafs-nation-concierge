import asyncio
from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agent import root_agent

async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(user_id="user_1", app_name="simple-agent")
    runner = Runner(agent=root_agent, session_service=session_service, app_name="simple-agent")

    user_prompt = "What's the weather and current time in San Francisco?"
    print(f"\nUser: {user_prompt}\n")

    message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_prompt)]
    )

    print("Agent: ", end="", flush=True)
    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=message
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    asyncio.run(main())
