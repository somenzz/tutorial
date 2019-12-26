import sys

def func1():
    a = []
    # 两次引用，一次来自 a，一次来自 getrefcount
    print(sys.getrefcount(a))

    def func(a):
        # 四次引用，a，python 的函数调用栈，函数参数，和 getrefcount
        print(sys.getrefcount(a))
    func(a)
    # 两次引用，一次来自 a，一次来自 getrefcount，函数 func 调用已经不存在
    print(sys.getrefcount(a))


def fun2():
    import sys
    a = []
    print(sys.getrefcount(a)) # 两次
    b = a
    print(sys.getrefcount(a)) # 三次
    c = b
    d = b
    e = c
    f = e
    g = d
    print(sys.getrefcount(a)) # 八次


fun2()

