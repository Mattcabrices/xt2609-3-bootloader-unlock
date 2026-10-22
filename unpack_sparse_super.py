"""Read-only sparsechunk/LP parser; extracts logical images for inspection only."""
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import struct

p = argparse.ArgumentParser()
p.add_argument('source', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--partitions', nargs='*', default=['system_ext_a'])
a = p.parse_args()
segments = []
total = None
for path in sorted(a.source.glob('super.img_sparsechunk.*'), key=lambda x:int(x.suffix[1:])):
    with path.open('rb') as f:
        magic, major, minor, fh, ch, block, blocks, chunks, checksum = struct.unpack('<I4H4I', f.read(28))
        assert magic == 0xed26ff3a and major == 1 and fh >= 28 and ch >= 12
        assert total is None or total == block * blocks
        total = block * blocks
        f.seek(fh)
        logical = 0
        for _ in range(chunks):
            header = f.read(ch)
            kind, reserved, nblock, size = struct.unpack_from('<2H2I', header)
            length = nblock * block
            offset = f.tell()
            if kind == 0xcac1:
                assert size == ch + length
                segments.append((logical, logical+length, str(path), offset, None))
            elif kind == 0xcac2:
                assert size == ch + 4
                segments.append((logical, logical+length, str(path), offset, f.read(4)))
            elif kind == 0xcac3:
                assert size == ch
            elif kind != 0xcac4:
                raise ValueError(hex(kind))
            f.seek(offset + size-ch)
            logical += length
        assert logical == total
segments.sort()
for x,y in zip(segments,segments[1:]):
    assert x[1] <= y[0], 'Overlapping sparse data'
starts = [s[0] for s in segments]
handles = {}
def read(offset, size):
    result = bytearray()
    while size:
        i = bisect.bisect_right(starts, offset)-1
        if i >= 0 and offset < segments[i][1]:
            start,end,path,physical,fill = segments[i]
            n = min(size,end-offset)
            if fill is not None:
                assert n % 4 == 0 and (offset-start) % 4 == 0
                data = fill*(n//4)
            else:
                if path not in handles:
                    handles[path] = open(path,'rb')
                f=handles[path]
                f.seek(physical+offset-start)
                data=f.read(n)
                assert len(data)==n
        else:
            end=starts[i+1] if i+1<len(starts) else total
            n=min(size,end-offset)
            data=bytes(n)
        assert n>0
        result.extend(data)
        size-=n
        offset+=n
    return bytes(result)

geometry=read(4096,4096)
assert struct.unpack_from('<I',geometry)[0]==0x616c4467
gsize=struct.unpack_from('<I',geometry,4)[0]
g=bytearray(geometry[:gsize]); expected=bytes(g[8:40]);g[8:40]=bytes(32)
assert hashlib.sha256(g).digest()==expected
header=read(12288,256)
magic,major,minor,hsize=struct.unpack_from('<I2HI',header)
assert magic==0x414c5030 and major==10 and hsize<=256
h=bytearray(header[:hsize]);expected=bytes(h[12:44]);h[12:44]=bytes(32)
assert hashlib.sha256(h).digest()==expected
tsize=struct.unpack_from('<I',header,44)[0]
tables=read(12288+hsize,tsize)
assert hashlib.sha256(tables).digest()==header[48:80]
po,pn,ps=struct.unpack_from('<3I',header,80)
eo,en,es=struct.unpack_from('<3I',header,92)
extents=[struct.unpack_from('<QIQI',tables,eo+i*es) for i in range(en)]
parts=[]
a.output.mkdir(parents=True,exist_ok=True)
for i in range(pn):
    name,attr,first,count,group=struct.unpack_from('<36s4I',tables,po+i*ps)
    name=name.rstrip(b'\0').decode('ascii')
    chosen=extents[first:first+count]
    size=sum(e[0]*512 for e in chosen)
    info={'name':name,'bytes':size,'extents':chosen,'attributes':attr,'group':group}
    if name in a.partitions and size:
        digest=hashlib.sha256()
        with (a.output/(name+'.img')).open('wb') as out:
            for sectors,kind,sector,source in chosen:
                assert source==0 and kind in (0,1)
                left=sectors*512;offset=sector*512
                while left:
                    n=min(left,4*1024*1024)
                    data=read(offset,n) if kind==0 else bytes(n)
                    out.write(data);digest.update(data)
                    left-=n;offset+=n
        info['sha256']=digest.hexdigest()
        print('Extracted',name,size,flush=True)
    parts.append(info)
(a.output/'logical-partitions.json').write_text(json.dumps({'super_bytes':total,'metadata_checksums':'PASS','partitions':parts},indent=2))
print(json.dumps(parts,indent=2),flush=True)
