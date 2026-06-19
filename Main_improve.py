import wikipedia
from langchain import agents,tools
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage,AIMessage
from langchain_community.tools import ReadFileTool, YouTubeSearchTool
from langchain_community.tools.wikipedia.tool import *
from langchain_community.agent_toolkits.steam.toolkit import SteamToolkit 
from typing import List, Dict
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QMouseEvent, QClipboard,QGuiApplication
from markdown2 import markdown


wikipedia.set_user_agent("Test (danielballardboquet01@gmail.com)")

def Calculate_tools(m :AIMessage, messages,t):
    if m.tool_calls != None:
        messages.append(m)
        for tool in m.tool_calls:
            for ftool in t:
                if ftool.name == tool["name"]:
                    messages.append(ftool.invoke(tool))
    
        return messages
    else:
        return None

api_wrapper = WikipediaAPIWrapper(
    top_k_results=1,
    doc_content_chars_max=1000
)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

Tools = [
        {"Tool_name": "Wikipedia Tool", "Tool": wiki_tool, "Active": True},
        {"Tool_name": "Youtube Search", "Tool": YouTubeSearchTool(), "Active": True},
    ]


class Message(QLabel):
    def __init__(self,text, color, Text_color = "black", font_size = 12, font_name = ""):
        text = markdown(text)
        super().__init__(text=text)
        self.setStyleSheet(f"background-color:{color}; color: {Text_color}; font-size: {font_size}; border-radius:10px; padding:20px")
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        self.clip = QGuiApplication.clipboard()
    def mousePressEvent(self, ev: QMouseEvent ):
        if ev.button() == Qt.RightButton:
            self.clip.setText(self.text())
        

