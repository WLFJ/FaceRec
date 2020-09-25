import threading

class MyThread(threading.Thread):
    def __init__(self, func, args = ()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
    
    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def add(num):
    result = num + 5
    return result

if __name__ == '__main__':
    data = []
    threads = []
    nums = [1, 2, 3]
    for num in nums:
        t = MyThread(add, args = (num, ))
        threads.append(t)
        t.start()
    for t in threads:
        # 这里在等待的时候 其他线程都在运行
        t.join()
        data.append(t.get_result())
    print(data)
    
