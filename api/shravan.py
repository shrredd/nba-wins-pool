from time import ctime, time

c0 = None
cc = 0.0
t0 = None

def SAY(*strings):
    with open('/tmp/shravan.out', 'a') as f:
        print >>f, ' '.join(str(s) for s in strings)

def REPR(*objs):
    SAY(*list(repr(obj) for obj in objs))

def TIMEIN():
    global t0
    t0 = time()

def TIMEOUT():
    dt = time() - t0
    SAY(ctime(), '-', dt)

def CIN():
    global c0
    c0 = time()
    return ''

def COUT():
    global cc, c0
    cc += time() - c0
    c0 = None
    return ''

def CSUM():
    global cc
    SAY(ctime(), '-', '{:.9f}'.format(cc))
    cc = 0.0
    return ''

__builtins__['CIN'] = CIN
__builtins__['COUT'] = COUT
__builtins__['CSUM'] = CSUM
__builtins__['SAY'] = SAY
__builtins__['REPR'] = REPR
__builtins__['TIMEIN'] = TIMEIN
__builtins__['TIMEOUT'] = TIMEOUT
