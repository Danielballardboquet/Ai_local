from langchain_community.tools import ReadFileTool, YouTubeSearchTool, FileSearchTool, CopyFileTool, MoveFileTool, DeleteFileTool, playwright
from langchain_community.tools.wikipedia.tool import *
from langchain_community.tools.shell.tool import ShellTool
from langchain.tools import tool
import wikipedia
import json
from langchain_community.tools.file_management import ReadFileTool, WriteFileTool
import requests

email = "danielballardboquet01@gmail.com"

wikipedia.set_user_agent(f"Test ({email})")

api_wrapper = WikipediaAPIWrapper(
    top_k_results=1,
    doc_content_chars_max=1000
)
    
Tools = [
        {"Tool_name": "Wikipedia Tool", "Tool": WikipediaQueryRun(api_wrapper=api_wrapper), "Active": True},
        {"Tool_name": "Youtube Search", "Tool": YouTubeSearchTool(description="search for youtube videos associ" "the input to this tool should be" "the first part contains a person" "number that is the maximum numbe" "to return aka num_results. the s" "The links to the videos must be in markdown pattern: [link text](http://example.com)"), "Active": True},
        {"Tool_name": "File search", "Tool": FileSearchTool(), "Active": True},
        {"Tool_name": "File copy", "Tool": CopyFileTool(), "Active": True},
        {"Tool_name": "File move", "Tool": MoveFileTool(), "Active": True},
        {"Tool_name": "File delete", "Tool": DeleteFileTool(), "Active": True},
        {"Tool_name": "File read", "Tool": ReadFileTool(), "Active": True},
        {"Tool_name": "File write", "Tool": WriteFileTool(), "Active": True},
        {"Tool_name": "Navigate Tool", "Tool": playwright.NavigateTool(), "Active": True},
        {"Tool_name": "Extract Text Tool", "Tool": playwright.ExtractTextTool(), "Active": True},
        {"Tool_name": "Navigate Back Tool", "Tool": playwright.NavigateBackTool(), "Active": True},
        {"Tool_name": "Get Element Tool", "Tool": playwright.GetElementsTool(), "Active": True},
    ]
