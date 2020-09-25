# FaceRec API 应用参考文档

## 初始化

首先导入包

```python
from FaceRec.FaceRec import FaceRec
from FaceRec.manager import manager
from FaceRec.FaceInfo import FaceInfo
```

```python
fr = FaceRec('学生管理对象', '人脸数据库', '认证服务器地址', '签到活动id')
```

在实际项目中只需要如此创建对象

```python
# 从文件中读出先前训练的面部数据
with open('facedb.db', 'rb') as f:
    face_database_all = pickle.loads(f.read())

act_id = 6

fr = FaceRec(manager(), face_database_all, '3.wlfj.fun:8000', act_id)
```

绑定识别成功与识别失败的事件(也就是说如果识别出人脸, 会自动调用你绑定的函数)

```python
# pinfo 为文本类型, 识别成功的学号
def callback_succ(pinfo, pname):
    print('识别成功', pinfo, pname)

fr.rec_out = callback_succ

# frame 为cv2捕捉的照片
def callback_faild(frame):
    print('识别失败')

fr.rec_fail = callback_faild
```

## 在人脸识别中嵌入API

在界面框架中找到具体负责摄像头捕捉图像的部分, 其工作过程类似如此:

1. 捕捉一张图像
2. 进行人脸识别, 并在上面框出人脸
3. 利用识别到的人脸信息做签到记录等操作

FaceRec里面已经实现了2.3., 所以你需要将这些代码删除, 替换为API调用.

```python
# frame是使用cv2捕捉的图像
fr.frame_come(frame, function)
```

你还需要传入function, 这是一个函数类型, 用于处理“在将面部框出来之后更新界面”的代码. 你需要将原来工程中“更新界面”的代码封装为函数, 并传入其中.(具体请看例子)

## 程序结束时

首先你需要绑定界面框架的关闭事件, 在其中调用

```python
db = fr.close_event()
```

将会得到经过识别后更新的面部数据库, 需要将其写入文件

```python
with open('facedb.db', 'wb') as f:
    s = pickle.dumps(db)
    f.write(s)
```
