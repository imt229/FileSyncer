import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore
from genericFunctions import *
from CopyThread import CopyThread


import shutil
import time
from multiprocessing import Process


# The `Qt` namespace has a lot of attributes to customise
# widgets. See: http://doc.qt.io/qt-5/qt.html
class CopyDialog(QDialog):

    #MemberVariables:


    def __init__(self, parentDimensions, *args, **kwargs):
        super(QDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Copy Progress")
        self.setWindowIcon(QIcon("document--arrow.png"))
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: Linen;")

        width = int(parentDimensions.width()/2)
        height = int(parentDimensions.height()/2)
        self.setGeometry(parentDimensions.x()+width/2, parentDimensions.y()+height/2, width, height)
        self.setMinimumSize(400,200)


        self.fileCounterLabel = QLabel("Copying 1 of 85 Files to D:/Foo/Foo/fiawgjoawergnjoawrgioajwg")
        #self.fileCounter.setText("FOo")
        self.fileCounterLabel.setFont(QFont("Arial", 10))

        self.percentageLabel = QLabel("0% Complete")
        self.percentageLabel.setFont(QFont("Arial", 14))

        self.progressBar = QProgressBar()
        self.progressBar.setValue(0)

        failedTransfersLabel = QLabel("Failed Transfer Log")
        failedTransfersLabel.setFont(QFont("Arial", 12))

        self.errorView = QListView()
        self.errorView.setFont(QFont("Arial", 10))
        self.errorModel = QStandardItemModel()
        self.errorView.setModel(self.errorModel)
        self.errorLogList = []

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.pressed.connect(self.cancelButtonFunc)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.fileCounterLabel)
        layout.addWidget(self.percentageLabel)
        layout.addWidget(self.progressBar)
        layout.addWidget(failedTransfersLabel)
        layout.addWidget(self.errorView)
        layout.addWidget(self.cancelButton)



        #https://doc.qt.io/qt-5/qt.html#WindowModality-enum
        #Changing this property while the window is visible has no effect;
        #you must hide() the widget first, then show() it again.
        self.setWindowModality(2)
        #self.show()
        
        #self.setWindowTitle("Copy Progress")
    
    def increaseProgress(self):
        count = 0

        '''
        while (count < 100):
            timeNow = time.time()
            if timeNow - startTime > 10:
                count += 1
                startTime = timeNow
                self.progressBar.setValue(count)
        '''
    #Button that closes copying dialog, effectively stopping copying as well
    #This is because copying functions resides in dialog class
    def cancelButtonFunc(self):
        self.copyThread.stop = True
        while(self.copyThread.isRunning()):
            x =1
        self.copyThread.quit()
        self.copyThread.terminate()
        self.copyThread = ""
    
    def wrapper(self, copyList, destinationList, overwrite):
        self.proc = Process(target=self.copy, args=(copyList, destinationList, overwrite), daemon=True)
        self.proc.start()

    def copy(self, copyList, destinationList, overwrite):
        print("start")
        self.fileCounterLabel.setText("Preparing Files")
        copyPaths = []
        self.fileCount = 0
        for i in copyList:
            self.fileCount += self.countFiles(i, copyPaths)[0]

        removeList = []
        for destination in destinationList:
            if (not os.path.exists(destination.data())):
                removeList.append(destination)
        
        for removeDest in removeList:
            destinationList.remove(removeDest)
            self.errorModel.appendRow(QStandardItem(QIcon("cross.png"), "Destination Path " + removeDest.data() + " not found, cannot complete any copying"))

        self.amountOfDest = len(destinationList)
        self.totalAmountOfFiles = self.fileCount * self.amountOfDest
        self.amountOfDest = str(self.amountOfDest)
        self.totalFileCount = 0

        self.copyThread = CopyThread(copyPaths, destinationList, overwrite, self.errorModel, self.fileCounterLabel, self.progressBar, self.percentageLabel, self.fileCount, self.totalAmountOfFiles, self.amountOfDest)
        self.copyThread.start()
        self.copyThread.update.connect(self.updateCopyWindowLabels)
        return
        for pathIndex in destinationList:
            self.pathFileCount = 0
            self.pathForLabel = pathIndex.data()
            for filePath in copyPaths:
                path = pathIndex.data()
                self.pathFileCount += 1
                self.totalFileCount += 1
                self.updateCopyWindowLabels()
                
                if (isinstance(filePath, list)):
                    folder = filePath[0]
                    fileName = os.path.basename(folder)
                    newFilePath = os.path.join(path, fileName)
                    if (os.path.exists(newFilePath)):
                        if (overwrite):
                            print("foo")
                    else:
                        os.makedirs(newFilePath)
                        self.folderCopy(newFilePath, filePath)


                else:
                    if (overwrite):
                        try:
                            shutil.copy(filePath, path)
                        except Exception as e:
                            ###Add log message
                            self.errorModel.appendRow(QStandardItem(QIcon("cross.png"), "Overwrite Copy Unexpected Error: " + str(e) + filePath + " to " + path))
                    else:
                        fileName = os.path.basename(filePath)
                        newFilePath = os.path.join(path, fileName)
                        index = 0
                        isDir = os.path.isdir(filePath)

                        ## Open the file and raise an exception if it exists
                        try:

                            # Copy the file and automatically close files at the end
                            f = os.open(newFilePath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                            shutil.copy2(filePath, newFilePath)
                            os.close(f)

                        #If file exists
                        except:
                            if (isDir):
                                self.errorModel.appendRow(QStandardItem(QIcon("cross.png"),"Unexpected Error: Folder Condition for transfer of " + filePath + " to " + newFilePath))
                            else:
                                #Add numbers until we find a file path that does not exist
                                while(os.path.exists(newFilePath)):
                                    #Seperate name of file and extension
                                    #Use newFilePath to construct name of file that hopefully does not exist
                                    newFilePath, extension = os.path.splitext(fileName)
                                    index += 1
                                    newFilePath += " (" + str(index) + ")" + extension
                                    newFilePath = os.path.join(path, newFilePath)
                                try:

                                    # Copy the file and automatically close files at the end
                                    f = os.open(newFilePath, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                                    shutil.copy2(filePath, newFilePath)
                                    os.close(f)
                                except Exception as e:
                                    ###Add log message
                                    self.errorModel.appendRow(QStandardItem(QIcon("cross.png"), "Overwrite Copy Unexpected Error:" + str(e) + " for transfer of " + filePath + " to " + newFilePath))
        self.fileCounterLabel.setText("Finished Transfer: ")
        self.cancelButton.setText("Close")

    #Count total amount of files that need to be copied as well as collating all file paths
    #When we encounter a folder, we create a list for that folder such that root folder is index 0 and all other subfiles are stored in that list
    #So if you have a list within a list, you know that the first list is root folder, second list is a subfolder and all the files in the subfolder
    def countFiles(self, path, pathList):
        fileCount = 0

        #Only add valid paths to list of files that need to be copied
        if(os.path.exists(path)):
            fileCount += 1

            #If file we're checking is a folder, we create a new list and append file
            #New List represents folder and all its contents
            if os.path.isdir(path):
                folderList = []
                folderList.append(path)
                pathList.append(folderList)

                #Go through contents of folder, if we encounter another folder run function recursively for subfolder
                with os.scandir(path) as it:
                    for i in it:
                        if(os.path.isdir(i.path)):
                            try:
                                tempList = self.countFiles(i.path, folderList)
                                fileCount += tempList[0]
    
                            except Exception as e:
                                self.errorModel.appendRow(QStandardItem(QIcon("cross.png"),"Unexpected Error: " + str(e) + "for", i.path))
                        else:
                            folderList.append(i.path)
                            fileCount += 1
            else:
                pathList.append(path)
        else:
            self.errorModel.appendRow(QStandardItem(QIcon("cross.png"), "File Path Not Valid for File: " + path))
        return [fileCount, pathList]

    #Function for recursively copying contents of a folder to a folder that has just been created
    def folderCopy(self, path, fileList):
        del fileList[0]
        for file in fileList:
            self.pathFileCount += 1
            self.totalFileCount += 1
            self.updateCopyWindowLabels()
            if (isinstance(file, list)):
                folderPath = file[0]
                folderName = os.path.basename(folderPath)
                newFolderPath = os.path.join(path, folderName)
                os.makedirs(newFolderPath)
                self.folderCopy(newFolderPath, file)
            else:
                fileName = os.path.basename(file)
                newFilePath = os.path.join(path, fileName)
                try:
                    shutil.copy2(file, newFilePath)
                except Exception as e:
                    self.errorModel.appendRow(QStandardItem(QIcon("cross.png"), "Unexpected Error: " + str(e) + " - Unable to copy " + file + " to " + newFilePath))
    

    #Function used to update labels on QDialog Window so that user is updated
    def updateCopyWindowLabels(self, pathFileCount, totalFileCount, pathForLabel):
        #Copying file# of amountOfFiles Files to DestinationPath
        self.fileCounterLabel.setText("Copying " + str(pathFileCount) + " of " + str(self.fileCount) + " Files to " + pathForLabel)

        #Calculate percent and set progressbar
        percent = int(totalFileCount*100/self.totalAmountOfFiles)
        self.progressBar.setValue(percent)

        ##For Grammar Reasons
        #Singular Destinations
        if (self.amountOfDest == "1"):
            self.percentageLabel.setText(str(percent) + "% Complete: " + str(totalFileCount) + " of " + str(self.totalAmountOfFiles) + " Files to " + self.amountOfDest + " Destination")
        # Plural
        else:
            self.percentageLabel.setText(str(percent) + "% Complete: " + str(totalFileCount) + " of " + str(self.totalAmountOfFiles) + " Files to " + self.amountOfDest + " Destinations")