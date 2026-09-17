import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/sahilss2/Desktop/ECE470Labs/Lab2/install/ece470labs'
