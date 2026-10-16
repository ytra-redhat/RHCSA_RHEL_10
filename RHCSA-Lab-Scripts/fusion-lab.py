#!/usr/bin/env python3
"""Owned, powered-off Fusion ARM64 exam VMs. No implicit teardown."""
import argparse
import fcntl
import getpass
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import uuid

APP = Path('/Applications/VMware Fusion.app/Contents/Library')
VMRUN = APP / 'vmrun'
VDISK = APP / 'vmware-vdiskmanager'
BASE = Path(__file__).resolve().parents[1]
OWNER = 'jconwell-fusion-2026-10-05'
NODES = {
 'alpha': (1, [10], '192.168.100.10', 'fd00::10'),
 'bravo': (1, [10, 5], '192.168.100.20', 'fd00::20'),
 'charlie': (2, [8, 6, 4], '10.20.30.11', 'fd42::11'),
 'delta': (2, [8], '10.20.30.12', 'fd42::12'),
 'echo': (3, [8, 6], '172.16.40.21', 'fd10::21'),
 'foxtrot': (3, [8], '172.16.40.22', 'fd10::22'),
}


def fail(message):
    raise RuntimeError(message)


def run(*args):
    argv=[str(x) for x in args]
    try:p=subprocess.run(argv,capture_output=True,text=True,timeout=1800)
    except subprocess.TimeoutExpired:fail('Fusion operation timed out; command/credential arguments withheld')
    if p.returncode:
        detail=p.stderr.strip() or p.stdout.strip() or 'Fusion command failed'
        for i,value in enumerate(argv[:-1]):
            if value in ('-gp','-vp') and argv[i+1]:detail=detail.replace(argv[i+1],'[redacted]')
        fail(detail)
    return p.stdout


def vr(*args):
    return run(VMRUN, '-T', 'fusion', *args)


def mac():
    return '00:50:56:' + ':'.join(f'{x:02x}' for x in (os.urandom(1)[0] % 64, *os.urandom(2)))


def load(path):
    entries = {}
    for line in path.read_text().splitlines():
        m = re.match(r'^\s*([^#\s=]+)\s*=\s*"(.*)"\s*$', line)
        if not m and line.strip() and not line.lstrip().startswith('#'):
            fail('Unsupported VMX line; preserved without editing: ' + line)
        if m:
            key = m[1].lower()
            if key in entries:
                fail('Duplicate VMX key: ' + key)
            entries[key] = m[2]
    return entries


def save(path, entries):
    if any('"' in str(v) or '\n' in str(v) for v in entries.values()):
        fail('Quotes or newlines in VMX values are unsupported')
    temp = path.with_suffix('.vmx.tmp')
    temp.write_text(''.join(f'{k} = "{v}"\n' for k, v in entries.items()))
    temp.replace(path)


def owned(root, node):
    path = root / f'rhel10-{node}.vmwarevm'
    state = path / 'fusion-state.json'
    if path.is_symlink() or state.is_symlink() or not state.is_file():
        fail('Not an owned VM bundle: ' + str(path))
    data = json.loads(state.read_text())
    if data.get('owner') != OWNER or data.get('node') != node or not re.fullmatch(r'[0-9a-f]{32}', data.get('id','')):
        fail('Ownership does not match')
    for field in ('mac0','mac1'):
        if not re.fullmatch(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}', data.get(field,'')):fail('Invalid manifest MAC')
    if data.get('schema')==2 and node in NODES and data.get('extra_sizes')!=NODES[node][1]:fail('Manifest disk layout does not match node')
    vmx = path / f'rhel10-{node}.vmx'
    if not vmx.is_file() or vmx.is_symlink():
        fail('Missing or unsafe VMX')
    return vmx, data


def off(vmx, require_unlocked=True):
    entries = load(vmx)
    if entries.get('checkpoint.vmstate'):
        fail('VM is suspended; shut it down normally first')
    running = vr('list').splitlines()[1:]
    if any(Path(x).resolve() == vmx.resolve() for x in running if x.strip()):
        fail('VM must be powered off: ' + str(vmx))
    if require_unlocked and list(vmx.parent.glob('*.lck')):
        fail('VM bundle has locks; close Fusion access before editing')


def disk(path, size):
    if path.exists():
        fail('Disk already exists: ' + str(path))
    run(VDISK, '-c', '-s', f'{size}GB', '-a', 'lsilogic', '-t', '0', path)


