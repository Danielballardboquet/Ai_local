from langchain_community.tools import ReadFileTool, YouTubeSearchTool
from langchain_community.tools.wikipedia.tool import *
import wikipedia

wikipedia.set_user_agent("Test (danielballardboquet01@gmail.com)")



api_wrapper = WikipediaAPIWrapper(
    top_k_results=1,
    doc_content_chars_max=1000
)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

Tools = [
        {"Tool_name": "Wikipedia Tool", "Tool": wiki_tool, "Active": True},
        {"Tool_name": "Youtube Search", "Tool": YouTubeSearchTool(), "Active": True},
    ]
