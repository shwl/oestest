#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import platform
import xlrd
import color

excelFile = r"test.xlsx"
testBaseFile = r"testBase.txt"
testCasePath = os.getcwd() + "/testCase/"

if False == os.path.exists(testCasePath):
    os.makedirs(testCasePath)

book = xlrd.open_workbook(excelFile)    #得到Excel文件的book对象，实例化对象
sheet_count = len(book.sheets())        #获得sheet个数
print("sheet_count:", sheet_count)
index = 0
sheet0 = book.sheet_by_index(index)     #通过sheet索引获得sheet对象
sheet_name = book.sheet_names()[index]  #获得指定索引的sheet表名字

#写入测试文件头
testCaseFile = testCasePath + sheet_name + ".py"
testCase = open(testCaseFile, "w", encoding = 'utf-8')
testBase = open(testBaseFile, "r", encoding = 'utf-8')
testCase.write(testBase.read() + "\n\n")
testBase.close()
print("sheet_name:", sheet_name)

#读取、写入动态库信息
rowindex = 1
colindex = 0
tgdll = "tgdll"

if 'Windows' in platform.system():
    dllname = sheet0.cell_value(rowindex, colindex)
    dllpath = sheet0.cell_value(rowindex, colindex + 1)
    calltype = sheet0.cell_value(rowindex, colindex + 2)
    print("dllpath:%s\ndllname:%s\ncalltype:%s\n"%(dllpath, dllname, calltype))
    testCase.write("os.chdir(r'%s')\n"%(dllpath))
    if calltype == "stdcall":
        testCase.write("%s = ctypes.windll.LoadLibrary(r'%s')\n"%(tgdll, dllname))
    else:
        testCase.write("%s = ctypes.cdll.LoadLibrary(r'%s')\n"%(tgdll, dllname))
else:
    dllname = sheet0.cell_value(rowindex + 1, colindex)
    dllpath = sheet0.cell_value(rowindex + 1, colindex + 1)
    testCase.write("%s = cdll.LoadLibrary(r'%s/%s')\n"%(tgdll, dllpath, dllname))
testCase.write("\n")

#接口测试
nrows = sheet0.nrows    #获取行总数
print("sheet_nrows:", nrows)
rowindex = 4
funcendstr = ")\n"
printres = "print(funcname + \"res:\", res)\n\n"
param_null = "param_%d = None\n"
param_pu_char = "param_%d = ctypes.create_string_buffer(%s)\n"
param_pu_char_in = "param_%d = r\"%s\"\n"
param_p_int = "param_%d = pointer(c_int(%s))\n"
param_int = "param_%d = c_int(%s)\n"
param_u_long = "param_%d = c_ulong(%s)\n"

