import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sampling_feature(fast_agent):
    """Test that the agent can process a simple prompt using directory-specific config."""
    # Use the FastAgent instance from the test directory fixture
    fast = fast_agent

    # Define the agent
    @fast.agent(name="foo", instruction="bar", servers=["sampling_test"])
    async def agent_function():
        async with fast.run() as agent:
            result = await agent("***CALL_TOOL sample {}")
            assert "hello, world" in result

    await agent_function()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sampling_passback(fast_agent):
    """Test that the agent can process a simple prompt using directory-specific config."""
    # Use the FastAgent instance from the test directory fixture
    fast = fast_agent

    # Define the agent
    @fast.agent(name="foo", instruction="bar", servers=["sampling_test"])
    async def agent_function():
        async with fast.run() as agent:
            result = await agent("***CALL_TOOL sample {to_sample='llmindset'}")
            assert "llmindset" in result

    await agent_function()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sampling_config(fast_agent):
    """Test that the agent can process a simple prompt using directory-specific config."""
    # Use the FastAgent instance from the test directory fixture
    fast = fast_agent
    async with fast.run():
        assert (
            "passthrough"
            == fast.context.config.mcp.servers["sampling_test"].sampling.model
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sampling_with_value(fast_agent):
    """Test that the agent can process a tool call with a specific value."""
    # Use the FastAgent instance from the test directory fixture
    fast = fast_agent

    # Define the agent
    @fast.agent(name="foo", instruction="bar", servers=["sampling_test"])
    async def agent_function():
        try:
            async with fast.run() as agent:
                # Use full server-tool name format with explicit value
                result = await agent(
                    '***CALL_TOOL sampling_test-sample {"to_sample": "test_value"}'
                )
                assert "test_value" in result
        except Exception as e:
            pytest.fail(f"Test failed with error: {str(e)}")

    await agent_function()
