import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Union

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("File Utilities")

@mcp.tool()
def list_directory(path: Optional[str] = None) -> Dict:
    """
    List files and directories in the specified path.
    If no path is provided, lists the current directory.
    """
    if path is None:
        path = os.getcwd()
    
    path_obj = Path(path)
    if not path_obj.exists():
        return {"error": f"Path does not exist: {path}"}
    
    if not path_obj.is_dir():
        return {"error": f"Path is not a directory: {path}"}
    
    try:
        items = []
        for item in path_obj.iterdir():
            items.append({
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size": os.path.getsize(item) if item.is_file() else None
            })
        
        return {
            "path": str(path_obj.absolute()),
            "items": items
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_file(file_path: str) -> Dict:
    """
    Read and return the contents of a file.
    """
    path_obj = Path(file_path)
    
    if not path_obj.exists():
        return {"error": f"File does not exist: {file_path}"}
    
    if not path_obj.is_file():
        return {"error": f"Path is not a file: {file_path}"}
    
    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "path": str(path_obj.absolute()),
            "content": content
        }
    except UnicodeDecodeError:
        return {
            "path": str(path_obj.absolute()),
            "error": "File is not a text file or has an unsupported encoding"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def copy_item(source: str, destination: str) -> Dict:
    """
    Copy a file or directory from source to destination.
    """
    src_path = Path(source)
    dst_path = Path(destination)
    
    if not src_path.exists():
        return {"error": f"Source does not exist: {source}"}
    
    try:
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)
            action = "copied file"
        else:
            shutil.copytree(src_path, dst_path)
            action = "copied directory"
        
        return {
            "success": True,
            "message": f"Successfully {action} from {source} to {destination}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def move_item(source: str, destination: str) -> Dict:
    """
    Move a file or directory from source to destination.
    """
    src_path = Path(source)
    
    if not src_path.exists():
        return {"error": f"Source does not exist: {source}"}
    
    try:
        shutil.move(source, destination)
        item_type = "directory" if src_path.is_dir() else "file"
        
        return {
            "success": True,
            "message": f"Successfully moved {item_type} from {source} to {destination}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_item(path: str, recursive: bool = False) -> Dict:
    """
    Delete a file or directory.
    If recursive is True, recursively delete directories.
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        return {"error": f"Path does not exist: {path}"}
    
    try:
        if path_obj.is_file():
            os.remove(path)
            return {
                "success": True,
                "message": f"Successfully deleted file: {path}"
            }
        else:
            if recursive:
                shutil.rmtree(path)
                return {
                    "success": True,
                    "message": f"Successfully deleted directory and its contents: {path}"
                }
            else:
                os.rmdir(path)
                return {
                    "success": True,
                    "message": f"Successfully deleted empty directory: {path}"
                }
    except IsADirectoryError:
        return {"error": f"Path is a directory, use recursive=True to delete: {path}"}
    except OSError as e:
        if "directory is not empty" in str(e).lower():
            return {"error": f"Directory is not empty, use recursive=True to delete: {path}"}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_directory(path: str, exist_ok: bool = False) -> Dict:
    """
    Create a new directory at the specified path.
    If exist_ok is True, don't raise an error if directory already exists.
    """
    try:
        os.makedirs(path, exist_ok=exist_ok)
        return {
            "success": True,
            "message": f"Successfully created directory: {path}"
        }
    except FileExistsError:
        return {"error": f"Directory already exists: {path}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def write_file(file_path: str, content: str, append: bool = False) -> Dict:
    """
    Write content to a file.
    If append is True, append to the file instead of overwriting.
    """
    mode = 'a' if append else 'w'
    
    try:
        path_obj = Path(file_path)
        if not path_obj.parent.exists():
            path_obj.parent.mkdir(parents=True)
            
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        action = "appended to" if append else "wrote"
        return {
            "success": True,
            "message": f"Successfully {action} file: {file_path}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_file_info(file_path: str) -> Dict:
    """
    Get metadata about a file or directory.
    """
    path_obj = Path(file_path)
    
    if not path_obj.exists():
        return {"error": f"Path does not exist: {file_path}"}
    
    try:
        info = {
            "path": str(path_obj.absolute()),
            "name": path_obj.name,
            "is_file": path_obj.is_file(),
            "is_directory": path_obj.is_dir(),
            "parent": str(path_obj.parent),
            "exists": path_obj.exists(),
        }
        
        if path_obj.is_file():
            info.update({
                "size": os.path.getsize(path_obj),
                "created": os.path.getctime(path_obj),
                "modified": os.path.getmtime(path_obj),
                "accessed": os.path.getatime(path_obj),
            })
            
        return info
    except Exception as e:
        return {"error": str(e)}

# Entry point for running the server
if __name__ == "__main__":
    import asyncio
    
    # Run the server
    asyncio.run(mcp.run())
