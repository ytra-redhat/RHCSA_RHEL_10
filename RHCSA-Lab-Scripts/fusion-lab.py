#!/usr/bin/env python3
"""Owned, powered-off Fusion ARM64 exam VMs. No implicit teardown."""
import argparse
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
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if p.returncode:
        # Never print argv: guest authentication may include a password.
        fail(p.stderr.strip() or p.stdout.strip() or 'Fusion command failed')
    return p.stdout


def vr(*args):
    return run(VMRUN, '-T', 'fusion', *args)


def mac():
    return '00:50:56:' + ':'.join(f'{x:02x}' for x in (os.urandom(1)[0] % 64, *os.urandom(2)))


def load(path):
    entries = {}
    for line in path.read_text().splitlines():
        m = re.match(r'^\s*([^#\s=]+)\s*=\s*"(.*)"\s*$', line)
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
    if path.is_symlink() or not state.is_file():
        fail('Not an owned VM bundle: ' + str(path))
    data = json.loads(state.read_text())
    if data.get('owner') != OWNER or data.get('node') != node:
        fail('Ownership does not match')
    vmx = path / f'rhel10-{node}.vmx'
    if not vmx.is_file() or vmx.is_symlink():
        fail('Missing or unsafe VMX')
    return vmx, data


def off(vmx):
    entries = load(vmx)
    if entries.get('checkpoint.vmstate'):
        fail('VM is suspended; shut it down normally first')
    running = vr('list').splitlines()[1:]
    if any(Path(x).resolve() == vmx.resolve() for x in running if x.strip()):
        fail('VM must be powered off: ' + str(vmx))
    if list(vmx.parent.glob('*.lck')):
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
    path.write_text(json.dumps(data, indent=2) + '\n')
    path.chmod(0o600)


def template(root, iso):
    bundle = root / 'rhel10-golden.vmwarevm'
    if bundle.exists():
        fail('Golden bundle already exists; preserved')
    bundle.mkdir(parents=True)
    data = dict(owner=OWNER, node='golden', mac0=mac(), mac1=mac(), id=uuid.uuid4().hex)
    mark(bundle, data)
    disk(bundle / 'system.vmdk', 30)
    entries = {'.encoding':'UTF-8', 'config.version':'8', 'virtualhw.version':'20',
      'displayname':'rhel10-golden — RHCSA Fusion', 'guestos':'arm-rhel9-64',
      'firmware':'efi', 'uefi.secureboot.enabled':'FALSE', 'memsize':'4096', 'numvcpus':'2',
      'pcibridge0.present':'TRUE', 'pcibridge4.present':'TRUE', 'pcibridge4.virtualdev':'pcieRootPort',
      'pcibridge4.functions':'8', 'nvme0.present':'TRUE', 'nvme0:0.present':'TRUE',
      'nvme0:0.filename':'system.vmdk', 'sata0.present':'TRUE', 'sata0:0.present':'TRUE',
      'sata0:0.devicetype':'cdrom-image', 'sata0:0.filename':str(iso),
      'sata0:0.startconnected':'TRUE', 'usb.present':'TRUE', 'usb_xhci.present':'TRUE',
      'sound.present':'FALSE', 'tools.synctime':'TRUE', 'bios.bootorder':'cdrom,hdd'}
    network(entries, data)
    save(bundle / 'rhel10-golden.vmx', entries)
    print('Golden VM created. Install via Fusion, run guest-golden.sh as root, shut down.')
    print(bundle / 'rhel10-golden.vmx')


