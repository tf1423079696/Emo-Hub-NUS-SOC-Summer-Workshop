import pyautogui
import time
import xlrd
import pyperclip


def mouseClick(clickTimes, lOrR, img, reTry):
    if reTry == 1:
        while True:
            location = pyautogui.locateCenterOnScreen(img, confidence=0.9)
            if location is not None:
                pyautogui.click(location.x, location.y, clicks=clickTimes, interval=0.2, duration=0.2, button=lOrR)
                break
            print("未找到匹配图片,0.1秒后重试")
            time.sleep(0.1)
    elif reTry == -1:
        while True:
            location = pyautogui.locateCenterOnScreen(img, confidence=0.9)
            if location is not None:
                pyautogui.click(location.x, location.y, clicks=clickTimes, interval=0.2, duration=0.2, button=lOrR)
            time.sleep(0.1)
    elif reTry > 1:
        i = 1
        while i < reTry + 1:
            location = pyautogui.locateCenterOnScreen(img, confidence=0.9)
            if location is not None:
                pyautogui.click(location.x, location.y, clicks=clickTimes, interval=0.2, duration=0.2, button=lOrR)
                print("重复")
                i += 1
            time.sleep(0.1)


def mainWork(img):
    i = 1
    sheet1 = img
    while i < sheet1.nrows:
        # 取本行指令的操作类型
        cmdType = sheet1.row(i)[0]
        if cmdType.value == 1.0:
            # 取图片名称
            img = sheet1.row(i)[1].value
            reTry = 1
            if sheet1.row(i)[2].ctype == 2 and sheet1.row(i)[2].value != 0:
                reTry = sheet1.row(i)[2].value
            mouseClick(1, "left", img, reTry)
            print("单击左键", img)
        # 2代表双击左键
        elif cmdType.value == 2.0:
            # 取图片名称
            img = sheet1.row(i)[1].value
            # 取重试次数
            reTry = 1
            if sheet1.row(i)[2].ctype == 2 and sheet1.row(i)[2].value != 0:
                reTry = sheet1.row(i)[2].value
            mouseClick(2, "left", img, reTry)
            print("双击左键", img)
        # 3代表右键
        elif cmdType.value == 3.0:
            # 取图片名称
            img = sheet1.row(i)[1].value
            # 取重试次数
            reTry = 1
            if sheet1.row(i)[2].ctype == 2 and sheet1.row(i)[2].value != 0:
                reTry = sheet1.row(i)[2].value
            mouseClick(1, "right", img, reTry)
            print("右键", img)
            # 4代表输入
        elif cmdType.value == 4.0:
            inputValue = sheet1.row(i)[1].value
            pyperclip.copy(inputValue)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            print("输入:", inputValue)
            # 5代表等待
        elif cmdType.value == 5.0:
            # 取图片名称
            waitTime = sheet1.row(i)[1].value
            time.sleep(waitTime)
            print("等待", waitTime, "秒")
        # 6代表滚轮
        elif cmdType.value == 6.0:
            # 取图片名称
            scroll = sheet1.row(i)[1].value
            pyautogui.scroll(int(scroll))
            print("滚轮滑动", int(scroll), "距离")
        i += 1


def sendWeChat(label):
    if label == 'ANGRY':
        file = './sendwechat/angry.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)

    if label == 'DISGUST':
        file = './sendwechat/disgust.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)

    if label == 'FEAR':
        file = './sendwechat/fear.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)

    if label == 'HAPPY':
        file = './sendwechat/happy.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)

    if label == 'NEUTRAL':
        print('NEUTRAL')

    if label == 'SAD':
        file = './sendwechat/sad.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)

    if label == 'SURPRISED':
        file = './sendwechat/surprised.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)

    if label == 'NEUTRAL':
        file = './sendwechat/neutral.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)

    if label == 'WARNING':
        file = './sendwechat/warning.xls'
        # 打开文件
        wb = xlrd.open_workbook(filename=file)
        # 通过索引获取表格sheet页
        sheet1 = wb.sheet_by_index(0)
        mainWork(sheet1)
