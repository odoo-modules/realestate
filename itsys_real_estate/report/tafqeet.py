# -*- coding: utf-8 -*-
#!/usr/bin/env python

def DITAFQEET( X ):
    ret = 'None'
    Letter1=""
    Letter2=""
    Letter3=""
    Letter4=""
    Letter5=""
    Letter6=""
    dblOriginal = X
    #c = Format(Round(X, 0) '000000000000')
    c = "%012d" % (X,)

    #C1 = Val(Mid(c, 12, 1)) 
    C1 = int(c[11:12])
    if (C1 == 1):
        Letter1 = 'واحد'
    elif (C1 == 2):
        Letter1 = 'اثنان'
    elif (C1 == 3):
        Letter1 = 'ثلاثة'
    elif (C1 == 4):
        Letter1 = 'اربعة'
    elif (C1 == 5):
        Letter1 = 'خمسة'
    elif (C1 == 6):
        Letter1 = 'ستة'
    elif (C1 == 7):
        Letter1 = 'سبعة'
    elif (C1 == 8):
        Letter1 = 'ثمانية'
    elif (C1 == 9):
        Letter1 = 'تسعة'
    C2 = int(c[10:11])
    #C2 = Val(Mid(c, 11, 1))
    if (C2 == 1):
        Letter2 = 'عشر'
    elif (C2 == 2):
        Letter2 = 'عشرون'
    elif (C2 == 3):
        Letter2 = 'ثلاثون'
    elif (C2 == 4):
        Letter2 = 'اربعون'
    elif (C2 == 5):
        Letter2 = 'خمسون'
    elif (C2 == 6):
        Letter2 = 'ستون'
    elif (C2 == 7):
        Letter2 = 'سبعون'
    elif (C2 == 8):
        Letter2 = 'ثمانون'
    elif (C2 == 9):
        Letter2 = 'تسعون'
    if Letter1 != '' and C2 > 1:
        Letter2 = Letter1 + ' و' + Letter2
    if Letter2 == '':
        Letter2 = Letter1
    if Letter2 == '':
        Letter2 = Letter1
    if C1 == 0 and C2 == 1:
        Letter2 = Letter2 + 'ة'
    if C1 == 1 and C2 == 1:
        Letter2 = 'احدى عشر'
    if C1 == 2 and C2 == 1:
        Letter2 = 'اثنى عشر'
    if C1 > 2 and C2 == 1:
        Letter2 = Letter1 + ' ' + Letter2
    #C3 = Val(Mid(c, 10, 1))
    C3 = int(c[9:10])
    if (C3 == 1):
        Letter3 = 'مائة'
    elif (C3 == 2):
        Letter3 = 'مئتان'
    elif (C3 == 3):
        Letter3 = 'ثلثمائة'
    elif (C3 == 4):
        Letter3 = 'ربعمائة'
    elif (C3 == 5):
        Letter3 = 'خمسمائة'
    elif (C3 == 6):
        Letter3 = 'ستمائة'
    elif (C3 == 7):
        Letter3 = 'سبعمائة'
    elif (C3 == 8):
        Letter3 = 'ثمنمائة'
    elif (C3 == 9):
        Letter3 = 'تسعمائة'
    elif (C3 > 2):
        #Letter3 = Left(DITAFQEET(C3) Len(DITAFQEET(C3)) - 1) + 'مائة'
        Letter3 = DITAFQEET(C3)[-len(DITAFQEET(C3)) - 1:] + 'مائة'
    if Letter3 != '' and Letter2 != '':
        Letter3 = Letter3 + ' و' + Letter2
    if Letter3 == '':
        Letter3 = Letter2

    C4 = int(c[6:9])
    if (C4 == 1):
        Letter4 = 'الف'
    elif (C4 == 2):
        Letter4 = 'الفان'
    elif (3 <= C4 <= 10):
        Letter4 = DITAFQEET(C4) + ' آلاف'
    elif (C4 > 10):
        Letter4 = DITAFQEET(C4) + ' الف'
    if Letter4 != '' and Letter3 != '':
        Letter4 = Letter4 + ' و' + Letter3
    if Letter4 == '':
        Letter4 = Letter3

    C5 = int(c[3:6])
    if (C5 == 1):
        Letter5 = 'مليون'
    elif (C5 == 2):
        Letter5 = 'مليونان'
    elif (3 <= C5 <= 10):
        Letter5 = DITAFQEET(C5) + ' ملايين'
    elif (C5 > 10):
        Letter5 = DITAFQEET(C5) + ' مليون'
    if Letter5 != '' and Letter4 != '':
        Letter5 = Letter5 + ' و' + Letter4
    if Letter5 == '':
        Letter5 = Letter4
    #C6 = Val(Mid(c, 1, 3))
    C6 = int(c[0:3])
    if (C6 == 1):
        Letter6 = 'مليار'
    elif (C6 == 2):
        Letter6 = 'ملياران'
    elif (C6 > 2):
        Letter6 = DITAFQEET(C6) + ' مليار'
    if Letter6 != '' and Letter5 != '':
        Letter6 = Letter6 + ' و' + Letter5
    if Letter6 == '':
        Letter6 = Letter5
    return Letter6
