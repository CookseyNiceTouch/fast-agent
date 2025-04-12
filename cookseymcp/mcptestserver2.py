from mcp.server.fastmcp import FastMCP, Context

# Create a named MCP server
mcp = FastMCP("Test Server")

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Add a static resource
@mcp.resource("info://about")
def get_info() -> str:
    """Information about this test server"""
    return "This is a simple MCP test server for demonstration purposes."

# Add a calculator tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# Define a simple prompt template
@mcp.prompt()
def calculator_prompt(operation: str = "add") -> str:
    """A prompt for using the calculator"""
    return f"""You are a helpful calculator assistant.
The user wants to perform a {operation} operation.
Please help them calculate the result."""

# Run the server when this script is executed directly
if __name__ == "__main__":
    import sys
    
    # If no arguments, run in development mode
    if len(sys.argv) == 1:
        import asyncio
        from mcp.server.cli.dev import dev_server
        
        asyncio.run(dev_server(mcp))
    else:
        # Otherwise, use the CLI commands
        mcp.run()
