import random


digits = random.choices('12345678',k=3)
letters = random.choices('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM',k=3)
symbols = random.choices('!@#$%^&*',k=2)
leight = digits + letters + symbols
random.shuffle(leight)
password = ''.join(leight)
print(password)