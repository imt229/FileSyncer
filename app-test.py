import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
from genericFunctions import *
from CopyWindow import *

import shutil


#home_directory = os.path.expanduser('~')

# The `Qt` namespace has a lot of attributes to customise
# widgets. See: http://doc.qt.io/qt-5/qt.html
class MainWindow(QMainWindow):

    #MemberVariables:
    #self.width - width of window

    #For File List Area
    #self.fileList - Python List of files, read and written to from file
    #self.fileListView - qListView for file list
    #self.fileListModel - qStandardItemModel for file list


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
        height = int(availableGeo.height()/2)
        self.setGeometry(0,0, self.width, height) #Left, top, width, height


        label = QFileDialog(self)
        
        #Adding Toolbar
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)


        #Add button
        button_action = QAction("Log", self)
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

        self.setupPathArea()
        


        #self.tree.setGeometry(1000,1000,1000,1000)
        #layout.addWidget(self.tree)
        #layout.addWidget(self.list)
        #layout.addWidget(label)


    ####################
    ## Path Functions ##
    ####################
        
    def setupPathArea(self):
        #Creating List System
        self.listView = QListView()
        self.listModel = QStandardItemModel()
        #https://doc.qt.io/qt-5/qabstractitemview.html#SelectionMode-enum
        viewSettings(self.listView)

        
        self.loadPath()
        self.listView.setModel(self.listModel)
        self.listView.clicked.connect(self.onListClicked)
        #pathLabel = QLabel("Saved Paths")


        #Layout for list Area
        pathLayout = QVBoxLayout()
        #pathLayout.addWidget(pathLabel)
        pathLayout.addWidget(self.listView)


        self.setupPathButtons(pathLayout)

        self.setupFileListArea(pathLayout)
        self.firstGrid.addLayout(pathLayout, 0, 3, 1, 2)

    def setupPathButtons(self, layout):
        #Create Path Buttons and Layout
        addPathBt = QPushButton("Add Path")
        checkPathBt = QPushButton("Check Paths")
        #self.addPathBt.setFixedHeight(74)
        deletePathBt = QPushButton("Delete Path")
        deleteAllBt = QPushButton("Delete All")
        pathButtonLayout = QHBoxLayout()
        pathButtonLayout.addWidget(addPathBt)
        pathButtonLayout.addWidget(checkPathBt)
        pathButtonLayout.addWidget(deletePathBt)
        pathButtonLayout.addWidget(deleteAllBt)
        layout.addLayout(pathButtonLayout)
        
        #Hooking functions up to buttons
        addPathBt.pressed.connect(self.addPath)
        checkPathBt.pressed.connect(self.checkPaths)
        deletePathBt.pressed.connect(self.deletePath)
        deleteAllBt.pressed.connect(self.deleteAll)



    #Function that adds path to file and model view
    def addPath(self):
        try:
            if (not self.currentFilePath):
                self.statusBar.showMessage("No File Selected", 3000)
                return
            ##Checking if selected on tree is a folder or file
            ##If folder, add. If file, find folder that file is under and add that
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
    
    def checkPaths(self):
        #selection = self.listView.selectionModel().selectedIndexes()

        ###Iterates through all paths and checks validity
        for i in range(self.listModel.rowCount()):
            index = self.listModel.index(i, 0)
            path = index.data()
            if os.path.isdir(path):
                self.listModel.itemFromIndex(index).setIcon(QIcon("tick.png"))
            else:
                self.listModel.itemFromIndex(index).setIcon(QIcon("cross.png"))
            #Alternative way is to use self.listModel.setData(index, QStandardItem(icon, data))


    #Function that deletes path from file and model view
    def deletePath(self):
        print("Delete Path")
        #For multiple Selection
        #Use QListView.clicked() to get index of whatever is clicked
        selection = self.listView.selectionModel().selectedIndexes()
        if not selection:
            self.statusBar.showMessage("Nothing Selected to Delete", 3000)
        else:
            while selection:
                i = selection[0]
                if (i.data() in self.pathList):
                    self.pathList.remove(i.data())
                #Using i.row() gets row of index 
                self.listModel.removeRows(i.row(),1)
                selection = self.listView.selectionModel().selectedIndexes()
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
        self.pathList = loadFile("pathData.txt")
        for item in self.pathList:
            if(os.path.isdir(item)):
                self.listModel.appendRow(QStandardItem(QIcon('tick.png'),item))
            else:
                self.listModel.appendRow(QStandardItem(QIcon('cross.png'),item))

    #Function that writes to txt file that stores list of paths
    def storePath(self):
        with open('pathData.txt', 'w') as outfile:
            json.dump(self.pathList, outfile)

    def onListClicked(self, index):
        indexItem = self.listModel.index(index.row(), 0, index.parent())
        print(indexItem.data())
    
    #########################
    ## File List Functions ##
    #########################

    def setupFileListArea(self, layout):
        #Creating List System
        self.fileListView = QListView()
        viewSettings(self.fileListView)
        self.fileListModel = QStandardItemModel()
        self.loadFilePath()
        self.fileListView.setModel(self.fileListModel)
        #self.fileListView.clicked.connect(self.onListClicked)

        layout.addWidget(self.fileListView)
        self.createFileButtons(layout)

    def createFileButtons(self, layout):
        #Create File Buttons
        addFileBt = QPushButton("Add File")
        checkFileBt = QPushButton("Check Files")
        deleteFileBt = QPushButton("Delete File")
        copyFileBt = QPushButton("Copy")

        # Horizontal Layout
        pathButtonLayout = QHBoxLayout()
        pathButtonLayout.addWidget(addFileBt)
        pathButtonLayout.addWidget(checkFileBt)
        pathButtonLayout.addWidget(deleteFileBt)
        pathButtonLayout.addWidget(copyFileBt)
        layout.addLayout(pathButtonLayout)

        #########TO DO#########
        # Connect Button Functions
        addFileBt.pressed.connect(self.addFile)
        checkFileBt.pressed.connect(self.checkFiles)
        deleteFileBt.pressed.connect(self.deleteFile)
        copyFileBt.pressed.connect(self.copyFile)

    def addFile(self):
        fileSelection = getTreeSelection(self.tree, self.model)
        if (not fileSelection):
            self.statusBar.showMessage("No File Selected", 3000)
        else:
            for path in fileSelection:
                try:
                    if not path in self.fileList:
                        self.fileList.append(path)
                        self.fileListModel.appendRow(QStandardItem(QIcon('tick.png'), path))
                        self.statusBar.showMessage("File Added: " + path, 3000)
                        
                    else:
                        #Duplicates
                        self.statusBar.showMessage("File Already Listed: " + path, 3000)
                except Exception:
                    self.statusBar.showMessage("Unable to Add Path:" + path, 3000)
            saveFile(self.fileList, "fileData.txt")
    
    def checkFiles(self):
        ###Iterates through all File and checks validity
        for i in range(self.fileListModel.rowCount()):
            index = self.fileListModel.index(i, 0)
            path = index.data()
            if os.path.exists(path):
                self.fileListModel.itemFromIndex(index).setIcon(QIcon("tick.png"))
            else:
                self.fileListModel.itemFromIndex(index).setIcon(QIcon("cross.png"))
            #Alternative way is to use self.listModel.setData(index, QStandardItem(icon, data))

    #Function that deletes file listing from file and model view
    def deleteFile(self):
        #For multiple Selection
        #Use QListView.clicked() to get index of whatever is clicked
        selection = self.fileListView.selectionModel().selectedIndexes()
        if not selection:
            self.statusBar.showMessage("Nothing Selected to Delete", 3000)
        else:
            print(len(selection))
            while selection:
                i = selection[0] #selecting first item
                if (i.data() in self.fileList):
                    self.fileList.remove(i.data())
                #Using index.row() gets row of index 
                self.fileListModel.removeRows(i.row(),1)
                selection = self.fileListView.selectionModel().selectedIndexes()
            saveFile(self.fileList, "fileData.txt")
            self.statusBar.showMessage("File(s) Deleted", 3000)

    def copyFile(self):
        pathSelection = self.listView.selectionModel().selectedIndexes()

        self.copyWindow = CopyDialog(self.frameGeometry())
        self.copyWindow.show()
        #self.copyWindow = CopyDialog(self.frameGeometry(), None, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        fileSelectionIndexes = self.fileListView.selectionModel().selectedIndexes()
        if not pathSelection:
            self.statusBar.showMessage("No Paths Selected", 3000)
            return
        if not fileSelectionIndexes:
            self.statusBar.showMessage("No Files Selected", 3000)
            return
        ### TO DO ### COUNT AMOUNT OF FILES TO TRANSFER
        fileSelection = []
        #Appending all file selection paths
        for i in fileSelectionIndexes:
            fileSelection.append(i.data())
        overwrite = self.overwriteCheck.isChecked()
        #self.copyWindow.wrapper(fileSelection, pathSelection, overwrite)
        self.copyWindow.copy(fileSelection, pathSelection, overwrite)

        self.checkFiles()


    def loadFilePath(self):
        self.fileList = loadFile('fileData.txt')
        for item in self.fileList:
            ##Check validity of path and assigning icon accordingly
            if(os.path.exists(item)):
                self.fileListModel.appendRow(QStandardItem(QIcon('tick.png'),item))
            else:
                self.fileListModel.appendRow(QStandardItem(QIcon('cross.png'),item))

    ####################
    ## Tree Functions ##
    ####################

    def setupTreeArea(self):
        #Creating Tree System
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setSelectionMode(3)
        self.tree.setWordWrap(True)
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
        copyBt = QPushButton("Copy")
        self.overwriteCheck = QCheckBox("Overwrite")
        self.overwriteCheck.setChecked(True)
        copyBt.pressed.connect(self.copy)

        treeButtonLayout = QGridLayout()
        treeButtonLayout.addWidget(self.overwriteCheck, 0, 0)
        treeButtonLayout.addWidget(copyBt, 0, 1, 1, 5)

        treeLayout.addLayout(treeButtonLayout)
        self.firstGrid.addLayout(treeLayout, 0, 0, 1, 3) #row, column, rowspan, columnspan

        #Set up Checkbox


        ##Setup File Selection
        self.labelFileName = QLabel(self)
        self.labelFileName.setText("File Name:")

        self.lineEditFileName = QLineEdit(self)

        self.labelFilePath = QLabel(self)
        self.labelFilePath.setText("File Path:")

        self.lineEditFilePath = QLineEdit(self)

        gridLayout = QGridLayout()
        
        gridLayout.addWidget(self.labelFileName, 0, 0)
        gridLayout.addWidget(self.lineEditFileName, 0, 1)
        gridLayout.addWidget(self.labelFilePath, 1, 0)
        gridLayout.addWidget(self.lineEditFilePath, 1, 1)
        treeLayout.addLayout(gridLayout)

    def on_treeView_clicked(self, index):
        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        self.currentFileName = fileName
        filePath = self.model.filePath(indexItem)
        self.currentFilePath = filePath

        self.lineEditFileName.setText(fileName)
        self.lineEditFilePath.setText(filePath)

    def copy(self):
        pathSelection = self.listView.selectionModel().selectedIndexes()

        treeSelectionPaths = getTreeSelection(self.tree, self.model)
        print(treeSelectionPaths)
        return
        if not pathSelection:
            self.statusBar.showMessage("No Paths Selected", 3000)
            return
        if not treeSelectionPaths:
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
        
    #The signal passed indicates whether the button is *checked*,
    #  and since our button is not checkable — just clickable — it is always false.
    #Have to set the setCheckable property on the QAction to true
    def onMyToolBarButtonClick(self, s):
        print("click", s)
        newWidget = QWidget()
        newLayout = QVBoxLayout()
        label = QLabel("Changed")   
        newLayout.addWidget(label)
        newWidget.setLayout(newLayout)
        self.setCentralWidget(newWidget)



app = QApplication(sys.argv)

window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop and exit after function call ends
sys.exit(app.exec_())

# Your application won't reach here until you exit and the event 
# loop has stopped.