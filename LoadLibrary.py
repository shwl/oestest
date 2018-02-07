#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import ctypes
from ctypes import *
import color

os.chdir(r'H:\git\ak-client-gov\bin\Debug');
TGSignSM2 = cdll.LoadLibrary(r'TGSignSM2.dll');
dllName = b'SKFAPI20066.dll';
print(dllName);
ret = TGSignSM2.SM2_SetDllName(dllName);
print(ret);

certType = 1;
bufLen = 1024;
buf = ctypes.create_string_buffer(bufLen);
bufLen = pointer(c_ulong(bufLen));
ret = TGSignSM2.SM2_GetCertList(None, certType, buf, bufLen);
buf = buf.value.decode('utf-8');
print("ret:%d, bufLen:%d, buf:%s"%(ret, bufLen[0], buf))