def iso_path(value):
    path = Path(value).expanduser().resolve()
    if not path.is_file() or path.suffix.lower() != '.iso':
        fail('Provide a local DVD ISO')
    if 'x86_64' in path.name.lower() or not any(x in path.name.lower() for x in ('aarch64', 'arm64')):
        fail('An ARM64/aarch64 ISO is required')
    if not any(x in path.name.lower() for x in ('dvd', 'dvd1')):
        fail('Use the full DVD ISO containing BaseOS and AppStream, not boot/minimal')
    return path


def network(entries, data):
    for key in list(entries):
        if key.startswith('ethernet'):
            del entries[key]
    for n, kind in enumerate(('nat', 'hostonly')):
        entries.update({f'ethernet{n}.present':'TRUE', f'ethernet{n}.connectionType':kind,
                        f'ethernet{n}.virtualDev':'vmxnet3', f'ethernet{n}.addressType':'static',
                        f'ethernet{n}.address':data[f'mac{n}'], f'ethernet{n}.startConnected':'TRUE'})


def mark(bundle, data):
    path = bundle / 'fusion-state.json'
    if path.is_symlink(): fail('Unsafe state symlink')
    temp=path.with_suffix('.json.tmp')
    with temp.open('w') as stream:
        stream.write(json.dumps(data, indent=2) + '\n')
        stream.flush(); os.fsync(stream.fileno())
    temp.chmod(0o600);temp.replace(path)


def template(root, iso):
    bundle = root / 'rhel10-golden.vmwarevm'
    if bundle.exists():
        state=bundle/'fusion-state.json'
        if bundle.is_symlink() or state.is_symlink() or not state.is_file():fail('Unknown golden bundle preserved')
        data=json.loads(state.read_text())
        if data.get('owner')!=OWNER or data.get('node')!='golden' or data.get('schema')!=2:fail('Legacy/unknown golden preserved; read BESTAANDE-VMS.md')
        if data.get('phase')=='ready':print('Golden already created; preserved');return
    else:
        bundle.mkdir(parents=True)
        data=dict(owner=OWNER,node='golden',schema=2,phase='hardware',mac0=mac(),mac1=mac(),id=uuid.uuid4().hex)
        mark(bundle,data)
    if (bundle/'rhel10-golden.vmx').exists():off(bundle/'rhel10-golden.vmx')
    if (bundle/'system.vmdk').exists():validate_vmdk(bundle/'system.vmdk',30)
    else:disk(bundle/'system.vmdk',30)
    entries = {'.encoding':'UTF-8', 'config.version':'8', 'virtualhw.version':'20',
      'displayname':'rhel10-golden — RHCSA Fusion', 'guestos':'arm-rhel9-64',
      'firmware':'efi', 'uefi.secureboot.enabled':'FALSE', 'memsize':'4096', 'numvcpus':'2',
      'pcibridge0.present':'TRUE', 'pcibridge4.present':'TRUE', 'pcibridge4.virtualdev':'pcieRootPort',
      'pcibridge4.functions':'8', 'nvme0.present':'TRUE', 'nvme0:0.present':'TRUE',
      'nvme0:0.filename':'system.vmdk', 'sata0.present':'TRUE', 'sata0:0.present':'TRUE',
      'sata0:0.devicetype':'cdrom-image', 'sata0:0.filename':str(iso),
      'sata0:0.startconnected':'TRUE', 'usb.present':'TRUE', 'usb_xhci.present':'TRUE',
      'sound.present':'FALSE', 'tools.synctime':'FALSE', 'bios.bootorder':'cdrom,hdd'}
    network(entries, data)
    save(bundle / 'rhel10-golden.vmx', entries)
    data['phase']='ready';mark(bundle,data)
    print('Golden VM created. Install via Fusion, run guest-golden.sh as root, shut down.')
    print(bundle / 'rhel10-golden.vmx')


