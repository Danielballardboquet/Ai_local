from langchain.tools import tool
import json
import wikipediaapi
from langchain_community.tools import wikipedia

@tool
def wikipedia_serach(title: str)-> str:
    "Search a wikipedia page from the title and retrive the page text"
    wiki = wikipediaapi.Wikipedia(user_agent="Test (danielballardboquet01@gmail.com)", language="en")
    print(title)
    return wiki.page(list(wiki.search(title).pages.keys())[0]).text4