class Menu(QDialog):
    def __init__(self, Font_size:int, Font:str, AI_color : QColor, User_color : QColor, Text_color : QColor):
        super().__init__()
        self.lay = QGridLayout()
        self.apply_bool = False

        self.bAI_color = AI_color
        self.bUser_color = User_color
        self.bFont = Font
        self.bFont_size = Font_size
        self.bText_color = Text_color

        self.AI_color = AI_color
        self.User_color = User_color
        self.Font = Font
        self.Font_size = Font_size
        self.Text_color = Text_color

        self.font_label = QLabel("Font")
        self.AI_label = QLabel("AI color")
        self.User_label = QLabel("User Color")

        self.font = QFontComboBox()
        self.AI_color_b = QPushButton()
        self.User_color_b = QPushButton()
        self.wText_color = QPushButton()
        self.wfont_size = QSpinBox()
        self.wfont_size.setValue(self.Font_size)

        self.AI_color_b.setStyleSheet(f"background-color: {AI_color.name()}")
        self.User_color_b.setStyleSheet(f"background-color: {User_color.name()}")
        self.wText_color.setStyleSheet(f"background-color: {Text_color.name()}")

        self.apply = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")

        self.lay.addWidget(self.font_label,0,0)
        self.lay.addWidget(self.font,0,1)
        self.lay.addWidget(self.wfont_size,0,2)
        self.lay.addWidget(self.wText_color,0,3)

        self.lay.addWidget(self.AI_label,1,0)
        self.lay.addWidget(self.AI_color_b,1,1)
        self.lay.addWidget(self.User_label,2,0)
        self.lay.addWidget(self.User_color_b,2,1)

        self.lay.addWidget(self.apply,3,2)
        self.lay.addWidget(self.cancel,3,3)

        self.setLayout(self.lay)

        self.AI_color_b.clicked.connect(self.change_AI_color)
        self.User_color_b.clicked.connect(self.change_User_color)
        self.wText_color.clicked.connect(self.change_Text_color)
        self.apply.clicked.connect(self.fapply)
        self.cancel.clicked.connect(self.close)

    def change_AI_color(self):
        c = QColorDialog(self,currentColor=self.AI_color)
        self.AI_color = c.getColor()
        self.AI_color_b.setStyleSheet(f"background-color: {self.AI_color.name()}")

    def change_Text_color(self):
        c = QColorDialog(self,currentColor=self.Text_color)
        self.Text_color = c.getColor()
        self.wText_color.setStyleSheet(f"background-color: {self.Text_color.name()}")

    def change_User_color(self):
        c = QColorDialog(self,currentColor=self.User_color)
        self.User_color = c.getColor()
        self.User_color_b.setStyleSheet(f"background-color: {self.User_color.name()}")
    
    def fapply(self):
        self.apply_bool = True
        self.close()
    
    def exec(self):
        super().exec()
        if self.apply_bool:
            return self.Font_size, self.Font, self.AI_color, self.User_color, self.Text_color
        
        return self.wfont_size.value(), self.bFont, self.bAI_color, self.bUser_color, self.bText_color

        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.i = 0
        self.AI_color = QColor(255,0,0)
        self.User_color = QColor(0,0,255)
        self.Text_color = QColor(0,0,0)
        self.font = ""
        self.font_size = 12

        self.CreateMenu()
        self.create_widgets()

        self.setWindowTitle("Ai Chatting")

        self.tools_list = []

        for i in Tools:
            if i["Active"]:
                self.tools_list.append(i["Tool"])
        self.messagess = [SystemMessage("You are a AI assistant")]
        llm = ChatOllama(model="gemma4:e4b",temperature=0.8,verbose=True, reasoning=True).bind_tools(self.tools_list)

        first_step = RunnableLambda(lambda x : llm.invoke(x))
        tool_step = RunnableLambda(lambda x : Calculate_tools(x,self.messagess,self.tools_list))
        tool_invoke_step = RunnableLambda(lambda x : llm.invoke(x) if x != None else x[-1])
        append_step = RunnableLambda(lambda x: self.messagess.append(x))
        output_step = RunnableLambda(lambda x : self.messagess[-1].content)

        self.chain = first_step | tool_step | tool_invoke_step | append_step |output_step


    def create_widgets(self): 
        self.cenWidget = QWidget()
        self.lay = QVBoxLayout()
        self.setCentralWidget(self.cenWidget)

        self.cenWidget.setLayout(self.lay)

        self.setMinimumSize(500,500)
        self.conv = QWidget()
        self.scr = QScrollArea()
        self.scr.setWidget(self.conv)
        self.scr.setWidgetResizable(True)
        self.scr.setStyleSheet("border-radius: 10px; border: 1px solid Gainsboro")

        self.lay.addWidget(self.scr)

        self.messages = QGridLayout()
        self.conv.setLayout(self.messages)
        self.conv.setStyleSheet("background-color: white")
        shadow = QGraphicsDropShadowEffect(blurRadius=5,xOffset=10,yOffset=10)
        self.scr.setGraphicsEffect(shadow)

        self.prompt = {"messages": []}
        self.edit = QLineEdit()
        self.edit.returnPressed.connect(self.send)
        self.edit.setStyleSheet("QLineEdit{border-radius: 10px; padding: 5px} QLineEdit:active{border: 1px solid LightBlue}")

        self.lay.addWidget(self.edit)


    def CreateMenu(self):
        mb = self.menuBar()
        Save = QAction("Save", self)
        Load = QAction("Load", self)

        mb.addAction(Save)
        mb.addAction(Load)

        Tools = QAction("Tools", self)
        LLM = QAction("LLM Model", self)
        C_Setting = QAction("Preferences", self)
        Clear = QAction("Clear", self)

        menu = mb.addMenu("Settings")
        menu.addAction(Tools)
        menu.addAction(LLM)
        menu.addAction(C_Setting)
        menu.addAction(Clear)

        add_tool = QAction("Add Tool", self)

        menu = mb.addMenu("Advance Settings")
        menu.addAction(add_tool)

        C_Setting.triggered.connect(self.Color_settings)
        Clear.triggered.connect(self.Clear_chat)
    
    def Color_settings(self):

        m = Menu(24,self.font,self.AI_color,self.User_color,self.Text_color)
        self.font_size, self.font , self.AI_color, self.User_color, self.Text_color = m.exec()
        print(self.font_size)
        count = self.messages.rowCount()
        k = 0
        for i in range(count):
            if k == 0:
                widget = self.messages.itemAtPosition(i,0).widget()
                widget.setStyleSheet(f"background-color:{self.User_color.name()}; color: {self.Text_color.name()}; font-size: {self.font_size}; border-radius:10px; padding:20px")

            if k == 1:
                widget = self.messages.itemAtPosition(i,1).widget()
                widget.setStyleSheet(f"background-color:{self.AI_color.name()};color: {self.Text_color.name()}; font-size: {self.font_size}; border-radius:10px; padding:20px")

            k += 1
            k = k%2


    def Clear_chat(self):
        self.prompt["messages"] = []
        self.i = 0

    def send(self):
        text = self.edit.text()
        self.messages.addWidget(Message(text,self.User_color.name(),self.Text_color.name(),self.font_size, self.font),self.i,0)
        self.i+=1

        self.prompt["messages"].append({"role":"user", "content": text})

        try:
            self.messagess.append(HumanMessage(text))
            output = self.chain.invoke(self.messagess)

            self.prompt["messages"].append({"role":"system", "content": output})
            self.messages.addWidget(Message(output,self.AI_color.name(),self.Text_color.name(),self.font_size, self.font),self.i,1)
            self.i+=1
        except:
            self.messages.addWidget(Message("Error",self.AI_color.name(),self.Text_color.name(),self.font_size, self.font),self.i,1)
            self.i+=1
        
        self.edit.setText("")

app = QApplication()
m = MainWindow()
m.show()

app.exec()
