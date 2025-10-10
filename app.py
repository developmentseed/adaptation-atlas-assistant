import chainlit
from chainlit import Message

import atlas_assistant.settings
from atlas_assistant.agent import create_graph


@chainlit.on_chat_start
async def start():
    settings = atlas_assistant.settings.get_settings()
    graph = await create_graph(settings)
    chainlit.user_session.set("graph", graph)
    chainlit.user_session.set("thread_id", "default_thread")


@chainlit.on_message
async def main(message: Message):
    graph = chainlit.user_session.get("graph")
    assert graph
    thread_id = chainlit.user_session.get("thread_id")

    config = {"configurable": {"thread_id": thread_id}}

    # Stream agent updates
    async for update in graph.astream(
        {"messages": [("user", message.content)]}, config=config, stream_mode="updates"
    ):
        for key, value in update.items():
            if key in ["agent", "tools"]:
                for message in value["messages"]:
                    if message.content:
                        _ = await Message(message.content).send()
