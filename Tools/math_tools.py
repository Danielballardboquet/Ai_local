from langchain.tools import tool

@tool
def temperature(location: str) -> int:
    "Return temperature in location as an int"
    return 69