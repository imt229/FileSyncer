import os
import datetime
from fpdf import FPDF
from collections import OrderedDict

def calculateSize(size):
    if (size >= 1048576 * 1024):
        size = float(size)/(1048576*1024)
        size = "{:.2f}".format(size)
        size = str(size) + " GB"
    elif (size >= 1048576):
        size = float(size)/1048576
        size = "{:.2f}".format(size)
        size = str(size) + " MB"
    elif (size >= 1024):
        size = float(size)/1024
        size = "{:.2f}".format(size)
        size = str(size) + " KB"
    else:
        size = str(size) + " bytes"
    return size

def collateSize(path):
    byteCount = 0
    fileCount = 0
    folderCount = 1
    smallFolderCount = 0
    with os.scandir(path) as it:
        for i in it:
            fileName = str(i)
            fileName = fileName[11:len(fileName) - 2]
            if(os.path.isdir(path+"\\" + fileName)):
                tempList = collateSize(path+"\\" + fileName)
                byteCount += tempList[0]
                fileCount += tempList[1]
                folderCount += tempList[2]
                smallFolderCount += tempList[3]

                #Checking if returned folder size is less than 5kb
                if (byteCount <1024*5):
                    smallFolderCount += 1
            else:
                byteCount += i.stat().st_size
                fileCount += 1

    return [byteCount, fileCount, folderCount, smallFolderCount]



pdf = FPDF() 
  
# Add a page 
pdf.add_page() 
  
# set style and size of font  
# that you want in the pdf 
pdf.set_font("Arial", size = 20) 
  
# create a cell 
pdf.cell(40, 10, txt = "Modification Dates",  border = 0,
         ln = 1, align = 'L') 

currentTime = str(datetime.datetime.now())
currentTime = currentTime[:len(currentTime)-7]
pdf.set_font("Arial", size = 18) 
pdf.cell(40, 10, txt = "Report Generated at: " + currentTime,  border = 0,
         ln = 1, align = 'L')


currentPath = "G:\My Drive\Olivet Company\Sales Team\Logistic\\"
#pdf.cell(40, 10, txt = "Report Root Path: " + os.getcwd(),  border = 0, ln = 1, align = 'L')
pdf.cell(40, 10, txt = "Report Root Path: " + currentPath,  border = 0, ln = 1, align = 'L')

pdf.set_font("Arial", size = 8) 
# add another cell 
pdf.cell(75, 9, txt = "Name", border = 1,
         ln = 0, align = 'L')
pdf.cell(22, 9, txt = "Size", border = 1,
         ln = 0, align = 'L')
pdf.cell(15, 9, txt = "Files", border = 1,
         ln = 0, align = 'L') 
pdf.cell(15, 9, txt = "Folders", border = 1,
                ln = 0, align = 'L')  
pdf.cell(40, 9, txt = "Modified", border = 1,
         ln = 0, align = 'L')
pdf.cell(23, 9, txt = "Subfolders < 5kb", border = 1,
         ln = 1, align = 'L')  

fileMap = {}
with os.scandir(currentPath) as it:
    for i in it:
        #Get stats of each file
        stats = i.stat()

        #Time
        time = datetime.datetime.fromtimestamp(stats.st_mtime)
        time = str(time)
        time = time[:len(time)-7]
        
        #File Name
        fileName = str(i)
        fileName = fileName[11:len(fileName) - 2]

        size = 0
        fileCount = 0
        folderCount = 0
        smallFolderCount = 0
        if(os.path.isdir(currentPath + fileName)):
            tempList = collateSize(currentPath + fileName)
            size = tempList[0]
            fileCount = tempList[1]
            folderCount = tempList[2] - 1
            smallFolderCount = tempList[3]


        else:
            #File size
            size = stats.st_size
            fileCount = 1

        size = calculateSize(size)
        
        fileMap[fileName] = [size,fileCount,folderCount,time,smallFolderCount]

        '''
        pdf.cell(75, 9, txt = fileName, border = 1,
         ln = 0, align = 'L')
        pdf.cell(22, 9, txt = size, border = 1,
                ln = 0, align = 'L')
        pdf.cell(15, 9, txt = str(fileCount), border = 1,
                ln = 0, align = 'L')  
        pdf.cell(15, 9, txt = str(folderCount), border = 1,
                ln = 0, align = 'L')  
        pdf.cell(40, 9, txt = time, border = 1,
                ln = 1, align = 'L') 
        '''


for key in sorted(fileMap):
    value = fileMap[key]
    pdf.cell(75, 9, txt = key, border = 1,
        ln = 0, align = 'L')
    pdf.cell(22, 9, txt = value[0], border = 1,
        ln = 0, align = 'L')
    pdf.cell(15, 9, txt = str(value[1]), border = 1,
        ln = 0, align = 'L')  
    pdf.cell(15, 9, txt = str(value[2]), border = 1,
        ln = 0, align = 'L')  
    pdf.cell(40, 9, txt = value[3], border = 1,
        ln = 0, align = 'L') 
    pdf.cell(23, 9, txt = str(value[4]), border = 1,
        ln = 1, align = 'L') 


# save the pdf with name .pdf 
pdf.output("Report.pdf")    