def create(root, exam, iso):
    golden, gs = owned(root, 'golden')
    if gs.get('schema')!=2 or gs.get('phase')!='ready':fail('Use the v2 golden copy; read START-HIER.md')
    off(golden,require_unlocked=False)
    g = load(golden)
    if not g.get('guestos', '').startswith('arm-') or g.get('firmware') != 'efi':
        fail('Golden VM must be ARM with EFI')
    if len(validate_disks(golden,g)) != 1:fail('Golden must have exactly one disk across all controllers')
    if not g.get('nvme0:0.filename') or any(k.startswith('nvme0:') and k.endswith('.present') and k!='nvme0:0.present' and v.upper()=='TRUE' for k,v in g.items()):
        fail('Golden must contain only one NVMe system disk')
    nodes = [n for n,v in NODES.items() if v[0] == exam]
    # Preflight every destination before changing any node.
    for node in nodes:
        b=root/f'rhel10-{node}.vmwarevm'
        if b.exists():
            vmx,state=owned(root,node)
            if state.get('schema') != 2:
                fail('Legacy bundle preserved. Use the new v2 root; see BESTAANDE-VMS.md')
            if state.get('phase')!='ready':off(vmx)
    for node in nodes:
        bundle=root/f'rhel10-{node}.vmwarevm'
        vmx=bundle/f'rhel10-{node}.vmx'
        if bundle.exists():
            vmx,data=owned(root,node)
            if data.get('phase') == 'ready':
                print(node+': existing ready clone preserved; use status/start');continue
        else:
            # A failed clone without metadata is deliberately not auto-adopted.
            print(node+': cloning (may take several minutes)',flush=True)
            vr('clone',golden,vmx,'full','-cloneName=rhel10-'+node)
            data=dict(owner=OWNER,node=node,exam=exam,schema=2,phase='hardware',
                      mac0=mac(),mac1=mac(),id=uuid.uuid4().hex,golden_id=gs['id'],
                      seeded=False,extra_sizes=list(NODES[node][1]))
            mark(bundle,data)
        off(vmx)
        e=load(vmx)
        validate_disks(vmx,e)
        e.update(displayname='rhel10-'+node+' — RHCSA Fusion v2',memsize='4096',numvcpus='2',
                 **{'sata0.present':'TRUE','sata0:0.present':'TRUE','sata0:0.devicetype':'cdrom-image',
                    'sata0:0.filename':str(iso),'sata0:0.startconnected':'TRUE',
                    'bios.bootorder':'hdd,cdrom','tools.synctime':'FALSE'})
        network(e,data)
        for n,size in enumerate(data['extra_sizes'],1):
            name=f'extra-{n}-{size}G.vmdk'
            target=bundle/name
            if not target.exists():disk(target,size)
            else:validate_vmdk(target,size)
            e.update({f'nvme0:{n}.present':'TRUE',f'nvme0:{n}.filename':name})
        backup=vmx.with_suffix('.vmx.before-v2')
        if not backup.exists():backup.write_bytes(vmx.read_bytes())
        save(vmx,e)
        script=BASE/'guest-seeds'/f'{node}.sh'
        script.parent.mkdir(exist_ok=True)
        script.write_text(seed_text(node,data))
        data['phase']='ready';mark(bundle,data)
        print(node+': ready. Start, seed, shut down, snapshot.')


def validate_vmdk(path,size=None):
    if path.is_symlink():fail('Disk symlinks unsupported: '+str(path))
    # Disk manager validates its own descriptor/extent chain, without repair.
    run(VDISK,'-e',path)
    with path.open('rb') as stream:text=stream.read(65536).decode('utf-8',errors='replace')
    for relative in re.findall(r'(?:parentFileNameHint=|(?:RW \d+ \S+ ))\"([^\"]+)\"',text):
        if Path(relative).is_absolute() or (path.parent/relative).resolve().parent!=path.parent.resolve():fail('External VMDK chain reference refused')
    if size is not None:
        sectors=sum(int(x) for x in re.findall(r'^RW (\d+) ',text,re.M))
        if sectors != size*1024**3//512:
            fail('Existing extra disk has wrong capacity: '+str(path))


def validate_disks(vmx,entries):
    disks=[]
    for key,value in entries.items():
        if re.fullmatch(r'(nvme|scsi|sata|ide)\d+:\d+\.filename',key) and value.lower().endswith('.vmdk'):
            target=vmx.parent/value
            if Path(value).is_absolute() or target.resolve().parent != vmx.parent.resolve():
                fail('External disk reference refused: '+value)
            if not target.is_file():fail('Missing disk: '+value)
            validate_vmdk(target);disks.append(key)
    if not disks:fail('No system disk found')
    return disks


