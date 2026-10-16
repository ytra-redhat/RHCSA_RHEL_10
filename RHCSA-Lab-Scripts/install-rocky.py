#!/usr/bin/env python3
"""Create and start a NEW guarded Rocky 10 ARM golden; never reinstall a bundle."""
import argparse
import configparser
import getpass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fusion_auto', BASE/'RHCSA-Lab-Scripts/fusion-lab.py')
fusion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fusion)
PACKAGES = ['sudo', *re.search(r'dnf install -y (.*?)\nsystemctl ',
    (BASE/'RHCSA-Lab-Scripts/guest-golden.sh').read_text(), re.S)[1].replace('\\\n',' ').split()]

def run(*args, input=None):
    result = subprocess.run(list(map(str,args)), input=input, text=True,
                            capture_output=True, timeout=3600)
    if result.returncode:
        raise RuntimeError('Installation tool failed: '+str(args[0])+'\n'+result.stderr[-2000:])
    return result.stdout + result.stderr

def checksum(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''): h.update(block)
    return h.hexdigest()

def ask_hash(label):
    password=getpass.getpass(label+' (minimaal 12 tekens): ')
    if len(password)<12 or '\n' in password or '\x00' in password:
        raise RuntimeError('Gebruik een labwachtwoord van minimaal 12 tekens')
    if getpass.getpass(label+' opnieuw: ')!=password:
        raise RuntimeError('Wachtwoorden verschillen')
    result=run(shutil.which('openssl'),'passwd','-6','-stdin',input=password+'\n').strip()
    if not re.fullmatch(r'\$6\$[./A-Za-z0-9]+\$[./A-Za-z0-9]+',result):
        raise RuntimeError('OpenSSL SHA-512 password hashing unavailable')
    return result

def boot_config(label):
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,32}',label):
        raise RuntimeError('Unsupported ISO label')
    return f'''set default=0
set timeout=5
insmod gzio
insmod part_gpt
insmod fat
insmod iso9660
search --no-floppy --set=root -l '{label}'
menuentry 'RHCSA AUTO - NEW guarded golden only' {{
 linux /images/pxeboot/vmlinuz inst.stage2=hd:LABEL={label} inst.repo=cdrom inst.ks=hd:LABEL={label}:/rhcsa-auto/ks.cfg inst.text
 initrd /images/pxeboot/initrd.img
}}
'''

