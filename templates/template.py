import sys
import io
import time

_INPUT = '''\


'''
sys.stdin = io.StringIO(_INPUT)

start = time.time()

n = int(input())
a, b = map(int, input().split())
s = input()
li = [list(map(int, input().split())) for _ in range(n)]


stop = time.time()
print(f'time: {stop - start} sec')
