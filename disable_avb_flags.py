"""Prepare verification-disabled VBMeta for the EXACT documented retail source.
Offline only. Requires the phone's bootloader to remain unlocked if installed.
"""
import argparse, hashlib, struct
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('input',type=Path)
p.add_argument('output',type=Path)
a=p.parse_args()
if a.input.resolve()==a.output.resolve() or a.output.exists():
    raise SystemExit('Use a new output file; original metadata is preserved')
b=bytearray(a.input.read_bytes())
if hashlib.md5(b).hexdigest()!='35e96510fcd5052617a522b576ef6e17':
    raise SystemExit('Not the documented retail VBMeta source; stopped')
if b[:4]!=b'AVB0' or struct.unpack_from('>I',b,120)[0]!=0:
    raise SystemExit('Unexpected AVB header/flags')
struct.pack_into('>I',b,120,3)
if hashlib.sha256(b).hexdigest()!='607501655ea216ac4000fbb3284fb8312e92f05ab1caa3779a87b42c302c4791':
    raise SystemExit('Unexpected output hash')
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_bytes(b)
print('Prepared offline VBMeta flags=3. No phone changes. Signature is intentionally invalidated; unlocked state is required.')