def kickstart(data,root_hash,student_hash):
    for field in ('mac0','mac1'):
        if not re.fullmatch(r'(?:[0-9a-f]{2}:){5}[0-9a-f]{2}',data[field]):
            raise RuntimeError('Invalid expected MAC')
    if not re.fullmatch(r'[a-f0-9]{32}',data['id']):raise RuntimeError('Invalid install identity')
    for value in (root_hash,student_hash):
        if not re.fullmatch(r'\$6\$[./A-Za-z0-9]+\$[./A-Za-z0-9]+',value):raise RuntimeError('Invalid password hash')
    profiles={}
    for name,mac,method,v6 in [('fusion-nat',data['mac0'],'auto','auto'),('fusion-lab',data['mac1'],'disabled','disabled')]:
        profiles[name]=f'''[connection]
id={name}
uuid={uuid.uuid4()}
type=ethernet
autoconnect=true
zone=public

[ethernet]
mac-address={mac}

[ipv4]
method={method}

[ipv6]
method={v6}
'''
    # Embed only JSON with fixed/generated data, never shell-interpolated user input.
    post=f'''set -euo pipefail
systemctl enable vmtoolsd NetworkManager sshd firewalld
systemctl set-default multi-user.target
python3 - <<'PROFILES'
from pathlib import Path
import configparser
folder=Path('/etc/NetworkManager/system-connections');folder.mkdir(parents=True,exist_ok=True)
for p in folder.glob('*.nmconnection'):
 c=configparser.ConfigParser(interpolation=None);c.read(p)
 if c.get('connection','type',fallback='') in ('ethernet','802-3-ethernet'):
  c.set('connection','autoconnect','false')
  with p.open('w') as f:c.write(f)
  p.chmod(0o600)
profiles={profiles!r}
for name,text in profiles.items():
 p=folder/(name+'.nmconnection');p.write_text(text);p.chmod(0o600)
PROFILES
printf '%s\\n' 'jconwell-fusion-golden-v2' > /etc/rhcsa-fusion-golden
cat > /root/guest-seal.sh <<'SEALSCRIPT'
{(BASE/'RHCSA-Lab-Scripts/guest-seal.sh').read_text().rstrip()}
SEALSCRIPT
cat > /root/rhcsa-finish-golden.sh <<'FINISHSCRIPT'
#!/bin/bash
set -euo pipefail
[[ $(id -u) == 0 && -z ${{SSH_CONNECTION:-}} ]] || {{ echo 'Gebruik root in Fusion-console'; exit 1; }}
[[ $(cat /etc/rhcsa-auto-installed) == {data['id']} ]] || exit 1
[[ $(uname -m) == aarch64 && $(getenforce) == Enforcing ]] || exit 1
INSTALL_DISKS=$(lsblk -dnr -o NAME,TYPE | awk '$2=="disk" && $1 !~ /^zram[0-9]+$/ {{print $1}}')
[[ "$INSTALL_DISKS" == nvme0n1 ]] || exit 1
[[ $(passwd -S root | awk '{{print $2}}') == P ]] || exit 1
SUDO_REPORT=$(LC_ALL=C sudo -l -U student 2>&1) || true
printf '%s\\n' "$SUDO_REPORT" | grep -Eq '^User student is not allowed to run sudo on .+\.$' || {{ echo 'Sudo-rechten student niet veilig uitgesloten'; exit 1; }}
for unit in vmtoolsd NetworkManager sshd firewalld; do systemctl is-active --quiet "$unit"; done
ssh-keygen -A
vmware-toolbox-cmd timesync disable
bash /root/guest-seal.sh
FINISHSCRIPT
chmod 700 /root/guest-seal.sh /root/rhcsa-finish-golden.sh
[[ $(passwd -S root | awk '{{print $2}}') == P ]]
[[ $(id -u student) == 1000 ]]
! id -nG student | tr ' ' '\\n' | grep -qx wheel
printf '%s\\n' '{data['id']}' > /etc/rhcsa-auto-installed
restorecon -RF /etc/NetworkManager/system-connections /root/guest-seal.sh /root/rhcsa-finish-golden.sh /etc/rhcsa-fusion-golden /etc/rhcsa-auto-installed
sync
'''
    return f'''# Generated ONLY for a new, empty Fusion golden with matching MACs.
text
lang en_US.UTF-8
keyboard --vckeymap=us --xlayouts=us
timezone Europe/Amsterdam --utc
cdrom
rootpw --iscrypted {root_hash}
user --name=student --uid=1000 --gid=1000 --password={student_hash} --iscrypted
network --device={data['mac0']} --bootproto=dhcp --activate --onboot=yes --hostname=rhel10-golden --noipv6
firewall --enabled --service=ssh
selinux --enforcing
firstboot --disable
services --enabled=vmtoolsd,NetworkManager,sshd,firewalld
ignoredisk --only-use=nvme0n1
clearpart --all --initlabel --disklabel=gpt --drives=nvme0n1
reqpart
part /boot --fstype=xfs --size=1024 --ondisk=nvme0n1
part pv.01 --size=1 --grow --ondisk=nvme0n1
volgroup rl pv.01
logvol swap --fstype=swap --size=2048 --name=swap --vgname=rl
logvol / --fstype=xfs --size=8192 --grow --name=root --vgname=rl
bootloader --append="crashkernel=auto"
poweroff

%pre --interpreter=/bin/bash --erroronfail --log=/tmp/rhcsa-auto-pre.log
set -euo pipefail
trap 'echo "Installation guard failed at line $LINENO; no disk may be cleared" >&2' ERR
[[ $(uname -m) == aarch64 && -d /sys/firmware/efi ]]
INSTALL_DISKS=$(lsblk -dnr -o NAME,TYPE | awk '$2=="disk" && $1 !~ /^zram[0-9]+$/ {{print $1}}')
[[ "$INSTALL_DISKS" == nvme0n1 ]]
[[ -b /dev/nvme0n1 && $(blockdev --getsize64 /dev/nvme0n1) == 32212254720 ]]
[[ -z $(wipefs -n --noheadings /dev/nvme0n1) ]]
[[ -z $(lsblk -nr -o TYPE /dev/nvme0n1 | grep '^part$' || true) ]]
for expected in '{data['mac0']}' '{data['mac1']}'; do
 grep -lx "$expected" /sys/class/net/*/address >/dev/null
 done
[[ $(find /sys/class/net -mindepth 1 -maxdepth 1 ! -name lo | wc -l) -eq 2 ]]
%end

%packages
@^minimal-environment
{chr(10).join(PACKAGES)}
%end

%post --interpreter=/bin/bash --erroronfail --log=/root/rhcsa-auto-post.log
{post}%end
'''

