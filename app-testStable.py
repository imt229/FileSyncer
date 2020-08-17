import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json

import shutil


#home_directory = os.path.expanduser('~')

# The `Qt` namespace has a lot of attributes to customise
# widgets. See: http://doc.qt.io/qt-5/qt.html
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.setWindowTitle("Olivet")

        #Create main widget and main layout
        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        #Finding height and width of window
        availableGeo = QDesktopWidget().availableGeometry()
        self.width = int(availableGeo.width()/2)
        self.height = int(availableGeo.height()/2)
        #Left, top, width, height
        self.setGeometry(0,0,self.width,self.height)


        label = QFileDialog(self)
        
        #Adding Toolbar
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)


        #Add button
        button_action = QAction("Your button", self)
        #Set Status Tip shows details at bottom of window
        button_action.setStatusTip("This is your button")
        #Connect Function for when button is triggered
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        #Add button to toolbar
        toolbar.addAction(button_action)

        #Add status bar at bottom of window
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        #Setting up Layout For View Systems
        self.firstGrid = QGridLayout()
        #self.firstGrid.addLayout(self.treeLayout, 0, 0, 1, 3) #row, column, rowspan, columnspan
        layout.addLayout(self.firstGrid)


        self.setupTreeArea()

        self.setUpPathArea()
        


        #self.tree.setGeometry(1000,1000,1000,1000)
        #layout.addWidget(self.tree)
        #layout.addWidget(self.list)
        #layout.addWidget(label)


        self.labelFileName = QLabel(self)
        self.labelFileName.setText("File Name:")

        self.lineEditFileName = QLineEdit(self)

        self.labelFilePath = QLabel(self)
        self.labelFilePath.setText("File Path:")

        self.lineEditFilePath = QLineEdit(self)

        self.gridLayout = QGridLayout()
        
        self.gridLayout.addWidget(self.labelFileName, 0, 0)
        self.gridLayout.addWidget(self.lineEditFileName, 0, 1)
        self.gridLayout.addWidget(self.labelFilePath, 1, 0)
        self.gridLayout.addWidget(self.lineEditFilePath, 1, 1)
        layout.addLayout(self.gridLayout)
        
    def setUpPathArea(self):
        #Creating List System
        self.list = QListView()
        self.list.setSelectionMode(3) #0 = NoSelection, 1 = SingleSelection, 2 = MultiSelection, 3 = ExtendedSelection, 4 = Contigious Selection
        self.list.setSelectionRectVisible(True)
        self.list.setWordWrap(True)
        self.listModel = QStandardItemModel()
        self.loadPath()
        self.list.setModel(self.listModel)
        self.list.clicked.connect(self.onListClicked)


        #Layout for list Area
        pathLayout = QVBoxLayout()
        pathLayout.addWidget(self.list)

        #Create Path Buttons and Layout
        self.addPathBt = QPushButton("Add Path")
        self.checkPathBt = QPushButton("Check Paths")
        #self.addPathBt.setFixedHeight(74)
        self.deletePathBt = QPushButton("Delete Path")
        self.deleteAllBt = QPushButton("Delete All")
        pathButtonLayout = QGridLayout()
        pathButtonLayout.addWidget(self.addPathBt, 0, 0)
        pathButtonLayout.addWidget(self.checkPathBt, 1, 0)
        pathButtonLayout.addWidget(self.deletePathBt, 0, 1)
        pathButtonLayout.addWidget(self.deleteAllBt, 1, 1)
        pathLayout.addLayout(pathButtonLayout)
        
        #Hooking functions up to buttons
        self.addPathBt.pressed.connect(self.addPath)
        self.deletePathBt.pressed.connect(self.deletePath)
        self.deleteAllBt.pressed.connect(self.deleteAll)
        self.firstGrid.addLayout(pathLayout, 0, 3, 1, 2)

    #Function that adds path to file and model view
    def addPath(self):
        print("Add Path")
        try:
            if (not self.currentFilePath):
                self.statusBar.showMessage("No File Selected", 3000)
                return
            if(os.path.isdir(self.currentFilePath)):
                pathToAdd = self.currentFilePath
            else:
                pathToAdd = os.path.dirname(self.currentFilePath)
            if not pathToAdd in self.pathList:
                self.pathList.append(pathToAdd)
                self.storePath()
                self.listModel.appendRow(QStandardItem(QIcon('tick.png'), pathToAdd))
                self.statusBar.showMessage("Path Added: " + pathToAdd, 3000)
                
            else:
                #Duplicates
                self.statusBar.showMessage("Path Already Listed: " + pathToAdd, 3000)
        except Exception:
            self.statusBar.showMessage("Unable to Add", 3000)

    #Function that deletes path from file and model view
    def deletePath(self):
        print("Delete Path")
        #For multiple Selection
        #Use QListView.clicked() to get index of whatever is clicked
        selection = self.list.selectionModel().selectedIndexes()
        if not selection:
            self.statusBar.showMessage("Nothing Selected to Delete", 3000)
        else:
            while selection:
                i = selection[0]
                if (i.data() in self.pathList):
                    self.pathList.remove(i.data())
                #Using i.row() gets row of index 
                self.listModel.removeRows(i.row(),1)
                selection = self.list.selectionModel().selectedIndexes()
            self.storePath()
            self.statusBar.showMessage("Path(s) Deleted", 3000)
    
    #Function that deletes all paths
    def deleteAll(self):
        self.pathList = []
        self.listModel.removeRows( 0, self.listModel.rowCount())
        self.storePath()
        self.statusBar.showMessage("All Paths Deleted", 3000)

    #Load paths from data store
    def loadPath(self):
        try:
            with open('pathData.txt') as openFile:
                self.pathList = json.load(openFile)
            for item in self.pathList:
                if(os.path.isdir(item)):
                    self.listModel.appendRow(QStandardItem(QIcon('tick.png'),item))
                else:
                    self.listModel.appendRow(QStandardItem(QIcon('cross.png'),item))
        except Exception:
            self.pathList = []
            pass

    #Function that writes to txt file that stores list of paths
    def storePath(self):
        with open('pathData.txt', 'w') as outfile:
            json.dump(self.pathList, outfile)

    def onListClicked(self, index):
        indexItem = self.listModel.index(index.row(), 0, index.parent())
        print(indexItem.data())
    

    def setupTreeArea(self):
        #Creating Tree System
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setColumnWidth(0, int(self.width/3))
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.clicked.connect(self.on_treeView_clicked)
        
        #Setup Tree Path Variables
        self.currentFileName = ""
        self.currentFilePath = ""


        #Layout for tree area
        treeLayout = QVBoxLayout()
        treeLayout.addWidget(self.tree)

        #Set up Tree buttons
        self.copyBt = QPushButton("Copy")
        self.overwriteCheck = QCheckBox("Overwrite")
        self.overwriteCheck.setChecked(True)
        self.copyBt.pressed.connect(self.copy)

        treeButtonLayout = QGridLayout()
        treeButtonLayout.addWidget(self.overwriteCheck, 0, 0)
        treeButtonLayout.addWidget(self.copyBt, 0, 1, 1, 5)

        treeLayout.addLayout(treeButtonLayout)
        self.firstGrid.addLayout(treeLayout, 0, 0, 1, 3) #row, column, rowspan, columnspan

        #Set up Checkbox


    #The signal passed indicates whether the button is *checked*,
    #  and since our button is not checkable — just clickable — it is always false.
    #Have to set the setCheckable property on the QAction to true
    def onMyToolBarButtonClick(self, s):
        print("click", s)

    def on_treeView_clicked(self, index):
        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        self.currentFileName = fileName
        filePath = self.model.filePath(indexItem)
        self.currentFilePath = filePath

        self.lineEditFileName.setText(fileName)
        self.lineEditFilePath.setText(filePath)

    def copy(self):
        pathSelection = self.list.selectionModel().selectedIndexes()
        if not pathSelection:
            self.statusBar.showMessage("No Paths Selected", 3000)
            return
        if not self.currentFileName:
            self.statusBar.showMessage("No File Selected", 3000)
            return
        for i in pathSelection:
            #QIcon("cross.png")
            #self.listModel.setData(i, "free")
            #i.setIcon(QIcon(self.cross))
            if (self.overwriteCheck.isChecked()):
                try:
                    shutil.copy(self.currentFilePath, i.data())
                except IOError:
                    print("Unable to copy file.")
                except:
                    print("Unexpected error:", sys.exc_info())
            else:
                # Open the file and raise an exception if it exists
                folder = i.data()
                newFilePath = os.path.join(folder,self.currentFileName)
                index = 0
                isDir = os.path.isdir(self.currentFilePath)
                breakVar = True
                try:

                    # Copy the file and automatically close files at the end
                    f = os.open(newFilePath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    shutil.copy2(self.currentFilePath, newFilePath)
                    os.close(f)


                except:
                    if (isDir):
                        print()
                    else:
                        while(os.path.exists(newFilePath)):
                            extension = self.currentFileName[self.currentFileName.rfind("."):len(self.currentFileName)]
                            newFilePath = self.currentFileName[0:self.currentFileName.rfind(".")]
                            index += 1
                            newFilePath += " (" + str(index) + ")"
                            newFilePath = os.path.join(folder, newFilePath + extension)
                        try:

                            # Copy the file and automatically close files at the end
                            f = os.open(newFilePath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                            shutil.copy2(self.currentFilePath, newFilePath)
                            os.close(f)
                        except:
                            print("Failed")



app = QApplication(sys.argv)

window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop and exit after function call ends
sys.exit(app.exec_())

# Your application won't reach here until you exit and the event 
# loop has stopped.