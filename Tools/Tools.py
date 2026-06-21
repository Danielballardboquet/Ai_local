from langchain_community.tools import ReadFileTool, YouTubeSearchTool, FileSearchTool, CopyFileTool, MoveFileTool, DeleteFileTool
from langchain_community.tools.wikipedia.tool import *
from langchain_community.tools.shell.tool import ShellTool
import wikipedia
import json
from langchain_community.tools.file_management import ReadFileTool, WriteFileTool
email = "danielballardboquet01@gmail.com"

wikipedia.set_user_agent(f"Test ({email})")

api_wrapper = WikipediaAPIWrapper(
    top_k_results=1,
    doc_content_chars_max=1000
)

Tools = [
        {"Tool_name": "Wikipedia Tool", "Tool": WikipediaQueryRun(api_wrapper=api_wrapper), "Active": True},
        {"Tool_name": "Youtube Search", "Tool": YouTubeSearchTool(), "Active": True},
        {"Tool_name": "File search", "Tool": FileSearchTool(), "Active": True},
        {"Tool_name": "File copy", "Tool": CopyFileTool(), "Active": True},
        {"Tool_name": "File move", "Tool": MoveFileTool(), "Active": True},
        {"Tool_name": "File delete", "Tool": DeleteFileTool(), "Active": True},
        {"Tool_name": "File read", "Tool": ReadFileTool(), "Active": True},
        {"Tool_name": "File write", "Tool": WriteFileTool(), "Active": True},
    ]
