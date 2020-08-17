import json
import sys
import datetime
import os
import sched

#Set settings for QList View
def viewSettings(view):
    view.setSelectionMode(3) #0 = NoSelection, 1 = SingleSelection, 2 = MultiSelection, 3 = ExtendedSelection, 4 = Contigious Selection
    view.setSelectionRectVisible(True)
    view.setWordWrap(True)

#Load file for saved user input
def loadFile(file):
    ##TO DO ##### - log
    try:
        with open(file) as openFile:
            return json.load(openFile)
    except FileNotFoundError:
        ###Add log message
        return []
    except Exception as e:
        print("Unexpected error:", e)
        return []

def saveFile(list, file):
    try:
        with open(file, 'w') as outfile:
            json.dump(list, outfile)
    except Exception as e:
        ###Add log messagewd
        print("Unexpected error:", e)
        print("Save File Exception")


#Get currently selected in tree views, returns a list of file paths
def getTreeSelection(tree, model):
    selection = []
    indexes = tree.selectionModel().selectedIndexes()

    for i in range(0,len(indexes), 4):
        #print(self.model.index(i.row(), 0, i.parent()))
        #print (self.model.filePath(i))
        selection.append(model.filePath(indexes[i]))
    return selection

def countFiles(path, pathList):
    fileCount = 0
    if(os.path.exists(path)):
        if os.path.isdir(path):
            with os.scandir(path) as it:
                for i in it:
                    pathList.append(i.path)
                    if(os.path.isdir(i.path)):
                        try:
                            fileCount += countFiles(i.path)
   
                        except Exception as e:
                            print("Unexpected Error: ", e)

                    fileCount += 1
        else:
            return 1

    return fileCount



###Tests####
'''
testPath = "D:/"
print(os.path.exists(testPath))
print(datetime.datetime.now())
print(countFiles(testPath))
print(datetime.datetime.now())
'''