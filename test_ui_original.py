from PyQt5.QtCore import QObject,Qt,pyqtSignal,pyqtSlot,QTimer,QSize,QTime,QMargins
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QFormLayout,QFrame,QPushButton,QGridLayout
from PyQt5.QtWidgets import QSizePolicy,QComboBox,QLabel,QSpinBox,qApp,QTextEdit,QDoubleSpinBox
from PyQt5.QtGui import QTextCursor,QPixmap
from PyQt5.QtSerialPort import QSerialPortInfo
import sys

# 窗口类 MainWidget
# 本身不包含任何逻辑，只包含界面构成组件，方便选手构建出统一的UI样式
# 对外提供的组件包含如下：
# QLabel组件：labelPicOne、labelPicTwo、labelPicThree、labelPicFour、labelImg 用于显示图像
# QLabel组件：labelCurTime 用于显示当前时间；labelInfo 显示检测结果说明
# QPushButton组件：btnCapture、btnStart、btnStop、btnExit 对应的控制按钮
# QComboBox组件： cmbModbus、cmbRobot 用于显示当前选择的串口
# QTextEdit组件：editLog用于显示日志辅助信息        

class MyWidget(QWidget):
    def __init__(self):
        super().__init__(None)
        self.__setUI()

    def __createImgLabel(self,info,isExpanding=True):
        label=QLabel(info)
        label.setAlignment(Qt.AlignCenter)
        label.setFrameShape(QFrame.Box)
        label.setScaledContents(False)
        if isExpanding ==True:
            label.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        return label
    def updateTime(self):
        self.labelCurTime.setText(QTime.currentTime().toString("hh:mm:ss"))
    def __setUI(self):
        #左侧纵向布局
        leftLayout = QVBoxLayout()
        leftLayout.setSpacing(1)
        titleText="广东省2021年度工业互联网边缘计算大赛"
        self.setWindowTitle(titleText)
        title=QLabel(titleText)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font: 26pt "Ubuntu";color:rgb(0,0,255);') 
        leftLayout.addWidget(title)
        #图像展示表格布局
        tmp=QGridLayout()
        tmp.setVerticalSpacing(1)
        tmp.setHorizontalSpacing(1)
        tmp.setAlignment(Qt.AlignRight)
        self.labelPicOne=self.__createImgLabel("图像1")
        self.labelPicTwo=self.__createImgLabel("图像2")
        self.labelPicThree=self.__createImgLabel("图像3")
        self.labelPicFour=self.__createImgLabel("图像4")
        tmp.addWidget(self.labelPicOne,0,0)
        tmp.addWidget(self.labelPicTwo,0,1)
        tmp.addWidget(self.labelPicThree,1,0)
        tmp.addWidget(self.labelPicFour,1,1)
        leftLayout.addLayout(tmp)
        #控制组件横向布局
        self.btnCapture = QPushButton("手动拍照")
        self.btnStart = QPushButton("开始")
        self.btnStop = QPushButton("停止")
        self.btnExit = QPushButton("退出程序")
        self.cmbModbus = QComboBox()
        self.cmbRobot = QComboBox()
        all_ports = QSerialPortInfo.availablePorts()
        for item in all_ports:
            self.cmbModbus.addItem(item.systemLocation())
            self.cmbRobot.addItem(item.systemLocation())
        tmp = QHBoxLayout()
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
        #右侧纵向布局
        rightLayout=QVBoxLayout()
        rightLayout.setSpacing(3)
        self.labelCurTime=QLabel(QTime.currentTime().toString("hh:mm:ss"))
        self.labelCurTime.setAlignment(Qt.AlignCenter)
        self.labelCurTime.setStyleSheet('font: 26pt "Ubuntu";color:rgb(255,100,100);') 
        self.labelInfo=QLabel("当前检测结果")
        self.labelImg=self.__createImgLabel("统计图像",False)
        self.labelImg.setFixedSize(200,200)
        self.editLog=QTextEdit()
        self.editLog.setMaximumWidth(200)
        self.editLog.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Expanding)
        rightLayout.addSpacing(10)
        rightLayout.addWidget(self.labelCurTime)
        rightLayout.addSpacing(30)
        rightLayout.addWidget(self.labelInfo)
        rightLayout.addWidget(self.labelImg)
        rightLayout.addSpacing(10)
        rightLayout.addWidget(self.editLog)
        logo=QLabel("国顺教育")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet('font: 26pt "Ubuntu";color:rgb(100,100,200);') 
        rightLayout.addWidget(logo)
        #整体布局
        tmp= QHBoxLayout()
        tmp.setSpacing(2)
        tmp.addLayout(leftLayout)
        tmp.addLayout(rightLayout)
        tmp.setContentsMargins(QMargins(5,2,5,2))
        self.setLayout(tmp)
        #更新时间
        t=QTimer(self)
        t.timeout.connect(self.updateTime)
        t.start(1000)


def __testUI():
    app = QApplication(sys.argv)
    w = MyWidget()
    w.resize(1024, 768)
    w.show()
    sys.exit(app.exec_())


__testUI()