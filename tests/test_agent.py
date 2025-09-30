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
        "Make a plot about cattle heatstress over all available regions"
    )

    assert "dataset" in result
    dataset = result["dataset"]

    assert dataset.metadata["key"] == "cattle_hs"


"Code: To determine how many times the letter 'r' appears in the word \"strawberry,\" let's go through each letter one by one:\n\n1. S\n2. T\n3. R\n4. A\n5. W\n6. B\n7. E\n8. R\n9. R\n10. Y\n\nNow, let's count the 'r's:\n\n- The 3rd letter is 'r' (1st 'r')\n- The 8th letter is 'r' (2nd 'r')\n- The 9th letter is 'r' (3rd 'r')\n\nSo, the letter 'r' appears **3 times** in the word \"strawberry.\", Result: Execution(Results: [], Logs: Logs(stdout: [], stderr: []), Error: ExecutionError(name='SyntaxError', value='unterminated string literal (detected at line 6) (2479195644.py, line 6)', traceback='  Cell In[1], line 6\\n    To determine how many times the letter \\'r\\' appears in the word \"strawberry,\" let\\'s go through each letter one by one:\\n                                                                                    ^\\nSyntaxError: unterminated string literal (detected at line 6)\\n'))"