def create(root, exam, iso):
    golden, gs = owned(root, 'golden')
    off(golden)
    g = load(golden)
    if not g.get('guestos', '').startswith('arm-') or g.get('firmware') != 'efi':
        fail('Golden VM must be ARM with EFI')
    if not g.get('nvme0:0.filename') or any(k.startswith('nvme0:') and k.endswith('.present') and k!='nvme0:0.present' and v.upper()=='TRUE' for k,v in g.items()):
        fail('Golden must contain only one NVMe system disk')
    nodes = [n for n,v in NODES.items() if v[0] == exam]
    for node in nodes:
        if (root / f'rhel10-{node}.vmwarevm').exists():
            fail('Existing bundle preserved; use reset after creating exam-ready snapshots')
    for node in nodes:
        bundle = root / f'rhel10-{node}.vmwarevm'
        vmx = bundle / f'rhel10-{node}.vmx'
        # Do not create destination before vmrun clone: it creates the bundle.
        vr('clone', golden, vmx, 'full', '-cloneName=rhel10-' + node)
        data = dict(owner=OWNER, node=node, exam=exam, mac0=mac(), mac1=mac(), id=uuid.uuid4().hex,
                    golden_id=gs['id'], seeded=False, extra_sizes=NODES[node][1])
        mark(bundle, data)
        off(vmx)
        e = load(vmx)
        e.update(displayname='rhel10-' + node + ' — RHCSA Fusion', memsize='4096', numvcpus='2',
                 **{'sata0.present':'TRUE', 'sata0:0.present':'TRUE', 'sata0:0.devicetype':'cdrom-image',
                    'sata0:0.filename':str(iso), 'sata0:0.startconnected':'TRUE', 'bios.bootorder':'hdd,cdrom'})
        network(e, data)
        for n,size in enumerate(NODES[node][1],1):
            name = f'extra-{n}-{size}G.vmdk'
            disk(bundle / name,size)
            e.update({f'nvme0:{n}.present':'TRUE',f'nvme0:{n}.filename':name})
        save(vmx,e)
        script = BASE / 'guest-seeds' / f'{node}.sh'
        script.parent.mkdir(exist_ok=True)
        script.write_text(seed_text(node, data))
        print(node + ': created full clone; start, seed, then snapshot exam-ready')


def seed_text(node, data):
    header = f'''#!/bin/bash
set -euo pipefail
[ "$(id -u)" = 0 ] || {{ echo 'Run as root inside the correct clone'; exit 1; }}
[ -f /etc/rhcsa-fusion-golden ] || {{ echo 'Golden bootstrap missing'; exit 1; }}
[ "$(uname -m)" = aarch64 ] || exit 1
[ ! -f /etc/rhcsa-fusion-seeded ] || {{ echo 'Already seeded; refusing to seed completed work'; exit 1; }}
NAT_MAC='{data['mac0']}'
LAB_MAC='{data['mac1']}'
NODE='{node}'
EXPECTED_DISKS={1+len(data.get("extra_sizes",NODES[node][1]))}
# Verify identity by both VM-specific MAC addresses before any guest change.
NAT_IF=''; LAB_IF=''
for path in /sys/class/net/*; do
  address=$(cat "$path/address")
  [ "$address" != "$NAT_MAC" ] || NAT_IF=${{path##*/}}
  [ "$address" != "$LAB_MAC" ] || LAB_IF=${{path##*/}}
done
[ -n "$NAT_IF" ] && [ -n "$LAB_IF" ] || {{ echo 'Wrong VM MACs'; exit 1; }}
[ "$(lsblk -dn -o TYPE | grep -cx disk)" = "$EXPECTED_DISKS" ] || {{ echo 'Unexpected disk count'; exit 1; }}
ROOT_DISK=$(lsblk -srnp -o NAME,TYPE "$(findmnt -n -o SOURCE /)" | awk '$2=="disk" {{print $1}}')
[ "$ROOT_DISK" = /dev/nvme0n1 ] || {{ echo 'Root disk is not nvme0n1; inspect before continuing'; exit 1; }}
for path in /sys/block/nvme0n*; do
  [ "${{path##*/}}" != nvme0n1 ] || continue
  [ -z "$(ls "$path" | grep -E 'p[0-9]+$' || true)" ] || {{ echo 'Extra disk already partitioned'; exit 1; }}
  [ -z "$(wipefs -n --noheadings /dev/${{path##*/}})" ] || {{ echo 'Extra disk has signatures'; exit 1; }}
done
rm -f /etc/machine-id\nrm -f /var/lib/dbus/machine-id\nsystemd-machine-id-setup\nrm -f /etc/ssh/ssh_host_*key /etc/ssh/ssh_host_*key.pub\nssh-keygen -A\nsystemctl restart sshd\nhostnamectl set-hostname rhel10-$NODE
# Remove only the template-created profiles; do not overwrite all NM config.
for name in fusion-nat fusion-lab; do
 nmcli con delete "$name"
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
printf '%s\\n' 'UUID=deadbeef-0000-0000-0000-000000000000 /mnt/archive xfs defaults 0 0 # fusion-exam3-seed' >> /etc/fstab
'''
    header += f"printf '%s\\n' '{data['id']}' > /etc/rhcsa-fusion-seeded\n"
    if node in {'bravo','charlie','foxtrot'}:
        header += "printf 'root:%s\\n' \"$(openssl rand -base64 32)\" | chpasswd\n"
    header += f"vmtoolsd --cmd 'info-set guestinfo.rhcsa_seed {data['id']}'\n"
    return header + "sync\necho 'Seed complete. Shut down; create the exam-ready snapshot before rebooting.'\n"


