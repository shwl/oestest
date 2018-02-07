#!/usr/bin/python
# -*- coding: UTF-8 -*-

import xlrd

excelPath = r"test.xlsx"
book = xlrd.open_workbook(excelPath)    #得到Excel文件的book对象，实例化对象
index = 0
sheet0 = book.sheet_by_index(index)     #通过sheet索引获得sheet对象
sheet_name = book.sheet_names()[0]      #获得指定索引的sheet表名字
print("sheet_name:", sheet_name);
sheet1 = book.sheet_by_name(sheet_name) #通过sheet名字来获取，当然如果知道sheet名字就可以直接指定
nrows = sheet0.nrows    #获取行总数
print("sheet_nrows:", nrows);
ncols = sheet0.ncols    #获取列总数
print("sheet_ncols:", ncols);

#循环打印内容
for i in range(nrows):
    for j in range(ncols):
        cell_value = sheet0.cell_value(i, j)
        print("(%d,%d):%s"%(i, j, cell_value))
