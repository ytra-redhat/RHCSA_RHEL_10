#!/usr/bin/env python3
"""Safe static and mocked regression checks, no real Fusion or guest calls."""
import ast
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fusion_lab', ROOT/'RHCSA-Lab-Scripts/fusion-lab.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='fusion-course-test-')
        self.root=Path(self.tmp.name)/'VMs with spaces'
        self.original=(m.vr,m.disk,m.BASE)
        self.events=[];self.running=[];self.snaps={};self.fail_clone=False
        m.BASE=Path(self.tmp.name)/'course';m.BASE.mkdir()
        m.vr=self.vr;m.disk=self.disk
        m.template(self.root,Path('/ISO path/Rocky-aarch64-dvd1.iso'))

    def tearDown(self):
        m.vr,m.disk,m.BASE=self.original
        self.tmp.cleanup()

    def disk(self,path,size):
        self.events.append(('disk',size));path.write_text('mock vmdk')

    def vr(self,cmd,*args):
        self.events.append((cmd,))
        if cmd=='list':return 'Total running VMs: '+str(len(self.running))+'\n'+'\n'.join(self.running)
        if cmd=='clone':
            if self.fail_clone:raise RuntimeError('simulated clone failure')
            src,dst=map(Path,args[:2]);dst.parent.mkdir(parents=True)
            e=m.load(src);e['nvme0:0.filename']='cloned-system.vmdk';m.save(dst,e)
            (dst.parent/'cloned-system.vmdk').write_text('clone')
            return ''
        if cmd=='listSnapshots':return 'Total snapshots: 0\n'
        raise AssertionError('Unexpected vmrun call '+cmd)

    def test_all_exam_disk_layouts_and_seed_identities(self):
        for exam in (1,2,3):m.create(self.root,exam,Path('/ISO path/Rocky-aarch64-dvd1.iso'))
        macs=set()
        for node,(_,sizes,_,_) in m.NODES.items():
            vmx,data=m.owned(self.root,node);e=m.load(vmx)
            for mac in (data['mac0'],data['mac1']):
                self.assertNotIn(mac,macs);macs.add(mac)
            self.assertEqual(e['ethernet0.connectiontype'],'nat')
            self.assertEqual(e['ethernet1.connectiontype'],'hostonly')
            self.assertNotIn('..',e['nvme0:0.filename'])
            self.assertEqual(len(list(vmx.parent.glob('extra-*.vmdk'))),len(sizes))
            for i,size in enumerate(sizes,1):
                self.assertEqual(e[f'nvme0:{i}.filename'],f'extra-{i}-{size}G.vmdk')
            s=(m.BASE/'guest-seeds'/f'{node}.sh').read_text()
            self.assertIn(data['id'],s)
            self.assertIn(data['mac1'],s)
            self.assertIn('guestinfo.rhcsa_seed',s)
            self.assertIn('rm -f /etc/ssh/ssh_host_',s)
            x=subprocess.run(['bash','-n'],input=s,text=True,capture_output=True)
            self.assertEqual(x.returncode,0,x.stderr)
        self.assertEqual([x[1] for x in self.events if x[0]=='disk'],[30,10,10,5,8,6,4,8,8,6,8])

    def test_repeat_create_preserves_existing_bundle(self):
        m.create(self.root,1,Path('/dvd.iso'))
        p,_=m.owned(self.root,'alpha');before=p.read_bytes()
        with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
        self.assertEqual(before,p.read_bytes())

    def test_unowned_destination_refused_before_clone(self):
        (self.root/'rhel10-bravo.vmwarevm').mkdir()
        with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
        self.assertNotIn(('clone',),self.events)

    def test_running_golden_refused(self):
        p,_=m.owned(self.root,'golden');self.running=[str(p)]
        with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))

    def test_locked_or_suspended_vm_refused(self):
        p,_=m.owned(self.root,'golden');(p.parent/'run.lck').mkdir()
        with self.assertRaises(RuntimeError):m.off(p)
        (p.parent/'run.lck').rmdir();e=m.load(p);e['checkpoint.vmstate']='suspend.vmss';m.save(p,e)
        with self.assertRaises(RuntimeError):m.off(p)

    def test_ownership_tampering_refused(self):
        p,data=m.owned(self.root,'golden');data['owner']='other';m.mark(p.parent,data)
        with self.assertRaises(RuntimeError):m.owned(self.root,'golden')

    def test_symlink_bundle_refused(self):
        other=Path(self.tmp.name)/'other';other.mkdir()
        (self.root/'rhel10-alpha.vmwarevm').symlink_to(other)
        with self.assertRaises(RuntimeError):m.owned(self.root,'alpha')

    def test_failed_clone_does_not_delete_template(self):
        p,_=m.owned(self.root,'golden');before=p.read_bytes();self.fail_clone=True
        with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
        self.assertEqual(before,p.read_bytes())

    def test_seed_conditions_are_role_specific(self):
        for node in m.NODES:
            s=m.seed_text(node,dict(id='testid',mac0='00:50:56:00:01:02',mac1='00:50:56:00:01:03'))
            self.assertEqual('chpasswd' in s,node in {'bravo','charlie','foxtrot'})
            self.assertEqual('deadbeef-0000' in s,node=='foxtrot')
            self.assertEqual('set-default rescue.target' in s,node=='delta')
            self.assertEqual('Listen 8404' in s,node=='echo')
            self.assertLess(s.index('Wrong VM MACs'),s.index('hostnamectl'))

    def call_main(self, action, node):
        with patch('sys.argv',['fusion-lab.py','--root',str(self.root),action,'--node',node]), \
             patch.object(m.platform,'system',return_value='Darwin'), \
             patch.object(m.platform,'machine',return_value='arm64'), \
             patch.object(m,'VMRUN',Path(__file__)),patch.object(m,'VDISK',Path(__file__)):
            m.main()

    def test_snapshot_and_reset_require_tracked_ready_state(self):
        m.create(self.root,1,Path('/dvd.iso'))
        with self.assertRaises(RuntimeError):self.call_main('snapshot','alpha')
        with self.assertRaises(RuntimeError):self.call_main('reset','alpha')
        vmx,data=m.owned(self.root,'alpha');data['seeded']=True;m.mark(vmx.parent,data)
        snapshots=[];calls=[]
        def fake(cmd,*args):
            if cmd=='list':return 'Total running VMs: 0\n'
            if cmd=='listSnapshots':return 'Total snapshots: '+str(len(snapshots))+'\n'+'\n'.join(snapshots)
            if cmd=='snapshot':snapshots.append(args[1]);calls.append(cmd);return ''
            if cmd=='revertToSnapshot':calls.append(cmd);return ''
            raise AssertionError(cmd)
        m.vr=fake
        self.call_main('snapshot','alpha')
        with self.assertRaises(RuntimeError):self.call_main('snapshot','alpha')
        self.call_main('reset','alpha')
        self.assertEqual(calls,['snapshot','revertToSnapshot'])
        snapshots.clear()
        with self.assertRaises(RuntimeError):self.call_main('reset','alpha')

    def test_seed_requires_guest_completion_marker(self):
        m.create(self.root,1,Path('/dvd.iso'))
        vmx,data=m.owned(self.root,'alpha')
        marker=[''];calls=[]
        def fake(cmd,*args):
            if cmd=='list':return 'Total running VMs: 1\n'+str(vmx)
            if cmd=='-gu':calls.append(args[3]);return ''
            if cmd=='readVariable':return marker[0]
            raise AssertionError(cmd)
        m.vr=fake
        with patch.object(m.getpass,'getpass',return_value='test-password'):
            with self.assertRaises(RuntimeError):m.seed(self.root,'alpha')
            self.assertFalse(m.owned(self.root,'alpha')[1]['seeded'])
            marker[0]=data['id'];m.seed(self.root,'alpha')
        self.assertTrue(m.owned(self.root,'alpha')[1]['seeded'])
        self.assertIn('runProgramInGuest',calls)

    def test_repeated_template_refused(self):
        with self.assertRaises(RuntimeError):m.template(self.root,Path('/dvd.iso'))

    def test_nvme_partition_mapping_and_no_libvirt_in_active_exams(self):
        for n in (1,2,3):
            text=(ROOT/f'RHCSA Practice Exam {n} - RHEL 10.md').read_text()
            self.assertIsNone(re.search(r'/dev/[vs]d[a-e]',text))
            self.assertNotIn('virsh ',text)
            self.assertNotIn('virt-clone ',text)
            self.assertIsNone(re.search(r'nvme0n\d+[0-9]{2}\b',text))
            self.assertIn('/dev/nvme0n1',text)
        self.assertIn('/dev/nvme0n2p1',(ROOT/'RHCSA Practice Exam 1 - RHEL 10.md').read_text())


def static():
    count=0;blocks=0
    for p in (ROOT/'RHCSA-Lab-Scripts').glob('*.py'):ast.parse(p.read_text())
    for p in (ROOT/'RHCSA-Lab-Scripts').glob('*.sh'):
        x=subprocess.run(['bash','-n',str(p)],capture_output=True,text=True)
        assert x.returncode==0,(p,x.stderr);count+=1
    for p in ROOT.glob('RHCSA Practice Exam *.md'):
        for code in re.findall(r'```(?:bash|sh)\n(.*?)\n```',p.read_text(),re.S):
            x=subprocess.run(['bash','-n'],input=code,capture_output=True,text=True)
            assert x.returncode==0,(p.name,x.stderr,code[:160]);blocks+=1
    print(f'Syntax OK: {count} delivered shell scripts, {blocks} exam command blocks')


if __name__=='__main__':
    static()
    unittest.main(verbosity=2)