def seed_text(node, data):
    header = f'''#!/bin/bash
set -euo pipefail
[ "$(id -u)" = 0 ] || {{ echo 'Run as root inside the correct clone'; exit 1; }}
[ "$(cat /etc/rhcsa-fusion-golden 2>/dev/null)" = jconwell-fusion-golden-v2 ] || {{ echo 'Golden bootstrap missing'; exit 1; }}
[ "$(uname -m)" = aarch64 ] || exit 1
if [ -f /etc/rhcsa-fusion-seeded ]; then
 [ "$(cat /etc/rhcsa-fusion-seeded)" = '{data['id']}' ] || exit 1
 vmtoolsd --cmd 'info-set guestinfo.rhcsa_seed {data['id']}'
 echo 'Completion marker republished; no guest changes'; exit 0
fi
NAT_MAC='{data['mac0']}'
LAB_MAC='{data['mac1']}'
NODE='{node}'
EXPECTED_DISKS={1+len(data.get("extra_sizes",NODES[node][1]))}
EXPECTED_SIZES=({" ".join(str(x*1024**3) for x in data.get("extra_sizes",NODES[node][1]))})
# Verify identity by both VM-specific MAC addresses before any guest change.
NAT_IF=''; LAB_IF=''
[ -z "${{SSH_CONNECTION:-}}" ] || {{ echo 'Use the Fusion console; networking changes disconnect SSH'; exit 1; }}
for tool in nmcli openssl wipefs vmtoolsd ssh-keygen; do
 command -v "$tool" >/dev/null || {{ echo "Missing tool: $tool"; exit 1; }}
done
PROGRESS=/var/lib/rhcsa-fusion
mkdir -p "$PROGRESS"
trap 'echo "Seed failed at line $LINENO; inspect console and progress before retry" >&2' ERR

for path in /sys/class/net/*; do
  address=$(cat "$path/address")
  [ "$address" != "$NAT_MAC" ] || NAT_IF=${{path##*/}}
  [ "$address" != "$LAB_MAC" ] || LAB_IF=${{path##*/}}
done
[ -n "$NAT_IF" ] && [ -n "$LAB_IF" ] || {{ echo 'Wrong VM MACs'; exit 1; }}
[ "$(lsblk -dnr -o NAME,TYPE | awk '$2=="disk" && $1 !~ /^zram[0-9]+$/ {{n++}} END {{print n+0}}')" = "$EXPECTED_DISKS" ] || {{ echo 'Unexpected disk count'; exit 1; }}
ROOT_DISK=$(lsblk -srnp -o NAME,TYPE "$(findmnt -n -o SOURCE /)" | awk '$2=="disk" {{print $1}}')
[ "$ROOT_DISK" = /dev/nvme0n1 ] || {{ echo 'Root disk is not nvme0n1; inspect before continuing'; exit 1; }}
for i in "${{!EXPECTED_SIZES[@]}}"; do
 device=/dev/nvme0n$((i+2))
 [ "$(blockdev --getsize64 "$device")" = "${{EXPECTED_SIZES[$i]}}" ] || {{ echo "Unexpected capacity: $device"; exit 1; }}
done
for path in /sys/block/nvme0n*; do
  [ "${{path##*/}}" != nvme0n1 ] || continue
  [ -z "$(ls "$path" | grep -E 'p[0-9]+$' || true)" ] || {{ echo 'Extra disk already partitioned'; exit 1; }}
  [ -z "$(wipefs -n --noheadings /dev/${{path##*/}})" ] || {{ echo 'Extra disk has signatures'; exit 1; }}
done
[ -s /var/lib/rhcsa-fusion/golden-hostkey-fingerprint ] || {{ echo 'Hostkey seal record missing'; exit 1; }}
[ -s /var/lib/rhcsa-fusion/golden-machine-id ] || {{ echo 'Seal record missing; stop'; exit 1; }}
[ "$(cat /etc/machine-id)" != "$(cat /var/lib/rhcsa-fusion/golden-machine-id)" ] || {{ echo 'Golden was not sealed; identity reused'; exit 1; }}
[ -s /etc/machine-id ] || {{ echo 'First boot identity missing'; exit 1; }}
if [ ! -f "$PROGRESS/network.done" ]; then
ssh-keygen -A
[ "$(ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub | awk '{{print $2}}')" != "$(cat /var/lib/rhcsa-fusion/golden-hostkey-fingerprint)" ] || {{ echo 'SSH host key reused; stop'; exit 1; }}
systemctl restart sshd
hostnamectl set-hostname rhel10-$NODE
# Remove only the template-created profiles; do not overwrite all NM config.
for name in fusion-nat fusion-lab; do
 nmcli con delete "$name" >/dev/null 2>&1 || true
done
nmcli con add type ethernet ifname '*' con-name fusion-nat \\
  802-3-ethernet.mac-address "$NAT_MAC" ipv4.method auto ipv6.method auto connection.autoconnect yes
nmcli con add type ethernet ifname '*' con-name fusion-lab \\
  802-3-ethernet.mac-address "$LAB_MAC" ipv4.method disabled ipv6.method disabled connection.autoconnect yes
nmcli con mod fusion-lab connection.zone public
nmcli con up fusion-nat
nmcli con up fusion-lab
systemctl set-default multi-user.target
systemctl enable --now firewalld
touch "$PROGRESS/network.done"
fi
if [ ! -f "$PROGRESS/fixtures.done" ]; then
'''
    if node == 'bravo':
        header += 'systemctl set-default graphical.target\n'
    if node == 'alpha':
        header += """touch /var/tmp/badperms; chmod 777 /var/tmp/badperms
python3 - <<'GRUBPY'
from pathlib import Path
import re
p=Path('/etc/default/grub');text=p.read_text()
text=re.sub(r'^GRUB_TIMEOUT=.*$', 'GRUB_TIMEOUT=3', text, flags=re.M)
text=re.sub(r'^GRUB_TIMEOUT_STYLE=.*$', 'GRUB_TIMEOUT_STYLE=menu', text, flags=re.M)
def args(m):return 'GRUB_CMDLINE_LINUX="'+' '.join(x for x in m[1].split() if x!='quiet')+'"'
text=re.sub(r'^GRUB_CMDLINE_LINUX="(.*)"$',args,text,flags=re.M)
p.write_text(text)
GRUBPY
grub2-mkconfig -o /boot/grub2/grub.cfg --update-bls-cmdline
"""
    if node == 'charlie':
        header += '''mkdir -p /opt/finance/{reports,bin,private}
printf '#!/bin/bash\\necho finance\\n' > /opt/finance/bin/run_report.sh
chmod 000 /opt/finance
'''
    if node == 'echo':
        header += '''dnf install -y httpd policycoreutils-python-utils
mkdir -p /srv/intranet
printf '%s\\n' 'Echo Intranet OK' > /srv/intranet/index.html
cat > /etc/systemd/system/labdata.service <<'UNIT'
[Unit]
Description=Lab Data Collector
After=network.target
[Service]
Type=simple
ExecStart=/usr/local/sbin/labdata-collect --daemon
Restart=on-failure
[Install]
WantedBy=multi-user.target
UNIT
cat > /etc/httpd/conf.d/intranet.conf <<'CONF'
Listen 8404
<VirtualHost *:8404>
DocumentRoot /srv/intranet
<Directory /srv/intranet>
Require all granted
</Directory>
</VirtualHost>
CONF
# Refuse a template that already grants the desired port/path labels.
if semanage port -l | grep '^http_port_t ' | grep -qw 8404; then
 echo 'Port 8404 already allowed; use a pristine golden'; exit 1
fi
chcon -R -t default_t /srv/intranet
systemctl daemon-reload
systemctl enable labdata.service httpd
firewall-cmd --zone=public --permanent --add-port=8404/tcp
firewall-cmd --reload
'''
    if node == 'delta':
        header += 'systemctl set-default rescue.target\n'
    if node == 'foxtrot':
        header += '''mkdir -p /mnt/archive
grep -q 'fusion-exam3-seed' /etc/fstab || printf '%s\\n' 'UUID=deadbeef-0000-0000-0000-000000000000 /mnt/archive xfs defaults 0 0 # fusion-exam3-seed' >> /etc/fstab
'''
    header += 'touch "$PROGRESS/fixtures.done"\nfi\n'
    if node in {'bravo','charlie','foxtrot'}:
        header += "printf 'root:%s\\n' \"$(openssl rand -base64 32)\" | chpasswd\n"
    header += f"printf '%s\\n' '{data['id']}' > /etc/rhcsa-fusion-seeded.tmp\nmv /etc/rhcsa-fusion-seeded.tmp /etc/rhcsa-fusion-seeded\n"
    header += f"vmtoolsd --cmd 'info-set guestinfo.rhcsa_seed {data['id']}'\n"
    return header + "sync\necho 'Seed complete. Shut down; create the exam-ready snapshot before rebooting.'\n"


