import sys
import os

print(f"Received: {sys.argv[0]}")
if os.path.exists("arg.txt"):
    os.remove('arg.txt')
with open('arg.txt', 'w') as f:
    f.write(f"Received: {sys.argv[1]}")