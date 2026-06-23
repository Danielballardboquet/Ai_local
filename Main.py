from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage,AIMessage
from langchain_community.tools.wikipedia.tool import *
from langchain_community.agent_toolkits.steam.toolkit import SteamToolkit 
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QAction, QColor, QMouseEvent, QClipboard,QGuiApplication, QFont
from markdown2 import markdown
from Tools.Tools import Tools
import json
import threading
import os


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

class Message(QLabel):
    def __init__(self,text, color, Text_color = "black", font_size = 12, font_name = ""):
        text = markdown(text)
        super().__init__(text=text)
        self.setStyleSheet(f"background-color:{color}; color: {Text_color}; font-size: {font_size}; border-radius:10px; padding:20px")
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        self.clip = QGuiApplication.clipboard()
        self.setTextInteractionFlags(Qt.TextSelectableByMouse |Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.setOpenExternalLinks(True)

    def mousePressEvent(self, ev: QMouseEvent ):
        if ev.button() == Qt.RightButton:
            self.clip.setText(self.text())

class LLM_Menu(QDialog):
    def __init__(self, model_name: str):
        super().__init__()
        self.setWindowTitle("LLM preferences")
        self.apply = False
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.models = ["deepseek-r1:latest",
                       "deepseek-r1:1.5b",
                       "deepseek-r1:7b",
                       "deepseek-r1:8b",
                       "deepseek-r1:14b",
                       "deepseek-r1:32b",
                       "qwen3.5:27b",
                       "gemma4:e4b"]
        
        self.combo = QComboBox()
        self.combo.addItems(self.models)
        self.combo.setCurrentText(model_name)

        self.temperature = QSpinBox()
        self.temperature.setMaximum(100)
        self.temperature.setMinimum(0)
        self.temperature.setValue(80)

        self.model_name = QLabel("Model Name")
        self.tmp_label = QLabel("Temperature")

        self.apply = QPushButton("Apply")
        self.Quit = QPushButton("Quit")

        self.grid.addWidget(self.model_name,0,0)
        self.grid.addWidget(self.combo,0,1)

        self.grid.addWidget(self.tmp_label,1,0)
        self.grid.addWidget(self.temperature,1,1)

        self.grid.addWidget(self.apply,2,0)
        self.grid.addWidget(self.Quit,2,1)

        self.apply.clicked.connect(self.app)
        self.Quit.clicked.connect(self.close)

    def app(self):
        self.apply = True
        self.close()

    def exec(self):
        super().exec()

        if self.apply:
            return self.models[self.combo.currentIndex()], self.temperature.value()
        else:
            return None, None

class Menu(QDialog):
    def __init__(self, Font_size:int, Font:str, AI_color : QColor, User_color : QColor, Text_color : QColor):
        super().__init__()
        self.setWindowTitle("Preferences")
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

        self.f = QFontComboBox()
        self.AI_color_b = QPushButton()
        self.User_color_b = QPushButton()
        self.wText_color = QPushButton()
        self.wfont_size = QSpinBox()
        self.wfont_size.setValue(self.Font_size)
        self.f.setCurrentFont(QFont(self.bFont))

        self.AI_color_b.setStyleSheet(f"background-color: {AI_color.name()}")
        self.User_color_b.setStyleSheet(f"background-color: {User_color.name()}")
        self.wText_color.setStyleSheet(f"background-color: {Text_color.name()}")

        self.apply = QPushButton("Apply")
        self.cancel = QPushButton("Cancel")

        self.lay.addWidget(self.font_label,0,0)
        self.lay.addWidget(self.f,0,1)
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
            return self.wfont_size.value(), self.f.currentFont().family(), self.AI_color, self.User_color, self.Text_color
        
        return self.wfont_size.value(), self.bFont, self.bAI_color, self.bUser_color, self.bText_color

class Tool_menu(QDialog):
    def __init__(self, tools):
        super().__init__()
        self.setWindowTitle("Tools")

        self.tools = tools

        self.apply = True

        self.lay = QGridLayout()
        self.setLayout(self.lay)

        for i,tool in enumerate(self.tools):

            Hlay = QHBoxLayout()
            label = QLabel(tool["Tool_name"])
            qcheck = QCheckBox()
            bool = tool["Active"]
            qcheck.setChecked(bool)

            self.lay.addWidget(label,i,0)
            self.lay.addWidget(qcheck,i,1)
        
        self.apply = QPushButton("Apply")
        self.Cancel = QPushButton("Cancel")

        self.lay.addWidget(self.Cancel,i+1,0)
        self.lay.addWidget(self.apply,i+1,1)
        
    def exec(self):
        super().exec()
        if self.apply:
            for i,tool in enumerate(self.tools):
                tool["Active"] = self.lay.itemAtPosition(i,1).widget().isChecked()
            
            return self.tools
        
        else:
            return self.tools
        
class MainWindow(QMainWindow):
    
    Mes_Sig = Signal(str)
    
    def __init__(self):
        super().__init__()

        self.i = 0
        self.settings = {}
        self.Tools = Tools

        self.Mes_Sig.connect(self.add_message)

        #Create Widgets

        self.load_setting()
        self.CreateMenu()
        self.create_widgets()

        self.setWindowTitle("Ai Chatting")

        self.qfont = QFont(self.font,self.font_size)

        #Tools and prompts

        self.tools_list = []

        for i in self.Tools:
            if i["Active"]:
                self.tools_list.append(i["Tool"])

        self.sys_prompt = "You are a AI assistant"
        try: 
            with open("Custom_prompt.txt","r") as f:
                self.sys_prompt += "Custom prompt:" + f.read()
        except:
            None

        self.messagess = [SystemMessage(self.sys_prompt)]

        #Create LLM and Chain

        self.llm = ChatOllama(model=self.model,temperature=0.8,verbose=True, reasoning=True, num_predict=1028).bind_tools(self.tools_list)

        first_step = RunnableLambda(lambda x : self.llm.invoke(x))
        tool_step = RunnableLambda(lambda x : Calculate_tools(x,self.messagess,self.tools_list))
        tool_invoke_step = RunnableLambda(lambda x : self.llm.invoke(x) if x != None else x[-1])
        append_step = RunnableLambda(lambda x: self.messagess.append(x))
        output_step = RunnableLambda(lambda x : self.messagess[-1].content)

        self.chain = first_step | tool_step | tool_invoke_step | append_step |output_step

    def load_setting(self):

        try:
            with open("settings.json","r") as f:
                settings = json.loads(f.read())
            
                self.AI_color = QColor(settings["AI_color"])
                self.User_color = QColor(settings["User_Color"])
                self.Text_color = QColor(settings["text_color"])
                self.font = settings["font"]
                self.font_size = settings["font_size"]
                self.model = settings["model"]
        except:
            settings = {}
            self.model = "gemma4:e4b"
            self.AI_color = QColor(255,0,0)
            self.User_color = QColor(0,0,255)
            self.Text_color = QColor(0,0,0)
            self.font = "Segoe UI"
            self.font_size = 12

    def closeEvent(self, event):
        self.settings["User_Color"] = self.User_color.name()
        self.settings["text_color"] = self.Text_color.name()
        self.settings["font"] = self.font
        self.settings["font_size"] = self.font_size
        self.settings["AI_color"] = self.AI_color.name()
        self.settings["model"] = self.model

        with open("settings.json", "w") as f:
            print(f.write(json.dumps(self.settings)))

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

        Load.triggered.connect(self.Load)
        Save.triggered.connect(self.Save)
        Tools.triggered.connect(self.tool_menu)
        LLM.triggered.connect(self.LLM_settings)
        C_Setting.triggered.connect(self.Color_settings)
        Clear.triggered.connect(self.Clear_chat)
    
    def contextMenuEvent(self, event):
        None
         
    def Color_settings(self):

        m = Menu(self.font_size,self.font,self.AI_color,self.User_color,self.Text_color)
        self.font_size, self.fnt , self.AI_color, self.User_color, self.Text_color = m.exec()
        count = self.messages.rowCount()
        k = 0
        self.font = self.fnt
        self.qfont = QFont(self.font,self.font_size)
        print("Hello:",self.font_size)
        for i in range(count):
            if k == 0:
                widget = self.messages.itemAtPosition(i,0).widget()
                widget.setStyleSheet(f"background-color:{self.User_color.name()}; color: {self.Text_color.name()}; font-size: {self.font_size}; border-radius:10px; padding:20px")
                widget.setFont(self.qfont)

            if k == 1:
                widget = self.messages.itemAtPosition(i,1).widget()
                widget.setStyleSheet(f"background-color:{self.AI_color.name()};color: {self.Text_color.name()}; font-size: {self.font_size}; border-radius:10px; padding:20px")
                widget.setFont(self.qfont)

            k += 1
            k = k%2

    def Clear_chat(self):
        self.prompt["messages"] = []
        self.i = 0

    def LLM_settings(self):
        menu = LLM_Menu(self.model)
        LLM_model, temperature = menu.exec()

        if LLM_model != None and temperature != None:
            try:
                self.llm = ChatOllama(model=LLM_model,temperature=temperature/100,verbose=True, reasoning=True, validate_model_on_init=True,num_predict=1028).bind_tools(self.tools_list)

                first_step = RunnableLambda(lambda x : self.llm.invoke(x))
                tool_step = RunnableLambda(lambda x : Calculate_tools(x,self.messagess,self.tools_list))
                tool_invoke_step = RunnableLambda(lambda x : self.llm.invoke(x) if x != None else x[-1])
                append_step = RunnableLambda(lambda x: self.messagess.append(x))
                output_step = RunnableLambda(lambda x : self.messagess[-1].content)

                self.chain = first_step | tool_step | tool_invoke_step | append_step |output_step

            except:
                dial = QMessageBox()
                dial.setWindowTitle("Continue")
                dial.setText("You need to download the model")
                dial.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
                dial.setIcon(QMessageBox.Warning)
                exe = dial.exec()
                
                if exe == QMessageBox.Ok:
                    os.system(f"ollama pull {LLM_model}")
                    self.llm = ChatOllama(model=LLM_model,temperature=temperature/100,verbose=True, reasoning=True, validate_model_on_init=True,num_predict=1028).bind_tools(self.tools_list)

                    first_step = RunnableLambda(lambda x : self.llm.invoke(x))
                    tool_step = RunnableLambda(lambda x : Calculate_tools(x,self.messagess,self.tools_list))
                    tool_invoke_step = RunnableLambda(lambda x : self.llm.invoke(x) if x != None else x[-1])
                    append_step = RunnableLambda(lambda x: self.messagess.append(x))
                    output_step = RunnableLambda(lambda x : self.messagess[-1].content)

                    self.chain = first_step | tool_step | tool_invoke_step | append_step |output_step

    def send(self):
        self.edit.setDisabled(True)
        text = self.edit.text()
        mes = Message(text,self.User_color.name(),self.Text_color.name(),self.font_size, self.font)
        mes.setFont(self.qfont)
        self.messages.addWidget(mes,self.i,0)
        self.i+=1

        self.s = self.scr.verticalScrollBar()
        max = self.s.maximum()
        self.s.setValue(max)

        self.prompt["messages"].append({"role":"user", "content": text})
        self.edit.setText("")

        self.thrd = threading.Thread(target=self.generate, args=(text,))
        self.thrd.start()

    def generate(self,text):
        while True:
            self.messagess.append(HumanMessage(text))
            output = self.chain.invoke(self.messagess)

            self.prompt["messages"].append({"role":"system", "content": output})
            if output != "":
                break
        try:
            None
        except:
            output = "Error"

        self.edit.setDisabled(False)
        self.Mes_Sig.emit(output)

    def tool_menu(self):
        t = Tool_menu(Tools)
        self.Tools = t.exec()

        self.tools_list = []

        for i in self.Tools:
            if i["Active"]:
                self.tools_list.append(i["Tool"])
    
        self.llm = ChatOllama(model=self.model,temperature=0.8,verbose=True, reasoning=True, num_predict=1028).bind_tools(self.tools_list)

        first_step = RunnableLambda(lambda x : self.llm.invoke(x))
        tool_step = RunnableLambda(lambda x : Calculate_tools(x,self.messagess,self.tools_list))
        tool_invoke_step = RunnableLambda(lambda x : self.llm.invoke(x) if x != None else x[-1])
        append_step = RunnableLambda(lambda x: self.messagess.append(x))
        output_step = RunnableLambda(lambda x : self.messagess[-1].content)

        self.chain = first_step | tool_step | tool_invoke_step | append_step |output_step

    def Save(self):
        URL = QFileDialog.getSaveFileName()[0]
        if URL != "":
            mess = []
            for m in self.messagess:
                mess.append({"Type": str(type(m)),"content":m.content})
            
            with open(URL, "+w") as f:
                f.write(json.dumps(mess))
    
    def Load(self):
        URL = QFileDialog.getOpenFileName()[0]
        if URL != "":
            with open(URL, "r") as f:
                mess = json.loads(f.read())
        
        self.messagess = []
        self.i = 0
        for m in mess:
            if m["Type"] == "<class 'langchain_core.messages.human.HumanMessage'>":
                File =HumanMessage(m["content"])
                self.messages.addWidget(Message(m["content"],self.User_color.name(),self.Text_color.name(),self.font_size, self.font),self.i,0)
                self.i += 1
            elif m["Type"] == "<class 'langchain_core.messages.ai.AIMessage'>":
                File = AIMessage(m["content"])
                self.messages.addWidget(Message(m["content"],self.AI_color.name(),self.Text_color.name(),self.font_size, self.font),self.i,1)
                self.i += 1
            else:
                File = SystemMessage(m["content"])
            
            self.messagess.append(File)
    
    @Slot(str)
    def add_message(self,output : str):
        mes = Message(output,self.AI_color.name(),self.Text_color.name(),self.font_size, self.font)
        mes.setFont(self.qfont)
        self.messages.addWidget(mes,self.i,1)
        self.i+=1

        self.s = self.scr.verticalScrollBar()
        max = self.s.maximum()
        self.s.setValue(max)

app = QApplication()
m = MainWindow()
m.show()

app.exec()