def seed(root, node):
    vmx,data=owned(root,node)
    if data.get('schema')!=2:fail('Do not reseed legacy guests; read BESTAANDE-VMS.md')
    if data.get('seeded'):
        fail('Already seeded; reset the VM rather than reseeding')
    if vmx.resolve() not in [Path(x).resolve() for x in vr('list').splitlines()[1:] if x.strip()]:
        fail('Start this clone first')
    try:marker=vr('readVariable',vmx,'runtimeConfig','guestinfo.rhcsa_seed').strip()
    except RuntimeError:marker='' # Variable is absent before the first successful seed.
    if marker==data['id']:
        data['seeded']=True;mark(vmx.parent,data);print('Guest completion reconciled');return
    script=BASE/'guest-seeds'/f'{node}.sh'
    if not script.is_file():
        fail('Create-generated seed script missing')
    password=getpass.getpass('Root password inherited from golden (not saved): ')
    if not password:
        fail('Empty password refused')
    guest='/root/fusion-seed-'+data['id']+'.sh'
    auth=('-gu','root','-gp',password)
    vr(*auth,'copyFileFromHostToGuest',vmx,script,guest)
    vr(*auth,'runProgramInGuest',vmx,'/bin/bash',guest)
    if vr('readVariable',vmx,'runtimeConfig','guestinfo.rhcsa_seed').strip()!=data['id']:
        fail('Guest completion marker missing; inspect console before retrying')
    data['seeded']=True
    mark(vmx.parent,data)
    print('Seed completed. Shut down this VM normally before taking exam-ready snapshot.')


