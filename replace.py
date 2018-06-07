#coding=gb2312
import sys
import fileinput
import re
import os,time
import datetime

outFilePath	= "outfile.txt";
inFilePath	= "infile.txt";

def getParam(param):
    res = "";
    if param.strip()=='':
        return res;
    param = param.replace("(", "");
    param = param.replace(")", "");
    #print("param:", param);

    paramlist = param.split(",")
    for it in paramlist:
        if it.strip()!='':
            #print("it:", it);
            m = re.match(r"(\W*)(\w*)(\W*)(\w*)(\W*)(\w*)(\W*)", it);
            if m:
                #print("m.groups:", m.groups())
                for j in reversed(m.groups()):
                    if j.strip()!='':
                        res += j;
                        res += ","
                        break;
            else:
                print("ERROR!");
    res += "\n"
    return res;
def DelLastChar(str, num):
    str_list=list(str)
    for i in range(0,num):
        str_list.pop()
    return "".join(str_list)

def writeFunc(outFile, funcName, param):
    #print("funcName:", funcName);
    param = DelLastChar(param, 2);
    outFile.write("\n{\n\tif(!m_PKCS11Func){\n\t\treturn TG_UKEY_NOT_INIT;\n\t}");
    outFile.write("\n\tif(!m_PKCS11Func->%s){\n\t\treturn TG_UKEY_NOT_SUPPORT_FUNC;\n\t}"%funcName);
    outFile.write("\n\tCK_RV rv = m_PKCS11Func->%s(%s);"%(funcName, param));
    outFile.write("\n\treturn rv;");
    outFile.write("\n}\n");

def relpace():
        outFile = open(outFilePath, "w");
        inFile = open(inFilePath, "r");
        
        while 1:
                lines = inFile.readlines(10000);
                if not lines:
                        break;
                funcName = "";
                strparam = "";
                for line in lines:
                    m = re.match(r"\W*PKCS11_DECLARE_FUNCTION\((.*)", line);
                    if m:
                        #print("m.group(0):", m.group(0));
                        #print("m.group(1):", m.group(1));
                        strTmp = m.group(1)
                        m2 = re.match(r"(\w+),(.*)", strTmp);
                        if m2:
                            #print("m2.group(0):", m2.group(0));
                            #print("m2.group(1):", m2.group(1));
                            #print("m2.group(2):", m2.group(2));
                            funcName = m2.group(1);
                            m3 = re.match(r"(.*)(\);)", m2.group(2));
                            if m3:
                                #print("m3.group(0):", m3.group(0));
                                #print("m3.group(1):", m3.group(1));
                                strparam += getParam(m3.group(1));
                                outFile.write("CK_RV CPKCS11Method::" + funcName + m3.group(1));
                                writeFunc(outFile, funcName, strparam)
                                strparam = "";
                            else:
                                strparam += getParam(m2.group(2));
                                outFile.write("CK_RV CPKCS11Method::" + funcName + m2.group(2));
                        else:
                            print("ERROR!");
                    else:
                        m3 = re.match(r"(.*)(\);)", line);
                        if m3:
                            #print("m3.group(0):", m3.group(0));
                            #print("m3.group(1):", m3.group(1));
                            strparam += getParam(m3.group(1));
                            outFile.write(m3.group(1));
                            writeFunc(outFile, funcName, strparam)
                            strparam = "";
                        else:
                            strparam += getParam(line);
                            outFile.write(line);
        inFile.close();
        outFile.close();

def main():
        relpace();
        print("relpace end!")

if __name__ == "__main__":
        main()
