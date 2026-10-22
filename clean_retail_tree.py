"""Plan/remove identified carrier apps from EXTRACTED EROFS trees only.
Dry-run is default. This does not connect to a phone or flash anything.
"""
import argparse, json, re, shutil
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--tree',type=Path,required=True)
p.add_argument('--metadata-dir',type=Path,required=True)
p.add_argument('--out-config',type=Path,required=True)
p.add_argument('--execute',action='store_true')
args=p.parse_args()
root=args.tree.resolve()
if not root.is_dir(): raise SystemExit('Extracted tree directory is missing')
extra={
'priv-app/AttIqi','priv-app/IqiMotMetrics',
'app/TheScoop','overlay/MotoFrameworkResOverlayCKT.apk',
'overlay/MotoFrameworkResOverlayCKTDefault.apk'}
for stem in ['system_ext_a','product_a']:
    for suffix in ['fs_config','file_contexts']:
        if not (args.metadata_dir/(stem+'_'+suffix)).is_file():
            raise SystemExit('Missing original extraction metadata for '+stem)
report=[]
for stem,mount in [('system_ext_a','system_ext'),('product_a','product')]:
    base=(root/stem).resolve()
    if base.parent!=root or not base.is_dir(): raise SystemExit('Expected extracted partition tree: '+stem)
    selected=[]
    candidates=[]
    for target in base.rglob('*'):
        rel=target.relative_to(base).as_posix()
        if re.search(r'paks|cricket|att[.]iqi|iqimotmetrics|thescoop',rel,re.I) or rel in extra:
            candidates.append((rel,target))
    for rel,target in sorted(candidates,key=lambda pair:(pair[0].count('/'),pair[0])):
        if any(rel==prior or rel.startswith(prior+'/') for prior in selected):continue
        if not target.resolve().is_relative_to(base):raise SystemExit('Refusing path outside extracted tree')
        selected.append(rel)
    report.append({'partition':stem,'remove':selected})
    print(stem+': '+json.dumps(selected,indent=2))
    if not args.execute:continue
    for rel in selected:
        target=base/rel
        if target.is_dir():shutil.rmtree(target)
        else:target.unlink()
    args.out_config.mkdir(parents=True,exist_ok=True)
    for suffix in ['fs_config','file_contexts']:
        source=args.metadata_dir/(stem+'_'+suffix)
        text=source.read_text()
        text=text.replace('/'+stem,'/'+mount)
        if suffix=='fs_config':
            text=re.sub(r'^'+re.escape(stem)+r'(?=/| )',mount,text,flags=re.M)
        (args.out_config/(mount+'_'+suffix)).write_text(text,encoding='utf-8',newline='\n')
if args.execute:
    (args.out_config/'removal-plan.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Extracted copies changed; no phone operations.' if args.execute else 'DRY RUN: no files changed.')
