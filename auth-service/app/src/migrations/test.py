import os


o = os.path.dirname(__file__)
os.getcwd()
p = os.path.abspath(os.path.dirname(__file__))

print(o)
print(p)
print(os.path.join(p, 'env', '.env'))