for i in range(rowindex, nrows):
    colindex = 0
    funcname = sheet0.cell_value(i, colindex)
    if(0 == len(funcname)):
        continue
    else:
        defaultres = int(sheet0.cell_value(i, colindex + 1))
        testCase.write("defaultres = %d\nfuncname = '%s'\n"%(defaultres, funcname));
        print("funcname:%s\ndefaultres:%d\n"%(funcname, defaultres))
        #参数初始化
        for j in range(i, nrows):
            funcname1 = sheet0.cell_value(j, colindex)
            if(j == i or 0 == len(funcname1)):
                param_att = sheet0.cell_value(j, colindex + 2)
                param_type = sheet0.cell_value(j, colindex + 3)
                param_value = sheet0.cell_value(j, colindex + 4)
                #print("param_att:%s\nparam_type:%s\nparam_value:%s\n"%(param_att, param_type, param_value))
                if("unsigned char*" == param_type):
                    if("out" == param_att):
                        if(0 == int(param_value)):
                            testCase.write(param_null%(j - i))
                        else:
                            testCase.write(param_pu_char%(j - i, param_value))
                    elif("in" == param_att):
                        testCase.write(param_pu_char_in%(j - i, param_value))
                    else:
                        color.printRed("error")
                elif("int*" == param_type):
                    testCase.write(param_p_int%(j - i, param_value))
                elif("int" == param_type):
                    testCase.write(param_int%(j - i, param_value))
                elif("unsigned long" == param_type):
                    testCase.write(param_u_long%(j - i, param_value))
                else:
                    color.printRed("error")
            else:
                break
        #函数调用
        testCase.write("res = %s.%s("%(tgdll, funcname))
        if(j + 1 == nrows):
            j = j + 1
        for k in range(i, j):
            if(k != i):
                testCase.write(", ")
            testCase.write("param_%d"%(k - i))
        testCase.write(funcendstr + printres)
        
        #打印输出参数
        for j in range(i, nrows):
            funcname1 = sheet0.cell_value(j, colindex)
            if(j == i or 0 == len(funcname1)):
                param_att = sheet0.cell_value(j, colindex + 2)
                param_type = sheet0.cell_value(j, colindex + 3)
                param_name = sheet0.cell_value(j, colindex + 5)
                if("out" in param_att):
                    if("unsigned char*" == param_type):
                        testCase.write("if(param_%d != None):\n"%(j - i))
                        testCase.write("\ttry:\n");
                        testCase.write("\t\tbuf = param_%d.raw[0:int(param_%d[0])].decode('utf-8')\n"%(j - i, j - i + 1))
                        testCase.write("\texcept UnicodeDecodeError:\n");
                        testCase.write("\t\tbuf = ''.join(['%%02x' %% b for b in param_%d.raw[0:int(param_%d[0])]])\n"%(j - i, j - i + 1))
                        testCase.write("\tprint(\"%s:%%s\"%%(buf))\n"%(param_name))
                        testCase.write("else:\n")
                        testCase.write("\tprint(\"%s:None\")\n"%(param_name))
                    elif("int*" == param_type):
                        testCase.write("print(\"%s:%%s\"%%(param_%d[0]))\n"%(param_name, j - i))
            else:
                break
        testCase.write("print('\\n')")
        testCase.write("\n")

        #输出参数根据返回值重新申请缓存区
        print("funcname:%s\ndefaultres:%s\n"%(funcname, defaultres))
        testCase.write("if(res == defaultres):\n");
        #参数初始化
        for j in range(i, nrows):
            funcname1 = sheet0.cell_value(j, colindex)
            if(j == i or 0 == len(funcname1)):
                param_att = sheet0.cell_value(j, colindex + 2)
                param_type = sheet0.cell_value(j, colindex + 3)
                param_value = sheet0.cell_value(j, colindex + 4)
                #print("param_att:%s\nparam_type:%s\nparam_value:%s\n"%(param_att, param_type, param_value))
                if("unsigned char*" == param_type):
                    if("out" == param_att):
                        testCase.write("\t" + param_pu_char%(j - i, "param_%d[0]"%(j - i + 1)))
            else:
                break
        #函数调用
        testCase.write("\tres = %s.%s("%(tgdll, funcname))
        if(j + 1 == nrows):
            j = j + 1
        for k in range(i, j):
            if(k != i):
                testCase.write(", ")
            testCase.write("param_%d"%(k - i))
        testCase.write(funcendstr + "\t" + printres)
        
        #打印输出参数
        for j in range(i, nrows):
            funcname1 = sheet0.cell_value(j, colindex)
            if(j == i or 0 == len(funcname1)):
                param_att = sheet0.cell_value(j, colindex + 2)
                param_type = sheet0.cell_value(j, colindex + 3)
                param_name = sheet0.cell_value(j, colindex + 5)
                if("out" in param_att):
                    if("unsigned char*" == param_type):
                        testCase.write("\tif(param_%d != None):\n"%(j - i))
                        testCase.write("\t\ttry:\n");
                        testCase.write("\t\t\tbuf = param_%d.raw[0:int(param_%d[0])].decode('utf-8')\n"%(j - i, j - i + 1))
                        testCase.write("\t\texcept UnicodeDecodeError:\n");
                        testCase.write("\t\t\tbuf = ''.join(['%%02x' %% b for b in param_%d.raw[0:int(param_%d[0])]])\n"%(j - i, j - i + 1))
                        testCase.write("\t\tprint(\"%s:%%s\"%%(buf))\n"%(param_name))
                        testCase.write("\telse:\n")
                        testCase.write("\t\tprint(\"%s:None\")\n"%(param_name))
                    elif("int*" == param_type):
                        testCase.write("\tprint(\"%s:%%s\"%%(param_%d[0]))\n"%(param_name, j - i))
            else:
                break
        testCase.write("\tprint('\\n')")
        testCase.write("\t\n")
testCase.close()
