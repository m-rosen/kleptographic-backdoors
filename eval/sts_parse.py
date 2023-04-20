'''
    Written by Miriam Rosén in 2023
'''
from collections import namedtuple

TestResult = namedtuple("TestResult", "name proportion p data result")

def sts_parse(file_name):
    f = open(file_name, 'r')
    for i in range(0, 7): # Skip first 7 lines
        next(f)    
    res = []
    for line in f:
        if line == '\n':
            break
        tokens = line.split()
        data = [int(n) for n in tokens[0:10]]
        p = float(tokens[10])
        prop_i = 11
        result = ''
        if tokens[prop_i] == '*': # p-value fail
            result += '* p-value'
            prop_i +=1
        prop = [int(i) for i in tokens[prop_i].split('/')]
        name_i = prop_i + 1
        if tokens[name_i] == '*': # proportion fail
            result += ' * proportion'
            name_i += 1
        name = tokens[name_i]
        res.append(TestResult(name, prop, p, data, result))
    f.close()
    return res