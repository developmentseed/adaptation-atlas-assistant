from uuid import uuid4


from aacp.agent import create_graph


async def _run_agent(query: str, thread_id: str | None = None):
    """Run the agent with a query and collect output at each step (async)."""

    if thread_id is None:
        thread_id = str(uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    graph = await create_graph()

    return await graph.ainvoke(
        {"messages": [{"role": "user", "content": query}]}, config
    )


async def test_aacp_agent():
    result = await _run_agent(
        "Make a plot about pecent change in cattle dry matter intake over all available countries"
    )

    assert "chart" in result
    assert "chart_data" in result