def build_iso(source,output,data,root_hash,student_hash):
    if output.exists():raise RuntimeError('Output ISO exists; preserved')
    if output.resolve()==source.resolve():raise RuntimeError('Source ISO cannot be overwritten')
    for name in ('xorriso','mcopy','mdir','openssl'):
        if not shutil.which(name):raise RuntimeError('Missing tool: '+name+'; see AUTOMATISCHE-INSTALLATIE.md')
    if shutil.disk_usage(output.parent).free < source.stat().st_size+1024**3:
        raise RuntimeError('Insufficient free space for independent installation ISO')
    with tempfile.TemporaryDirectory(prefix='rhcsa-iso-',dir=output.parent) as tmp:
        work=Path(tmp);work.chmod(0o700)
        run('xorriso','-osirrox','on','-indev',source,'-extract','/.treeinfo',work/'treeinfo',
            '-extract','/images/efiboot.img',work/'efiboot.img')
        (work/'efiboot.img').chmod(0o600)
        (work/'treeinfo').chmod(0o600)
        tree=configparser.ConfigParser(interpolation=None);tree.read(work/'treeinfo')
        if tree.get('tree','arch',fallback='')!='aarch64' or tree.get('release','name',fallback='')!='Rocky Linux' or not tree.get('release','version',fallback='').startswith('10.'):
            raise RuntimeError('Expected a Rocky Linux 10 aarch64 DVD, verified through .treeinfo')
        if not all(tree.has_section('variant-'+name) for name in ('BaseOS','AppStream')):
            raise RuntimeError('DVD lacks BaseOS or AppStream metadata')
        listing=run('xorriso','-indev',source,'-find','/','-name','*.rpm','-exec','echo','--')
        missing=[name for name in PACKAGES if not re.search(r'/'+re.escape(name)+r'-[0-9]',listing)]
        if missing:raise RuntimeError('Required packages absent on DVD: '+', '.join(missing))
        report=run('xorriso','-indev',source,'-pvd_info','-report_el_torito','plain')
        labels=re.findall(r"Volume (?:id|Id)\s*:\s*'([^']+)'",report)
        if not labels:raise RuntimeError('Cannot determine DVD volume label')
        label=labels[0]
        grub=boot_config(label);(work/'grub.cfg').write_text(grub)
        run('mdir','-i',work/'efiboot.img','::/EFI/BOOT/BOOTAA64.EFI')
        run('mcopy','-o','-i',work/'efiboot.img',work/'grub.cfg','::/EFI/BOOT/grub.cfg')
        if run('mcopy','-i',work/'efiboot.img','::/EFI/BOOT/grub.cfg','-').strip()!=grub.strip():
            raise RuntimeError('Embedded EFI GRUB verification failed')
        ks=kickstart(data,root_hash,student_hash);(work/'ks.cfg').write_text(ks);(work/'ks.cfg').chmod(0o600)
        tree.set('checksums','images/efiboot.img','sha256:'+checksum(work/'efiboot.img'))
        with (work/'treeinfo').open('w') as f:tree.write(f)
        partial=output.with_suffix('.iso.partial')
        if partial.exists():raise RuntimeError('Partial ISO exists; preserve and inspect it before retry')
        # Private file permissions from its creation, including password hashes.
        previous=os.umask(0o077)
        try:
            run('xorriso','-indev',source,'-outdev',partial,
                '-map',work/'ks.cfg','/rhcsa-auto/ks.cfg',
                '-map',work/'grub.cfg','/EFI/BOOT/grub.cfg',
                '-map',work/'efiboot.img','/images/efiboot.img',
                '-map',work/'treeinfo','/.treeinfo','-boot_image','any','replay','-commit','-end')
            run('xorriso','-osirrox','on','-indev',partial,
                '-extract','/rhcsa-auto/ks.cfg',work/'checked.ks',
                '-extract','/EFI/BOOT/grub.cfg',work/'checked.grub',
                '-extract','/images/efiboot.img',work/'checked.efi')
            if (work/'checked.ks').read_text()!=ks or (work/'checked.grub').read_text()!=grub:
                raise RuntimeError('Installation ISO content verification failed')
            if run('mcopy','-i',work/'checked.efi','::/EFI/BOOT/grub.cfg','-').strip()!=grub.strip():
                raise RuntimeError('Final EFI image did not retain automatic boot configuration')
            bootreport=run('xorriso','-indev',partial,'-report_el_torito','plain')
            if not re.search(r'UEFI\s+y',bootreport):raise RuntimeError('Output lacks bootable UEFI entry')
            partial.chmod(0o600);partial.replace(output)
        finally:os.umask(previous)
    return {'source_sha256':checksum(source),'output_sha256':checksum(output),
            'volume_label':label,'rocky_version':tree.get('release','version'),
            'uefi_bootable':True,'efi_and_iso_grub_identical':True,
            'packages_on_dvd':PACKAGES,'live_installation_tested':False}

