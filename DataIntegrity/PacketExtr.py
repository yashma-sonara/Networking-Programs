
    import sys
import re

def extract():
    while True:

     content = sys.stdin.buffer.read1(6)
     if not content: #detect EOF on stdin
         break
     else:
         size = ""
         while True:
             byte = sys.stdin.buffer.read1(1)
             byte1 = byte.decode()
             #If B, then size has ended
             if byte1 == "B":
                 break
             size += byte1
         size = int(size)
         while size > 0:
            data = sys.stdin.buffer.read1(size)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
            size -= len(data)


if __name__ == "__main__":
   extract()                                                                                                                                      
