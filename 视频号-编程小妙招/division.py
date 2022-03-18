import sys
def fun(a,b):
    '''
    计算两个数的商
    '''
    print(f"{a = }")
    print(f"{b = }")
    val = a/b
    print(f"a/b = {val}")


if __name__ == "__main__":
    fun(int(sys.argv[1]),int(sys.argv[2]))
