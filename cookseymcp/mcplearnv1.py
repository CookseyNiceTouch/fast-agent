from mcp.server.fastmcp import FastMCP
import asyncio
import sys

# Create an MCP server
mcp = FastMCP("TestServer")

# Add a calculator tool with error handling
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers and return the result"""
    try:
        return a + b
    except Exception as e:
        print(f"Error in add tool: {e}", flush=True)
        raise

# Add a greeting tool with error handling
@mcp.tool()
def greet(name: str, language: str = "en") -> str:
    """Return a personalized greeting in the specified language
    
    Args:
        name: The name to greet
        language: Language code (en, es, fr, etc.) - defaults to English
    """
    try:
        greetings = {
            "en": f"Hello, {name}!",
            "es": f"¡Hola, {name}!",
            "fr": f"Bonjour, {name}!",
            "de": f"Hallo, {name}!",
            "it": f"Ciao, {name}!"
        }
        
        return greetings.get(language.lower(), greetings["en"])
    except Exception as e:
        print(f"Error in greet tool: {e}", flush=True)
        raise

# Run the server
if __name__ == "__main__":
    # Print startup message before starting the server
    print("MCP server starting...", flush=True)
    
    try:
        # Start the server using stdio transport
        mcp.run()
    except KeyboardInterrupt:
        print("Server stopped by user.", flush=True)
    except Exception as e:
        print(f"Server error: {e}", flush=True)
        sys.exit(1) 