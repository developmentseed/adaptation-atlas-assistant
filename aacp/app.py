import chainlit as cl
from aacp.agent import create_graph
import plotly.graph_objects as go
import json


@cl.on_chat_start
async def start():
    """Initialize the agent when chat starts"""
    graph = await create_graph()
    cl.user_session.set("graph", graph)
    cl.user_session.set("thread_id", "default_thread")
    await cl.Message(
        content="Hello! Ask me about climate adaptation data from the Adaptation Atlas."
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    graph = cl.user_session.get("graph")
    thread_id = cl.user_session.get("thread_id")

    config = {"configurable": {"thread_id": thread_id}}

    # Create a message to update with streaming content
    msg = cl.Message(content="")

    # Stream agent updates
    async for update in graph.astream(
        {"messages": [("user", message.content)]}, config=config, stream_mode="updates"
    ):
        for node, values in update.items():
            # Show raw state updates for each tool
            if values:  # Only show if there are actual updates
                update_json = json.dumps(values, indent=2, default=str)
                await cl.Message(
                    content=f"**{node}** state update:\n```json\n{update_json}\n```",
                    author="System",
                ).send()

            # Handle text messages
            if "messages" in values:
                last_msg = values["messages"][-1]
                if hasattr(last_msg, "content") and last_msg.content:
                    msg.content = last_msg.content
                    await msg.update()

            # Handle charts
            if "chart" in values and values["chart"]:
                chart_data = values["chart"]
                fig = go.Figure(chart_data)

                # Send chart as a separate element
                elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
                msg.elements = elements
                await msg.update()

    # Final send
    await msg.send()