def install(root,source,prepare_only=False):
    root=root.expanduser().resolve();source=fusion.iso_path(str(source))
    if (root/'rhel10-golden.vmwarevm').exists():
        raise RuntimeError('Existing golden preserved. Use a NEW VM root; this action never reinstalls.')
    for name in ('xorriso','mcopy','mdir','openssl'):
        if not shutil.which(name):raise RuntimeError('Missing tool: '+name)
    lock=fusion.acquire_operation_lock(root)
    try:
        folder=root/'auto-install'
        if folder.exists():raise RuntimeError('Earlier auto-install folder preserved; inspect it before using a new VM root')
        data=dict(owner=fusion.OWNER,node='golden',schema=2,phase='ready',
                  mac0=fusion.mac(),mac1=fusion.mac(),id=uuid.uuid4().hex)
        root_hash=ask_hash('Rootwachtwoord');student_hash=ask_hash('Studentwachtwoord')
        folder.mkdir(mode=0o700,exist_ok=False)
        output=folder/'Rocky-10-aarch64-dvd-auto.iso'
        print('Nieuwe installatie-ISO maken en controleren; de bron blijft ongewijzigd.',flush=True)
        evidence=build_iso(source,output,data,root_hash,student_hash)
        evidence.update(install_id=data['id'],original_iso=str(source),auto_iso=str(output))
        (folder/'media-check.json').write_text(json.dumps(evidence,indent=2)+'\n')
        fusion.template(root,output)
        vmx,template_data=fusion.owned(root,'golden')
        # template is brand new; replace its generated MACs with the ISO-bound identity.
        e=fusion.load(vmx);fusion.network(e,data);fusion.save(vmx,e)
        data['auto_install']={'id':data['id'],'original_iso':str(source),'iso':str(output)}
        fusion.mark(vmx.parent,data)
        if prepare_only:print('Voorbereid; start later met install-rocky.py start --root ...')
        else:fusion.vr('start',vmx,'gui');print('Installatie gestart. Wacht tot de golden vanzelf uitschakelt. Daarna: install-rocky.py boot --root ...')
    finally:lock.close()


