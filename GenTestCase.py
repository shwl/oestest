#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import platform
import xlrd
import color

testCasePath = os.getcwd() + "/testCase/"   #测试脚本生成目标路径

def PauseIfError(testCase, indentation):
    testCase.write(indentation + "color.printRed(\"不符合预期结果,Enter键继续\\n\")\n")
    testCase.write(indentation + "input()\n")

#打印输出参数
def PrintOutParam(sheet_obj, testCase, funcname, i, nrows, colindex, indentation):
    #打印输出参数
    for j in range(i, nrows):
        funcname1 = sheet_obj.cell_value(j, colindex)
        if(j == i or 0 == len(funcname1)):
            param_att = sheet_obj.cell_value(j, colindex + 2)
            param_type = sheet_obj.cell_value(j, colindex + 3)
            param_name = sheet_obj.cell_value(j, colindex + 5)
            if("out" in param_att):
                if("unsigned char*" == param_type):
                    testCase.write(indentation + "if(param_%d != None):\n"%(j - i))
                    testCase.write(indentation + "\ttry:\n");
                    testCase.write(indentation + "\t\tbuf = param_%d.raw[0:int(param_%d[0])].decode('utf-8')\n"%(j - i, j - i + 1))
                    testCase.write(indentation + "\texcept UnicodeDecodeError:\n");
                    testCase.write(indentation + "\t\tbuf = ''.join(['%%02x' %% b for b in param_%d.raw[0:int(param_%d[0])]])\n"%(j - i, j - i + 1))
                    testCase.write(indentation + "\tprint(\"%s:%%s\"%%(buf))\n"%(param_name))
                    testCase.write(indentation + "else:\n")
                    testCase.write(indentation + "\tprint(\"%s:None\")\n"%(param_name))
                elif("int*" == param_type):
                    testCase.write(indentation + "print(\"%s:%%s\"%%(param_%d[0]))\n"%(param_name, j - i))
        else:
            break
    testCase.write(indentation + "\n")

#生成参数列表和测试函数
def GenParamListAndFunc(sheet_obj, testCase, tgdll, funcname, i, nrows, colindex, isRetry):
    indentation = ""    #缩进
    if isRetry:
        indentation = "\t"
    
    #生成参数列表
    param_null = "param_%d = None\n"                                #NULL参数
    param_pu_char = "param_%d = ctypes.create_string_buffer(%s)\n"  #unsigned char*缓存区
    param_pu_char_in = "param_%d = r\"%s\"\n"                       #unsigned char*参数值
    param_p_int = "param_%d = pointer(c_int(%s))\n"                 #int*参数
    param_int = "param_%d = c_int(%s)\n"                            #int参数
    param_u_long = "param_%d = c_ulong(%s)\n"                       #unsigned long参数

    for j in range(i, nrows):
        funcname1 = sheet_obj.cell_value(j, colindex)
        if(j == i or 0 == len(funcname1)):
            param_att = sheet_obj.cell_value(j, colindex + 2)
            param_type = sheet_obj.cell_value(j, colindex + 3)
            param_value = sheet_obj.cell_value(j, colindex + 4)
            #print("param_att:%s\nparam_type:%s\nparam_value:%s\n"%(param_att, param_type, param_value))
            if(isRetry):
                if("unsigned char*" == param_type and "out" == param_att):
                    testCase.write(indentation + param_pu_char%(j - i, "param_%d[0]"%(j - i + 1)))
            else:
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
    funcendstr = ")\n"  #函数结束字符串
    printres = "print(funcname, \"res:\", res)\n\n"    #输出函数名称和返回值
    testCase.write(indentation + "res = %s.%s("%(tgdll, funcname))
    if(j + 1 == nrows):
        j = j + 1
    for k in range(i, j):
        if(k != i):
            testCase.write(", ")
        testCase.write("param_%d"%(k - i))
    testCase.write(funcendstr + indentation + printres)
    PrintOutParam(sheet_obj, testCase, funcname, i, nrows, colindex, indentation)