def import_golden(root,source):
    source=source.expanduser().resolve()
    if not source.is_file() or source.suffix!='.vmx':fail('Select an existing golden .vmx')
    off(source,require_unlocked=False)
    entries=load(source)
    if len(validate_disks(source,entries))!=1 or not entries.get('guestos','').startswith('arm-'):
        fail('Source golden must have exactly one disk and be ARM')
    bundle=root/'rhel10-golden.vmwarevm'
    vmx=bundle/'rhel10-golden.vmx'
    if bundle.exists():
        vmx,data=owned(root,'golden')
        if data.get('schema')!=2 or data.get('phase')!='import-config':fail('Destination golden exists; preserved')
        off(vmx)
    else:
        root.mkdir(parents=True,exist_ok=True)
        print('Copying golden as a full independent clone; source retained',flush=True)
        vr('clone',source,vmx,'full','-cloneName=rhel10-golden-v2')
        data=dict(owner=OWNER,node='golden',schema=2,phase='import-config',mac0=mac(),mac1=mac(),id=uuid.uuid4().hex)
        mark(bundle,data)
    entries=load(vmx);validate_disks(vmx,entries);network(entries,data)
    entries['tools.synctime']='FALSE';entries['displayname']='rhel10-golden — RHCSA Fusion v2'
    backup=vmx.with_suffix('.vmx.before-v2')
    if not backup.exists():backup.write_bytes(vmx.read_bytes())
    save(vmx,entries)
    data['phase']='ready';mark(bundle,data)
    print('Copy created. Boot this new golden, run v2 bootstrap, then seal. '+str(vmx))


def status(root,exam=None):
    running={Path(x).resolve() for x in vr('list').splitlines()[1:] if x.strip()}
    for node in ['golden',*NODES]:
        if exam and node!='golden' and NODES[node][0]!=exam:continue
        b=root/f'rhel10-{node}.vmwarevm'
        if not b.exists():print(node+': not created');continue
        try:
            vmx,data=owned(root,node);e=load(vmx)
            state='running' if vmx.resolve() in running else ('suspended' if e.get('checkpoint.vmstate') else 'powered off')
            snaps=vr('listSnapshots',vmx).splitlines()[1:]
            print(f"{node}: {state}; schema={data.get('schema','legacy')}; phase={data.get('phase','legacy')}; seeded={data.get('seeded',False)}; snapshots={snaps}")
            if vmx.resolve() in running:
                try:print('  guest marker: '+vr('readVariable',vmx,'runtimeConfig','guestinfo.rhcsa_seed').strip())
                except RuntimeError:print('  guest marker unavailable')
            print('  next: '+('see BESTAANDE-VMS.md' if data.get('schema')!=2 else ('prepare/seal golden' if node=='golden' else ('snapshot when powered off' if data.get('seeded') and not snaps else ('start exam or explicit reset' if snaps else 'start and seed')))))
        except (RuntimeError,OSError,ValueError) as error:print(node+': ERROR '+str(error))


