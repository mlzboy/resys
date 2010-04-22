#! usr/bin/env python
#encoding=utf8

def delfile(filename):
    "使用此方法要有足够的权限，不果不够会抛Permission denied"
    import os
    try:
        os.remove(filename)
        return True
    except:
        print "删除%s文件时出现异常"%filename
        return False
    
def savefile(filename,lines_list):
    f= open(filename,mode="w")
    f.writelines(lines_list)
    f.close()
    
def hasfile(filepath):
    import os.path
    return os.path.isfile(filepath)
    
def hasfolder(folderpath):
    import os.path
    return os.path.exists(folderpath)

def clearfolder(folderpath):
    import os
    for root, dirs, files in os.walk(folderpath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def createfolders(folderpath):
    import os
    try:
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        return True
    except:
        print "创建文件夹是出现异常"
        return False

if __name__=="__main__":
    #savefile("test.csv",["hello\r\n","world\r\n"])
    #print "done!"
    print hasfile("/aa.py")
    print hasfolder("/ddd")
    clearfolder("/home/mlzboy/logs_temp")
    print delfile("/aa.py")
    createfolders("/home/mlzboy/logs_temp3")
    print hasfolder("/home/mlzboy/logs_temp2")