#接口测试函数
def GenTestFunction(sheet_obj, testCase, tgdll):
    nrows = sheet_obj.nrows    #获取行总数
    print("sheet_nrows:", nrows)
    rowindex = 4        #测试函数读取起始行
    
    for i in range(rowindex, nrows):
        colindex = 0    #起始列
        funcname = sheet_obj.cell_value(i, colindex)
        if(0 == len(funcname)):
            continue
        else:
            testCase.write("print('\\n')\n")
            defaultres = int(sheet_obj.cell_value(i, colindex + 1))
            testCase.write("defaultres = %d\nfuncname = '%s'\n"%(defaultres, funcname));
            print("funcname:%s\ndefaultres:%d\n"%(funcname, defaultres))
            GenParamListAndFunc(sheet_obj, testCase, tgdll, funcname, i, nrows, colindex, False)
            testCase.write("if(res == 0):\n");
            GenParamListAndFunc(sheet_obj, testCase, tgdll, funcname, i, nrows, colindex, True)
            testCase.write("if(res != defaultres):\n");
            PauseIfError(testCase, "\t")

#生成测试动态库信息
def GenTestDllInfo(sheet_obj, testCase):
    rowindex = 1
    colindex = 0
    tgdll = "tgdll"
    if 'Windows' in platform.system():
        dllname = sheet_obj.cell_value(rowindex, colindex)
        dllpath = sheet_obj.cell_value(rowindex, colindex + 1)
        calltype = sheet_obj.cell_value(rowindex, colindex + 2)
        print("dllpath:%s\ndllname:%s\ncalltype:%s\n"%(dllpath, dllname, calltype))
        testCase.write("os.chdir(r'%s')\n"%(dllpath))
        if calltype == "stdcall":
            testCase.write("%s = ctypes.windll.LoadLibrary(r'%s')\n"%(tgdll, dllname))
        else:
            testCase.write("%s = ctypes.cdll.LoadLibrary(r'%s')\n"%(tgdll, dllname))
    else:
        dllname = sheet_obj.cell_value(rowindex + 1, colindex)
        dllpath = sheet_obj.cell_value(rowindex + 1, colindex + 1)
        testCase.write("%s = cdll.LoadLibrary(r'%s/%s')\n"%(tgdll, dllpath, dllname))
    testCase.write("\n")
    GenTestFunction(sheet_obj, testCase, tgdll)
    
#生成测试文件
def GenTestCase(sheet_obj, sheet_name):
    #写入测试文件头
    testCaseFile = testCasePath + sheet_name + ".py"
    testCase = open(testCaseFile, "w", encoding = 'utf-8')
    testBaseFile = r"testBase.txt"
    testBase = open(testBaseFile, "r", encoding = 'utf-8')
    testCase.write(testBase.read() + "\n\n")
    testBase.close()
    print("sheet_name:", sheet_name)
    GenTestDllInfo(sheet_obj, testCase)
    testCase.close()

#读取并根据配置文件生成测试脚本
def ReadConfigFile(excelFile, testCasePath):
    if False == os.path.exists(testCasePath):
        os.makedirs(testCasePath)
        
    book = xlrd.open_workbook(excelFile)    #得到Excel文件的book对象，实例化对象
    sheet_count = len(book.sheets())        #获得sheet个数
    print("sheet_count:", sheet_count)
    
    runAllCase = open(testCasePath + "RunAllCase.py", "w", encoding = 'utf-8')
    runAllCase.write("# -*- coding: UTF-8 -*- \n\n");

    for index in range(sheet_count):
        sheet_obj = book.sheet_by_index(index)      #通过sheet索引获得sheet对象
        sheet_name = book.sheet_names()[index]      #获得指定索引的sheet表名字
        GenTestCase(sheet_obj, sheet_name)
        runAllCase.write("import %s\n"%(sheet_name));
    runAllCase.close()
        
def main():
    excelFile = r"test.xlsx"
    ReadConfigFile(excelFile, testCasePath)
if __name__ == "__main__":
    main()
