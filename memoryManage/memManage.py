import os,sys
import psutil
import gc


# 显示当前 python 程序占用的内存大小
def show_memory_info(hint):
    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_info()
    memory = info.rss / 1024.0 / 1024
    print("{} 内存占用: {} MB".format(hint, memory))


def func():
    show_memory_info("func 调用前")
    a = [i for i in range(10000000)]
    show_memory_info("func 调用结束前")
    print(f"a 的引用计数 {sys.getrefcount(a)}")

def func2():
    '''
    循环引用测试
    :return:
    '''
    show_memory_info("func 调用前")
    a = [i for i in range(10000000)]
    b = [i for i in range(10000000)]
    a.append(b)
    b.append(a)
    show_memory_info("func 调用结束前")
    # print(f"a 的引用计数 {sys.getrefcount(a)}")



if __name__ == "__main__":
    func2()
    gc.collect()
    # print(f"a 的引用计数 {sys.getrefcount(a)}")
    show_memory_info("func 调用结束后")