def repair_media(root):
    """Rebuild only the failed pre-install media; preserve VM, disk and hashes."""
    root=root.expanduser().resolve();lock=fusion.acquire_operation_lock(root)
    try:
        vmx,data=fusion.owned(root,'golden')
        auto=data.get('auto_install',{})
        if data.get('schema')!=2 or auto.get('id')!=data['id'] or auto.get('boot_original'):
            raise RuntimeError('Repair only an automatic golden stopped BEFORE installation')
        fusion.off(vmx)
        folder=root/'auto-install'
        if folder.is_symlink():raise RuntimeError('Unsafe media folder')
        evidence_path=folder/'media-check.json'
        previous=json.loads(evidence_path.read_text())
        if previous.get('install_id')!=data['id']:raise RuntimeError('Media identity mismatch')
        source=fusion.iso_path(auto['original_iso'])
        old_iso=Path(auto['iso']).resolve()
        if old_iso.parent!=folder.resolve() or not old_iso.is_file():raise RuntimeError('Old media must be in the owned install folder')
        print('Bestaande media en originele DVD controleren; wachtwoorden blijven behouden.',flush=True)
        if checksum(old_iso)!=previous.get('output_sha256') or checksum(source)!=previous.get('source_sha256'):
            raise RuntimeError('Media checksum mismatch; preserved without changes')
        with tempfile.TemporaryDirectory(prefix='repair-',dir=folder) as tmp:
            work=Path(tmp);work.chmod(0o700)
            run('xorriso','-osirrox','on','-indev',old_iso,'-extract','/rhcsa-auto/ks.cfg',work/'old.ks')
            text=(work/'old.ks').read_text()
            roots=re.findall(r'^rootpw --iscrypted (\S+)$',text,re.M)
            users=re.findall(r'^user --name=student --uid=1000 --gid=1000 --password=(\S+) --iscrypted$',text,re.M)
            if len(roots)!=1 or len(users)!=1:raise RuntimeError('Cannot safely recover the existing password hashes')
            output=folder/('Rocky-10-aarch64-dvd-auto-zramfix-'+uuid.uuid4().hex[:8]+'.iso')
            current=build_iso(source,output,data,roots[0],users[0])
        current.update(install_id=data['id'],original_iso=str(source),auto_iso=str(output),repair='exclude-zram')
        e=fusion.load(vmx)
        backup=vmx.with_suffix('.vmx.before-zramfix')
        if not backup.exists():backup.write_bytes(vmx.read_bytes())
        e['sata0:0.filename']=str(output);e['sata0:0.startconnected']='TRUE';e['bios.bootorder']='cdrom,hdd'
        fusion.save(vmx,e)
        data['auto_install']['iso']=str(output);fusion.mark(vmx.parent,data)
        temp=evidence_path.with_suffix('.json.tmp');temp.write_text(json.dumps(current,indent=2)+'\n');temp.chmod(0o600);temp.replace(evidence_path)
        print('Installatiemedia hersteld. VM-disk en gekozen wachtwoorden behouden. Start met install-rocky.py start --root ...')
    finally:lock.close()


def action(root,boot=False):
    root=root.expanduser().resolve();lock=fusion.acquire_operation_lock(root)
    try:
        vmx,data=fusion.owned(root,'golden')
        if data.get('schema')!=2 or data.get('auto_install',{}).get('id')!=data['id']:
            raise RuntimeError('Not an automatically prepared v2 golden')
        fusion.off(vmx,require_unlocked=boot)
        if boot:
            original=fusion.iso_path(data['auto_install']['original_iso'])
            e=fusion.load(vmx)
            e['bios.bootorder']='hdd,cdrom';e['sata0:0.filename']=str(original)
            e['sata0:0.startconnected']='FALSE';fusion.save(vmx,e)
            data['auto_install']['boot_original']=True;fusion.mark(vmx.parent,data)
        elif data['auto_install'].get('boot_original'):
            raise RuntimeError('Installer already detached; use the normal open-golden command')
        fusion.vr('start',vmx,'gui')
    finally:lock.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='action',required=True)
    for name in ('install','start','boot','repair-media'):
        a=sub.add_parser(name);a.add_argument('--root',type=Path,default=Path.home()/'RHCSA-Fusion-auto')
        if name=='install':a.add_argument('--iso',required=True,type=Path);a.add_argument('--prepare-only',action='store_true')
    args=p.parse_args()
    if platform.system()!='Darwin' or platform.machine() not in ('arm64','aarch64'):
        raise RuntimeError('Use Apple Silicon macOS')
    if not fusion.VMRUN.is_file() or not fusion.VDISK.is_file():raise RuntimeError('Fusion must be installed in /Applications')
    if args.action=='install':install(args.root,args.iso,args.prepare_only)
    elif args.action=='repair-media':repair_media(args.root)
    else:action(args.root,args.action=='boot')

if __name__=='__main__':
    try:main()
    except (RuntimeError,OSError,ValueError,subprocess.TimeoutExpired) as error:
        print('STOPPED: '+str(error),file=sys.stderr);sys.exit(1)