def acquire_operation_lock(root):
    root.mkdir(parents=True,exist_ok=True)
    path=root/'.fusion-v2-operation.lock'
    if path.is_symlink():fail('Unsafe operation-lock symlink')
    handle=path.open('a');path.chmod(0o600)
    try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except OSError:handle.close();fail('Another v2 operation is using this VM root; wait for it to finish')
    return handle


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path.home()/'RHCSA-Fusion-v2')
    sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('plan');a.add_argument('--exam',type=int,choices=[1,2,3],default=1)
    a=sub.add_parser('template');a.add_argument('--iso',required=True)
    a=sub.add_parser('create');a.add_argument('--exam',type=int,choices=[1,2,3],required=True);a.add_argument('--iso',required=True)
    for name in ('start','seed','snapshot','reset','add-disk'):
        a=sub.add_parser(name);a.add_argument('--node',required=True,choices=list(NODES))
        if name=='add-disk':a.add_argument('--size',type=int,choices=range(1,65),required=True)
    a=sub.add_parser('status');a.add_argument('--exam',type=int,choices=[1,2,3])
    a=sub.add_parser('import-golden');a.add_argument('--source',type=Path,required=True)
    a=sub.add_parser('open-golden')
    argv=sys.argv[1:]
    if '--root' in argv:
        i=argv.index('--root')
        if i+1<len(argv):argv=argv[i:i+2]+argv[:i]+argv[i+2:]
    args=p.parse_args(argv);root=args.root.expanduser().resolve()
    if args.action=='plan':
        print(json.dumps({n:dict(exam=v[0],extra_GiB=v[1],ipv4=v[2],ipv6=v[3],
              system='/dev/nvme0n1',extra=[f'/dev/nvme0n{i+2}' for i in range(len(v[1]))])
              for n,v in NODES.items() if v[0]==args.exam},indent=2));return
    if platform.system()!='Darwin' or platform.machine() not in ('arm64','aarch64'):
        fail('This build requires macOS on Apple Silicon')
    if not VMRUN.is_file() or not VDISK.is_file():
        fail('Install VMware Fusion in /Applications')
    operation_lock=None if args.action in ('status','plan') else acquire_operation_lock(root)
    try:
        if args.action=='import-golden':
            import_golden(root,args.source);return
        if args.action=='status':
            status(root,args.exam);return
        if args.action in ('template','create'):
            iso=iso_path(args.iso)
            if args.action=='template':template(root,iso)
            else:create(root,args.exam,iso)
        elif args.action=='open-golden':
            vmx,_=owned(root,'golden');vr('start',vmx,'gui')
        elif args.action=='seed':seed(root,args.node)
        else:
            vmx,data=owned(root,args.node)
            if args.action=='start':
                if data.get('schema')!=2:fail('Legacy bundle preserved; use Fusion directly')
                vr('start',vmx,'gui');return
            # Fusion handles locks during snapshot/reset; direct edits require no locks.
            off(vmx, require_unlocked=args.action not in ('snapshot','reset'))
            if data.get('schema')!=2:fail('Legacy baseline preserved; no v2 reset/snapshot. Read BESTAANDE-VMS.md')
            if args.action=='snapshot':
                if not data.get('seeded'):fail('Seed this VM before the ready snapshot')
                if 'exam-ready-v2' in vr('listSnapshots',vmx).splitlines()[1:]:fail('Snapshot already exists; preserved')
                vr('snapshot',vmx,'exam-ready-v2');data['snapshot']='exam-ready-v2';mark(vmx.parent,data)
            elif args.action=='reset':
                if data.get('snapshot')!='exam-ready-v2':fail('No tracked exam-ready snapshot')
                if 'exam-ready-v2' not in vr('listSnapshots',vmx).splitlines()[1:]:fail('Tracked snapshot missing')
                vr('revertToSnapshot',vmx,'exam-ready-v2')
                print('Reverted. Use start to begin the exam again.')
            else:
                fail('v2 uses the prescribed disk layout; do not add arbitrary disks. See plan.')
    finally:
        if operation_lock is not None:operation_lock.close()


if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,ValueError,subprocess.TimeoutExpired) as exc:
        print('STOPPED: '+str(exc),file=sys.stderr);sys.exit(1)
