from langchain import agents,tools
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage,AIMessage
from langchain_community.tools import ReadFileTool, YouTubeSearchTool
from langchain_community.agent_toolkits.steam.toolkit import SteamToolkit 

@tools.tool
def add(a: int, b: int)-> int:
    "Add the two imputs a plus b"
    return a+b

t = [add, ReadFileTool(root_dir="F:\Programing\IU_tests"),YouTubeSearchTool()]

def Calculate_tools(m :AIMessage):
    if m.tool_calls != None:
        messages.append(m)
        for tool in m.tool_calls:
            for ftool in t:
                if ftool.name == tool["name"]:
                    messages.append(ftool.invoke(tool))
    
        return messages
    else:
        return None
    

messages = [SystemMessage("You are a AI assistant")]
llm = ChatOllama(model="gemma4:e4b",temperature=0.8,verbose=True, reasoning=True).bind_tools(t)

first_step = RunnableLambda(lambda x : llm.invoke(x))
tool_step = RunnableLambda(lambda x : Calculate_tools(x))
tool_invoke_step = RunnableLambda(lambda x : llm.invoke(x) if x != None else x[-1])
append_step = RunnableLambda(lambda x: messages.append(x))
output_step = RunnableLambda(lambda x : messages[-1].content)

chain = first_step | tool_step | tool_invoke_step | append_step |output_step
while True:
    text = input(">> ")
    if text == "exit":
        break
    messages.append(HumanMessage(text))

    output = chain.invoke(messages)
    print(output)






