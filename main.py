# coding=UTF-8
import collections
import re

import matplotlib.pyplot as plt
from evernote.api.client import EvernoteClient
from evernote.edam.notestore import NoteStore
from matplotlib import font_manager

# 设置字体（使得plt中能够显示中文）
from matplotlib import font_manager
a = sorted([f.name for f in font_manager.fontManager.ttflist])
for i in a:
    print(i)
plt.rcParams['font.sans-serif'] = ['Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

# 在这里输入开发者Token.
developer_token = "S=s58:U=12c3708:E=17780b91eaa:C=1775cac9818:P=1cd:A=en-devtoken:V=2:H=08d56c9a12edb7fefdeed42ec1ae0ea4"

# 初始化参数
sandbox = False
china = True

# 获取客户端
client = EvernoteClient(token=developer_token, sandbox=sandbox, china=china)

# 获取用户信息
user_store = client.get_user_store()

version_ok = user_store.checkVersion("Evernote EDAMTest (Python)", 1, 25)
print("Is my Evernote API version up to date? ", str(version_ok))
print("")
if not version_ok:
    exit(1)

note_store = client.get_note_store()

# 列出所有的笔记本
notebooks = note_store.listNotebooks()
print("Found ", len(notebooks), " notebooks:")
print()

for notebook in notebooks:
    print(notebook.name)
print()

# 根据GUID拿到笔记本
guid = 'c919a3d7-e1f6-4950-9755-7187e5e546e0'
notebook = note_store.getNotebook(guid)
print("现在拿到的是：" + notebook.name + "笔记本")
print()

# 展示/创建搜索条件
searches = note_store.listSearches()

# 根据笔记本guid获取笔记本中所有笔记
noteFilter = NoteStore.NoteFilter()
noteFilter.notebookGuid = guid
notesMetadataResultSpec = NoteStore.NotesMetadataResultSpec(True)
noteList = note_store.findNotesMetadata(noteFilter, 0, 100, notesMetadataResultSpec)


# 将笔记内容变成仅含有中文的字符串
def translate(str):
    line = str.strip()
    pattern = re.compile('[^\u4e00-\u9fa50-9]')
    # 只保留中文和数字
    zh = "".join(pattern.split(line)).strip()
    # 去除数字
    zh = re.sub('\d+', '', zh)
    # 去除多余字段
    outStr = zh.replace("每日日程安排周年月日开始时间微软雅黑时间微软雅黑周一微软雅黑周二微软雅黑周三微软雅黑周四微软雅黑周五微软雅黑周六微软雅黑周日微软雅黑微软雅黑", '').replace("微软雅黑",
                                                                                                              '').replace(
        "星期一星期二星期三星期四星期五星期六星期七", '')
    return outStr


# 将字符串转化为项目列表
def createWordsList(outStr):
    words = []
    outStr = translate(outStr)
    if ((len(outStr) % 4) != 0):
        print(len(outStr))
        print("数据格式有问题")
    else:
        for i in range(len(outStr)):
            if (i % 4 == 0):
                word = outStr[i:i + 4]
                words.append(word)

    print(collections.Counter(words))
    return words


# 统计整年时间花费
# words = []
# for i in range(0, len(noteList.notes)):
#     note = note_store.getNote(noteList.notes[i].guid, True, True, True, True)
#     temp = "" + note.title
#     if temp.__contains__("2020"):
#         words = words + createWordsList(note.content)
#
# counter = collections.Counter(words).get("欢度元旦")
# collections.Counter(words).items()
# print(collections.Counter(words))


# 输入笔记的标题来确定是哪一本笔记
title = '2021年第5周'
for note in noteList.notes:
    if note.title == title:
        requiredNote = note_store.getNote(note.guid, True, True, True, True)

# 统计本周的时间花费并作图
counter = dict(sorted(collections.Counter(createWordsList(requiredNote.content)).items(), key=lambda item: item[1]))
for key in counter.keys():
    counter[key] = counter[key] / 2
rects = plt.barh(range(len(list(counter.values()))), list(counter.values()), color=[
    'seagreen', 'chocolate', 'darkorange', 'lightcoral', 'lightsalmon'
])
index = [float(c) for c in range(len(list(counter.keys())))]
plt.xlim(xmax=max(counter.values()) * 1.3, xmin=0)
plt.yticks(index, list(counter.keys()))
plt.title(requiredNote.title + '时间使用情况')
plt.xlabel("花费时间（小时）")
for rect in rects:
    width = rect.get_width()
    plt.text(width, rect.get_y() + rect.get_height() / 2, str(width), ha='left', va='center')

# 解决图片保存不完整问题
plt.tight_layout()

# 图片写入文件
plt.savefig("/Users/anshaowei/Downloads/count.png", dpi=300, figsize=(6.4, 6))
exit(1)
