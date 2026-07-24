import struct, os, collections
def check(path):
    with open(path,'rb') as f:
        f.read(80); n = struct.unpack('<I', f.read(4))[0]
        edges = collections.Counter()
        for _ in range(n):
            data = f.read(50)
            vs = []
            for k in range(3):
                v = struct.unpack('<3f', data[12+12*k:24+12*k])
                vs.append(tuple(round(x,4) for x in v))
            if len(set(vs)) < 3: continue
            for i in range(3):
                a, b = vs[i], vs[(i+1)%3]
                edges[(min(a,b),max(a,b))] += 1
    odd  = sum(1 for c in edges.values() if c % 2 == 1)   # true open boundary
    even = sum(1 for c in edges.values() if c % 2 == 0 and c != 2)  # coincident stacking
    return n, odd, even
rows=[]
for fn in sorted(os.listdir('stl_v13')):
    if fn.endswith('.stl'):
        rows.append((fn,)+check(os.path.join('stl_v13',fn)))
w=max(len(r[0]) for r in rows); openfails=0
for fn,n,odd,even in rows:
    s='OK' if odd==0 else f'** {odd} OPEN edges **'
    if odd: openfails+=1
    extra = f'({even} coincident, benign)' if even else ''
    print(f'{fn:<{w}} {s:<22} {extra}')
print(f'\n{openfails} parts with true open boundaries')