def seed(root, node):
    vmx,data=owned(root,node)
    if data.get('seeded'):
        fail('Already seeded; reset the VM rather than reseeding')
    if vmx.resolve() not in [Path(x).resolve() for x in vr('list').splitlines()[1:] if x.strip()]:
        fail('Start this clone first')
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


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path.home()/'RHCSA-Fusion-jconwell')
    sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('plan');a.add_argument('--exam',type=int,choices=[1,2,3],default=1)
    a=sub.add_parser('template');a.add_argument('--iso',required=True)
    a=sub.add_parser('create');a.add_argument('--exam',type=int,choices=[1,2,3],required=True);a.add_argument('--iso',required=True)
    for name in ('start','seed','snapshot','reset','add-disk'):
        a=sub.add_parser(name);a.add_argument('--node',required=True,choices=list(NODES))
        if name=='add-disk':a.add_argument('--size',type=int,choices=range(1,65),required=True)
    a=sub.add_parser('open-golden')
    args=p.parse_args();root=args.root.expanduser().resolve()
    if args.action=='plan':
        print(json.dumps({n:dict(exam=v[0],extra_GiB=v[1],ipv4=v[2],ipv6=v[3],
              system='/dev/nvme0n1',extra=[f'/dev/nvme0n{i+2}' for i in range(len(v[1]))])
              for n,v in NODES.items() if v[0]==args.exam},indent=2));return
    if platform.system()!='Darwin' or platform.machine() not in ('arm64','aarch64'):
        fail('This build requires macOS on Apple Silicon')
    if not VMRUN.is_file() or not VDISK.is_file():
        fail('Install VMware Fusion in /Applications')
    if args.action in ('template','create'):
        iso=iso_path(args.iso)
        if args.action=='template':template(root,iso)
        else:create(root,args.exam,iso)
    elif args.action=='open-golden':
        vmx,_=owned(root,'golden');vr('start',vmx,'gui')
    elif args.action=='seed':seed(root,args.node)
    else:
        vmx,data=owned(root,args.node)
        if args.action=='start':vr('start',vmx,'gui');return
        off(vmx)
        if args.action=='snapshot':
            if not data.get('seeded'):fail('Seed this VM before the ready snapshot')
            if 'exam-ready' in vr('listSnapshots',vmx).splitlines()[1:]:fail('Snapshot already exists; preserved')
            vr('snapshot',vmx,'exam-ready');data['snapshot']='exam-ready';mark(vmx.parent,data)
        elif args.action=='reset':
            if data.get('snapshot')!='exam-ready':fail('No tracked exam-ready snapshot')
            if 'exam-ready' not in vr('listSnapshots',vmx).splitlines()[1:]:fail('Tracked snapshot missing')
            vr('revertToSnapshot',vmx,'exam-ready')
            print('Reverted. Use start to begin the exam again.')
        else:
            if data.get('seeded') or data.get('snapshot'):fail('Add extra disks only before seeding/snapshot')
            e=load(vmx);used=[int(m[1]) for k in e for m in [re.match(r'nvme0:(\d+)\.filename$',k)] if m]
            slot=max(used,default=0)+1
            if slot>14:fail('NVMe slots exhausted')
            filename=f'extra-{slot}-{args.size}G.vmdk';disk(vmx.parent/filename,args.size)
            e.update({f'nvme0:{slot}.present':'TRUE',f'nvme0:{slot}.filename':filename});save(vmx,e)
            data.setdefault('extra_sizes',list(NODES[args.node][1])).append(args.size)
            mark(vmx.parent,data)
            (BASE/'guest-seeds'/f'{args.node}.sh').write_text(seed_text(args.node,data))
            print('Disk attached; actual guest name must be checked with lsblk.')


if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,ValueError) as exc:
        print('STOPPED: '+str(exc),file=sys.stderr);sys.exit(1)
