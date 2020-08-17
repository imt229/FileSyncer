from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore

import os
import shutil


class CopyThread(QThread):
    update = pyqtSignal(int, int, str)

    def __init__(self, copyList, destinationList, overwrite, errorModel, fileCounterLabel, progressBar, percentageLabel, fileCount, totalAmountOfFiles, amountOfDest):
        super(QThread,self).__init__()
        self.errorModel = errorModel
        self.copyList = copyList
        self.destinationList = destinationList
        self.overwrite = overwrite
        self.stop = False
        self.fileCounterLabel = fileCounterLabel
        self.progressBar = progressBar
        self.percentageLabel = percentageLabel
        self.totalFileCount = 0
        self.fileCount = fileCount
        self.totalAmountOfFiles = totalAmountOfFiles
        self.amountOfDest = amountOfDest

    def __del__(self):
        self.wait()

    #Function for recursively copying contents of a folder to a folder that has just been created
    def folderCopy(self, path, fileList):
        del fileList[0]
        for file in fileList:
            if(self.stop):
                print("hi")
                return
            self.pathFileCount += 1
            self.totalFileCount += 1
            self.update.emit(self.pathFileCount, self.totalFileCount, self.pathForLabel)
            #self.updateCopyWindowLabels()
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

    def copy(self, copyPaths, destinationList, overwrite):
        for pathIndex in destinationList:
            self.pathFileCount = 0
            self.pathForLabel = pathIndex.data()
            for filePath in copyPaths:
                if(self.stop):
                    print("hi")
                    return
                path = pathIndex.data()

                self.pathFileCount += 1
                self.totalFileCount += 1
                self.update.emit(self.pathFileCount, self.totalFileCount, self.pathForLabel)
                #self.updateCopyWindowLabels()
                
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
        print("end")

    def updateCopyWindowLabels(self):
        #Copying file# of amountOfFiles Files to DestinationPath
        self.fileCounterLabel.setText("Copying " + str(self.pathFileCount) + " of " + str(self.fileCount) + "Files to " + self.pathForLabel)

        #Calculate percent and set progressbar
        percent = int(self.totalFileCount*100/self.totalAmountOfFiles)
        self.progressBar.setValue(percent)

        ##For Grammar Reasons
        #Singular Destinations
        if (self.amountOfDest == "1"):
            self.percentageLabel.setText(str(percent) + "% Complete: " + str(self.totalFileCount) + " of " + str(self.totalAmountOfFiles) + " Files to " + self.amountOfDest + " Destination")
        # Plural
        else:
            self.percentageLabel.setText(str(percent) + "% Complete: " + str(self.totalFileCount) + " of " + str(self.totalAmountOfFiles) + " Files to " + self.amountOfDest + " Destinations")

    def run(self):
        self.copy(self.copyList, self.destinationList, self.overwrite)