from PyQt5 import QtWidgets  # 窗口和代码详细注释
import sys

from PyQt5.QtCore import QTime, Qt, QMargins, QTimer
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy, QFrame, QVBoxLayout, QGridLayout, QPushButton, QComboBox, \
    QHBoxLayout, QTextEdit, QApplication




class MyWidget(QWidget):
    # 自己创建一个MyWindow类，以class开头，MyWindows是自己的类名
    # (QtWidgets.QWidget)是继承QtWidgets.QWidget类方法
    # 定义类或函数不要忘记“:”, 判断语句也必须以”:”结尾
    def __init__(self):
        # def是定义函数(类方法)，同样第二个__init__是函数名
        # (self)是pyqt类方法必须要有的，代表自己。相当于java，c++中的this
        # 其实__init__是析构函数，也就是类被创建后就会预先加载的项目
        super().__init__()  # 这里我们要重载一下MyWindows同时也包含了QtWidgets.QWidget的预加载项
        self.__setUI()  # 调用下面的__setUI()函数，前面已经讲过，该函数在类创建的时候就会被调用

    def __createImgLabel(self, info, isExpanding=True):  # 自定义函数，函数具体内容是设置标签的对齐方式
        label = QLabel(info)  # 生成一个QLabel实例对象，QLabel提供一个文本和图像显示的标签类
        label.setAlignment(Qt.AlignCenter)  # 居中对齐
        label.setFrameShape(QFrame.Box)  # 设置边框外形
        label.setScaledContents(False)  # 图片自适应边框大小
        if isExpanding == True:
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return label

    def updateTime(self):  # 自定义函数，内容是添加文本显示当前时间
        self.labelCurTime.setText(QTime.currentTime().toString("hh:mm:ss"))

    def __setUI(self):
        leftLayout = QVBoxLayout()  # 创建一个类的实例，QVBoxLayout是QT中垂直布局的类
        leftLayout.setSpacing(1)
        titleText = "广东省2021年度工业互联网边缘计算大赛"
        self.setWindowTitle(titleText)  # 调用函数显示标题内容
        title = QLabel(titleText)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font:26pt "Ubuntu";color:rgb(218,112,214);')
        leftLayout.addWidget(title)

        tmp = QGridLayout()  # 创建一个类的实例， QGridLayout格栅布局,也称网格布局（多行多列）
        tmp.setVerticalSpacing(1)  # 调用类的方法，设置垂直间距
        tmp.setHorizontalSpacing(1)  # 调用类的方法，设置水平间距
        tmp.setAlignment(Qt.AlignRight)
        label1 = QLabel("P1")  # 创建一个QLabel标签类的实例（对象），标签内容是p1
        label2 = QLabel("P2")
        label3 = QLabel("P3")
        label4 = QLabel("P4")
        label1.setAlignment(Qt.AlignCenter)
        label2.setAlignment(Qt.AlignCenter)
        label3.setAlignment(Qt.AlignCenter)
        label4.setAlignment(Qt.AlignCenter)
        self.labelPicTwo = self.__createImgLabel("图像2")  # 创建一个实例接受函数的返回对象，此时该实例已经具备函数中调用类的方法
        self.labelPicThree = self.__createImgLabel("图像3")
        self.labelPicOne = self.__createImgLabel("图像1")
        self.labelPicFour = self.__createImgLabel("图像4")
        tmp.addWidget(self.labelPicOne, 0, 0)
        # 调用QGridLayout类的一个方法addWidget添加组件， self.labelPicOne前面创建的一个QLabel的一个实例，0，0栅栏布局的位置
        tmp.addWidget(self.labelPicTwo, 0, 1)
        tmp.addWidget(label1, 1, 0)
        tmp.addWidget(label2, 1, 1)
        tmp.addWidget(self.labelPicThree, 2, 0)
        tmp.addWidget(self.labelPicFour, 2, 1)
        tmp.addWidget(label3, 3, 0)
        tmp.addWidget(label4, 3, 1)
        leftLayout.addLayout(tmp)  # 将tmp布局实例添加到leftLayout布局当中

        self.btnCapture = QPushButton("手动拍照")  # 创建一个类的实例，QPushButton按钮类
        self.btnStart = QPushButton("开始")
        self.btnStop = QPushButton("停止")
        self.btnExit = QPushButton("退出程序")
        self.cmbModbus = QComboBox()  # 创建一个类的实例,QComboBox下拉列表框组件类
        self.cmbRobot = QComboBox()
        all_ports = QSerialPortInfo.availablePorts()
        # 调用QSerialPortInfo串口类的一个方法availablePorts显示当前设备注册表中所有串口信息，返回值是一个列表
        #
        tmp = QHBoxLayout()  # 创建一个类的实例，QHBoxLayout水平布局的类
        tmp.setSpacing(10)
        tmp.addWidget(QLabel("ModBus端口:"))
        tmp.addWidget(self.cmbModbus)
        tmp.addWidget(QLabel("机器人端口:"))
        tmp.addWidget(self.cmbRobot)
        tmp.addWidget(self.btnStart)
        tmp.addWidget(self.btnStop)
        tmp.addWidget(self.btnCapture)
        tmp.addWidget(self.btnExit)
        tmp.addStretch()
        leftLayout.addLayout(tmp)

        rightLayout = QVBoxLayout()
        rightLayout.setSpacing(3)
        self.labelCurTime = QLabel(QTime.currentTime().toString("hh:mm:ss"))
        # 创建一个类的实例，QTime.currentTime()调用类的方法，显示当前时间
        self.labelCurTime.setAlignment(Qt.AlignCenter)
        self.labelCurTime.setStyleSheet('font: 26pt "Ubuntu";color:rgb(255,100,100);')
        self.labelInfo = QLabel("当前电路板检测结果")
        self.labelImg = self.__createImgLabel("统计图像", False)
        self.labelImg.setFixedSize(200, 200)
        self.editLog = QTextEdit()
        # 创建一个类的实例, QTextEdit类是一个多行文本框控件，可以显示多行文本内容，当文本内容超出控件显示范围时，可以显示水平个垂直滚动条
        self.editLog.setMaximumWidth(200)
        self.editLog.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        rightLayout.addSpacing(10)  # 调用类的方法，添加空格的大小
        rightLayout.addWidget(self.labelCurTime)
        rightLayout.addSpacing(30)
        rightLayout.addWidget(QLabel("当前电路板检测信息:"))
        rightLayout.addWidget(self.labelInfo)  # 调用类的方法，添加组件
        rightLayout.addWidget(self.labelImg)
        rightLayout.addSpacing(10)
        rightLayout.addWidget(self.editLog)
        logo = QLabel("中山职院")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet('font: 26pt "Ubuntu";color:rgb(100,100,200);')

        rightLayout.addWidget(logo)

        tmp = QHBoxLayout()
        tmp.setSpacing(2)
        tmp.addLayout(leftLayout)
        tmp.addLayout(rightLayout)
        tmp.setContentsMargins(QMargins(5, 2, 5, 2))
        # setContentsMargins设置左侧、顶部、右侧和底部边距，以便在布局周围使用
        # QMargins定义了矩形的四个外边距量，left,top,right和bottom，描述围绕矩形的边框宽度
        self.setLayout(tmp)
        # 将布局中的小部件重新父级化，以将窗口作为父级
        t = QTimer(self)  # 创建一个时间类的实例
        t.timeout.connect(self.updateTime)  # 调用时间类的方法，更新时间
        t.start(1000)


def mainWindow():
    app = QtWidgets.QApplication(sys.argv)
    # sys系统模块,封装了一些系统的信息和接口
    # sys.argv 从程序外部获取参数的桥梁
    # pyqt窗口必须在QApplication方法中使用
    w = MyWidget()
    w.resize(1024, 768)
    # MyWindows()是我们上面自定义的类
    w.show()  # 有了实例，就得让他们显示，这里的show()是QWidget的方法，用来显示窗口的
    sys.exit(app.exec_())  # 启动时间循环


#mainWindow()
