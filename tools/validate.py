#!/usr/bin/env python3
"""Local regression/structural checks. No live Fusion/guest mutations."""
import ast,importlib.util,json,re,subprocess,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('fusion',ROOT/'RHCSA-Lab-Scripts/fusion-lab.py')
v=module('verify',ROOT/'tools/verify.py')

class Host(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'VMs with spaces';self.events=[];self.running=[];self.snapshots={};self.failnode=None;self.faildisk=False
  self.old=(m.vr,m.disk,m.BASE,m.run)
  m.BASE=Path(self.temp.name)/'code';m.BASE.mkdir();m.vr=self.vr;m.disk=self.disk;m.run=lambda *a:''
  m.template(self.root,Path('/ISO with spaces/Rocky-aarch64-dvd1.iso'))
 def tearDown(self):m.vr,m.disk,m.BASE,m.run=self.old;self.temp.cleanup()
 def disk(self,path,size):
  if self.faildisk:self.faildisk=False;raise RuntimeError('interrupted disk')
  path.write_text('parentCID=ffffffff\nRW '+str(size*1024**3//512)+' SPARSE "'+path.name+'"\n')
 def vr(self,cmd,*args):
  self.events.append((cmd,*map(str,args)))
  if cmd=='list':return 'Total running VMs: '+str(len(self.running))+'\n'+'\n'.join(self.running)
  if cmd=='clone':
   src,dst=map(Path,args[:2])
   if self.failnode and self.failnode in dst.name:self.failnode=None;raise RuntimeError('interrupted clone')
   dst.parent.mkdir(parents=True);entries=m.load(src);entries['nvme0:0.filename']='system.vmdk';self.disk(dst.parent/'system.vmdk',30);m.save(dst,entries);return ''
  if cmd=='listSnapshots':return 'Total snapshots: '+str(len(self.snapshots.get(str(args[0]),[])))+'\n'+'\n'.join(self.snapshots.get(str(args[0]),[]))
  if cmd=='snapshot':self.snapshots.setdefault(str(args[0]),[]).append(str(args[1]));return ''
  if cmd=='revertToSnapshot':return ''
  if cmd=='readVariable':return ''
  raise AssertionError(cmd)
 def cli(self,*args):
  with patch.object(sys,'argv',['fusion',*args]),patch.object(m.platform,'system',return_value='Darwin'),patch.object(m.platform,'machine',return_value='arm64'),patch.object(m,'VMRUN',Path(__file__)),patch.object(m,'VDISK',Path(__file__)):
   m.main()
 def test_all_layouts(self):
  for ex in [1,2,3]:m.create(self.root,ex,Path('/dvd.iso'))
  macs=[]
  for n,(_,sizes,_,_) in m.NODES.items():
   vmx,data=m.owned(self.root,n);self.assertEqual(data['phase'],'ready');self.assertEqual(data['schema'],2)
   self.assertEqual(len(m.validate_disks(vmx,m.load(vmx))),len(sizes)+1)
   macs.extend([data['mac0'],data['mac1']])
   seed=m.seed_text(n,data)
   self.assertEqual(subprocess.run(['bash','-n'],input=seed,text=True,capture_output=True).returncode,0)
   self.assertIn('blockdev --getsize64',seed)
  self.assertEqual(len(macs),len(set(macs)))
 def test_second_clone_resume(self):
  self.failnode='bravo'
  with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
  alpha,_=m.owned(self.root,'alpha');old=alpha.read_bytes();m.create(self.root,1,Path('/dvd.iso'));self.assertEqual(old,alpha.read_bytes());m.owned(self.root,'bravo')
 def test_repeat_preserves_ready(self):
  m.create(self.root,1,Path('/dvd.iso'));old=len([x for x in self.events if x[0]=='clone']);m.create(self.root,1,Path('/dvd.iso'));self.assertEqual(old,len([x for x in self.events if x[0]=='clone']))
 def test_unowned_pair_refused_before_any_clone(self):
  (self.root/'rhel10-bravo.vmwarevm').mkdir()
  with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
  self.assertFalse(any(x[0]=='clone' for x in self.events))
 def test_hardware_resume(self):
  m.create(self.root,1,Path('/dvd.iso'));vmx,d=m.owned(self.root,'alpha');d['phase']='hardware';m.mark(vmx.parent,d);m.create(self.root,1,Path('/dvd.iso'));self.assertEqual(m.owned(self.root,'alpha')[1]['phase'],'ready')
 def test_wrong_capacity_stops(self):
  m.create(self.root,1,Path('/dvd.iso'));vmx,d=m.owned(self.root,'alpha');d['phase']='hardware';m.mark(vmx.parent,d);self.disk(vmx.parent/'extra-1-10G.vmdk',11)
  with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
 def test_running_golden_refused(self):
  vmx,_=m.owned(self.root,'golden');self.running=[str(vmx)]
  with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
 def test_lock_direct_edit_refused(self):
  vmx,_=m.owned(self.root,'golden');(vmx.parent/'open.lck').mkdir()
  with self.assertRaises(RuntimeError):m.off(vmx)
 def test_snapshot_lock_handled_by_fusion(self):
  m.create(self.root,1,Path('/dvd.iso'));vmx,d=m.owned(self.root,'alpha');d['seeded']=True;m.mark(vmx.parent,d);(vmx.parent/'open.lck').mkdir()
  self.cli('snapshot','--node','alpha','--root',str(self.root));self.cli('reset','--node','alpha','--root',str(self.root));self.assertEqual(self.snapshots[str(vmx.resolve())],['exam-ready-v2'])
 def test_running_snapshot_refused(self):
  m.create(self.root,1,Path('/dvd.iso'));vmx,d=m.owned(self.root,'alpha');d['seeded']=True;m.mark(vmx.parent,d);self.running=[str(vmx)]
  with self.assertRaises(RuntimeError):self.cli('snapshot','--node','alpha','--root',str(self.root))
 def test_suspended_refused(self):
  vmx,_=m.owned(self.root,'golden');e=m.load(vmx);e['checkpoint.vmstate']='x.vmss';m.save(vmx,e)
  with self.assertRaises(RuntimeError):m.off(vmx,False)
 def test_seed_roles_and_marker_order(self):
  for node in m.NODES:
   text=m.seed_text(node,dict(id='f'*32,mac0=m.mac(),mac1=m.mac()))
   if node in ['bravo','charlie','foxtrot']:self.assertLess(text.index('chpasswd'),text.index('> /etc/rhcsa-fusion-seeded.tmp'))
   self.assertEqual('set-default graphical.target' in text,node=='bravo')
   self.assertEqual('GRUB_TIMEOUT=3' in text,node=='alpha')
   self.assertEqual('chmod 000 /opt/finance' in text,node=='charlie')
   self.assertIn('golden-machine-id',text)
 def test_seed_reconciliation_without_password(self):
  m.create(self.root,1,Path('/dvd.iso'));vmx,d=m.owned(self.root,'alpha');self.running=[str(vmx)];oldvr=m.vr
  m.vr=lambda cmd,*a:d['id'] if cmd=='readVariable' else oldvr(cmd,*a)
  with patch.object(m.getpass,'getpass',side_effect=AssertionError('must not request password')):m.seed(self.root,'alpha')
  self.assertTrue(m.owned(self.root,'alpha')[1]['seeded'])
 def test_state_symlink_refused(self):
  p=self.root/'rhel10-golden.vmwarevm'/'fusion-state.json';data=p.read_bytes();p.unlink();target=Path(self.temp.name)/'state';target.write_bytes(data);p.symlink_to(target)
  with self.assertRaises(RuntimeError):m.owned(self.root,'golden')
 def test_external_disk_refused(self):
  vmx,_=m.owned(self.root,'golden');e=m.load(vmx);e['nvme0:0.filename']='/tmp/other.vmdk'
  with self.assertRaises(RuntimeError):m.validate_disks(vmx,e)
 def test_unknown_vmx_not_silently_erased(self):
  p=Path(self.temp.name)/'bad.vmx';p.write_text('unquoted = value\n');before=p.read_bytes()
  with self.assertRaises(RuntimeError):m.load(p)
  self.assertEqual(before,p.read_bytes())
 def test_duplicate_key_rejected(self):
  p=Path(self.temp.name)/'bad.vmx';p.write_text('x = "1"\nX = "2"\n')
  with self.assertRaises(RuntimeError):m.load(p)
 def test_legacy_create_and_reset_refused(self):
  m.create(self.root,1,Path('/dvd.iso'));vmx,d=m.owned(self.root,'alpha');d.pop('schema');m.mark(vmx.parent,d)
  with self.assertRaises(RuntimeError):m.create(self.root,1,Path('/dvd.iso'))
  with self.assertRaises(RuntimeError):self.cli('reset','--node','alpha','--root',str(self.root))
 def test_manifest_mac_injection_refused(self):
  vmx,d=m.owned(self.root,'golden');d['mac0']="x'; command";m.mark(vmx.parent,d)
  with self.assertRaises(RuntimeError):m.owned(self.root,'golden')
 def test_timeout_credentials_redacted(self):
  real=self.old[3]
  with patch.object(m.subprocess,'run',side_effect=subprocess.TimeoutExpired(['-gp','secret-test'],1800)):
   with self.assertRaises(RuntimeError) as error:real('-gp','secret-test')
  self.assertNotIn('secret-test',str(error.exception))
 def test_stderr_credentials_redacted(self):
  real=self.old[3]
  with patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess(['tool'],1,'','bad secret-test')):
   with self.assertRaises(RuntimeError) as error:real('-gp','secret-test')
  self.assertNotIn('secret-test',str(error.exception))
 def test_operation_lock_exclusive(self):
  lock=m.acquire_operation_lock(self.root)
  try:
   with self.assertRaises(RuntimeError):m.acquire_operation_lock(self.root)
  finally:lock.close()
 def test_template_repeat_preserved(self):
  vmx,_=m.owned(self.root,'golden');old=vmx.read_bytes();m.template(self.root,Path('/dvd.iso'));self.assertEqual(old,vmx.read_bytes())

class Grader(unittest.TestCase):
 def test_ip_false_positive(self):
  data=json.dumps([dict(addr_info=[dict(local='192.168.100.100')])]);self.assertFalse(v.match(data,'json-address','192.168.100.10'))
 def test_swap_wrong_device_or_priority(self):
  data=json.dumps(dict(swapdevices=[dict(name='/dev/nvme0n2p2',prio=110),dict(name='/dev/other',prio=10)]));self.assertFalse(v.match(data,'swap',dict(name='/dev/nvme0n2p2',prio=10)))
 def test_port_exact(self):self.assertFalse(v.match('22220/tcp 8080/tcp','token','2222/tcp'))
 def test_at_allow_extra_user(self):self.assertFalse(v.match('emma\nstudent\n','equal','emma'))
 def test_bind_same_inode_and_device(self):
  self.assertTrue(v.match('20:40\n20:40\n','same-inode',None))
  self.assertFalse(v.match('20:40\n21:40\n','same-inode',None))
 def test_module_name_field(self):self.assertTrue(v.match('labhttpd 1.0\nother 2.0','module','labhttpd'))
 def test_error_not_pass(self):
  state,detail=v.execute(dict(argv=['definitely-nonexistent-rhcsa-command'],match='nonempty'));self.assertEqual(state,'ERROR')
 def test_numeric_exact(self):self.assertFalse(v.match('116','numeric',16))
 def test_no_eval_or_mutation(self):
  s=(ROOT/'tools/verify.py').read_text();self.assertNotIn('shell=True',s)
  spec=json.loads((ROOT/'tools/checks.json').read_text())
  forbidden={'mount','umount','swapoff','swapon -a','systemctl restart','systemctl start'}
  for ex in spec.values():
   for tasks in ex.values():
    for t in tasks:
     for c in t['checks']:
      command=' '.join(c['argv']);self.assertFalse(any(command==f or command.startswith(f+' ') for f in forbidden),command)
 def test_firewall_runtime_and_permanent(self):
  spec=json.loads((ROOT/'tools/checks.json').read_text());checks=next(x['checks'] for x in spec['1']['alpha'] if x['task']==5)
  for label in ['http','ssh','5900-5910/tcp']:
   matches=[c for c in checks if c.get('expected')==label];self.assertEqual(len(matches),2);self.assertEqual(sum('--permanent' in c['argv'] for c in matches),1)

class Content(unittest.TestCase):
 def test_answer_coverage(self):
  for ex in [1,2,3]:
   s=(ROOT/f'Examen-{ex}-antwoorden.md').read_text();self.assertEqual([int(x) for x in re.findall(r'^\*\*T(\d+) —',s,re.M)],list(range(1,36)))
   q=(ROOT/f'Examen-{ex}-opdrachten.md').read_text();self.assertEqual([int(x) for x in re.findall(r'^\*\*Task (\d+) —',q,re.M)],list(range(1,36)))
 def test_task_interactions(self):
  self.assertIn('T33 vóór T16',(ROOT/'Examen-3-opdrachten.md').read_text())
  self.assertNotIn('create `emma` if needed',(ROOT/'Examen-3-opdrachten.md').read_text())
  self.assertNotIn('segment type becomes linear',(ROOT/'Examen-2-antwoorden.md').read_text())
 def test_no_old_errors(self):
  text='\n'.join(p.read_text() for p in ROOT.glob('Examen-*-antwoorden.md'))
  for bad in ['/dev/mapper/rhel-swap','/dev/rhel/swap','systemctl --user enable alice-web.service','-p RestartSec','/net/team/team          #','kill -HUP $(pgrep chronyd)']:
   self.assertNotIn(bad,text)
 def test_uid_regex_counterexample(self):
  pattern=r'^[^:]+:[^:]*:[0-9]{4}:'
  self.assertFalse(re.match(pattern,'bad:x:99:3100:test:/home/bad:/bin/bash'))
  self.assertTrue(re.match(pattern,'good:x:3100:99:test:/home/good:/bin/bash'))
 def test_105_tasks_in_manual_matrix(self):
  spec=json.loads((ROOT/'tools/checks.json').read_text())
  for ex in [1,2,3]:
   numbers={t['task'] for tasks in spec[str(ex)].values() for t in tasks};self.assertEqual(numbers,set(range(1,36)))


class ScriptExecution(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.dir=Path(self.temp.name);self.bin=self.dir/'bin';self.bin.mkdir()
 def tearDown(self):self.temp.cleanup()
 def script(self,ex,name):
  text=(ROOT/f'Examen-{ex}-antwoorden.md').read_text()
  pattern=r"(?:cat|tee) (?:> )?/[^\n]*"+re.escape(name)+r"[^\n]*<<'EOF'\n(.*?)\nEOF"
  found=re.search(pattern,text,re.S)
  if not found:raise AssertionError('Missing embedded script '+name)
  path=self.dir/name;path.write_text(found[1]+'\n');return path
 def stub(self,name,body):
  p=self.bin/name;p.write_text('#!/bin/bash\n'+body+'\n');p.chmod(0o755)
 def invoke(self,path,*args):
  import os
  return subprocess.run(['bash',str(path),*args],capture_output=True,text=True,env={**os.environ,'PATH':str(self.bin)+':'+os.environ['PATH']})
 def test_diskwatch_four_branches(self):
  path=self.script(3,'diskwatch.sh')
  self.stub('findmnt','[[ "$*" == *"/valid"* ]]')
  self.stub('df','printf "Use%%\n79%%\n"')
  self.assertEqual(self.invoke(path).returncode,2)
  self.assertEqual(self.invoke(path,'/not-mounted').returncode,3)
  self.assertEqual(self.invoke(path,'/valid').returncode,0)
  self.stub('df','printf "Use%%\n80%%\n"')
  self.assertEqual(self.invoke(path,'/valid').returncode,1)
  self.assertIn('CRITICAL',self.invoke(path,'/valid').stdout)
 def test_syscheck_exactly_one_arg(self):
  path=self.script(1,'syscheck.sh')
  for name in ['lscpu','free','df']:self.stub(name,'echo fixture')
  for option in ['cpu','mem','disk','all']:self.assertEqual(self.invoke(path,option).returncode,0)
  self.assertEqual(self.invoke(path).returncode,1)
  self.assertEqual(self.invoke(path,'cpu','mem').returncode,1)
  self.assertEqual(self.invoke(path,'wrong').returncode,1)
 def test_svcctl_exit_paths(self):
  path=self.script(2,'svcctl.sh')
  self.stub('systemctl', 'case "$1" in cat) [[ "$*" != *unknown* ]];; is-active) [[ "$*" != *stopped* ]];; status) exit 3;; *) exit 0;; esac')
  self.assertEqual(self.invoke(path,'check','running').returncode,0)
  self.assertEqual(self.invoke(path,'check','stopped').returncode,1)
  self.assertEqual(self.invoke(path,'invalid','running').returncode,2)
  self.assertEqual(self.invoke(path,'check','unknown').returncode,3)
  self.assertEqual(self.invoke(path,'status','running').returncode,3)
 def test_backup_failure_does_not_claim_success_or_remove_old(self):
  path=self.script(1,'etcbackup.sh');text=path.read_text()
  backups=self.dir/'backups';backups.mkdir();old=backups/'etc_backup_old.tar.gz';old.write_text('old')
  log=self.dir/'backup.log'
  text=text.replace('/root/backups',str(backups)).replace('/var/log/etcbackup.log',str(log));path.write_text(text)
  self.stub('tar','echo simulated-error >&2; exit 2')
  result=self.invoke(path)
  self.assertEqual(result.returncode,1);self.assertIn('FAILED',log.read_text());self.assertNotIn('Created',log.read_text());self.assertTrue(old.exists())
  self.assertEqual(list(backups.glob('.backup.*')),[])
 def test_backup_success_publishes_then_logs(self):
  path=self.script(1,'etcbackup.sh');backups=self.dir/'backups';log=self.dir/'backup.log'
  path.write_text(path.read_text().replace('/root/backups',str(backups)).replace('/var/log/etcbackup.log',str(log)))
  self.stub('tar','printf archive > "$2"; exit 0')
  result=self.invoke(path);self.assertEqual(result.returncode,0,result.stderr);self.assertIn('Created',log.read_text())
  self.assertEqual(len(list(backups.glob('etc_backup_*.tar.gz'))),1)
 def test_bulk_user_failure_not_success(self):
  path=self.script(1,'bulk_users.sh');listing=self.dir/'userlist';listing.write_text('testuser1\n')
  path.write_text(path.read_text().replace('/root/userlist.txt',str(listing)))
  self.stub('id','[[ "$1" == -u ]] && { echo 0; exit 0; }; exit 1')
  self.stub('useradd','exit 4');self.stub('chpasswd','exit 0')
  result=self.invoke(path);self.assertNotEqual(result.returncode,0);self.assertNotIn('created and password set',result.stdout)



class AutomaticInstaller(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.auto=module('auto_installer',ROOT/'RHCSA-Lab-Scripts/install-rocky.py')
  cls.data={'id':'a'*32,'mac0':'00:50:56:01:02:03','mac1':'00:50:56:01:02:04'}
  cls.hash='$6$testsalt$'+'a'*86
 def test_kickstart_restricts_disk_and_identity(self):
  ks=self.auto.kickstart(self.data,self.hash,self.hash)
  self.assertIn('ignoredisk --only-use=nvme0n1',ks)
  self.assertIn('clearpart --all --initlabel --disklabel=gpt --drives=nvme0n1',ks)
  self.assertIn('32212254720',ks);self.assertIn('wipefs -n --noheadings',ks)
  for mac in (self.data['mac0'],self.data['mac1']):self.assertIn(mac,ks)
  self.assertNotIn('--plaintext',ks);self.assertNotIn('--groups=wheel',ks)
  self.assertIn('selinux --enforcing',ks);self.assertIn('\npoweroff\n',ks)
 def test_bad_mac_and_hash_refused(self):
  for data,h in [({**self.data,'mac0':'x; touch /tmp/x'},self.hash),(self.data,'plaintext')]:
   with self.assertRaises(RuntimeError):self.auto.kickstart(data,h,self.hash)
 def test_bad_grub_labels_refused(self):
  for label in ["x'; reboot",'label with spaces','x\nreboot']:
   with self.assertRaises(RuntimeError):self.auto.boot_config(label)
  grub=self.auto.boot_config('Rocky-10-2-aarch64-dvd')
  self.assertIn('set default=0',grub);self.assertEqual(grub.count('menuentry'),1)
  self.assertIn('inst.ks=hd:LABEL=Rocky-10-2-aarch64-dvd:/rhcsa-auto/ks.cfg',grub)
 def test_pre_post_and_embedded_finish_syntax(self):
  ks=self.auto.kickstart(self.data,self.hash,self.hash)
  for block in re.findall(r'%p(?:re|ost)[^\n]*\n(.*?)\n%end',ks,re.S):
   r=subprocess.run(['bash','-n'],input=block,text=True,capture_output=True)
   self.assertEqual(r.returncode,0,r.stderr)
  for block in re.findall(r"<<'(?:SEALSCRIPT|FINISHSCRIPT)'\n(.*?)\n(?:SEALSCRIPT|FINISHSCRIPT)",ks,re.S):
   r=subprocess.run(['bash','-n'],input=block,text=True,capture_output=True)
   self.assertEqual(r.returncode,0,r.stderr)
 def test_existing_golden_preserved_before_password(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);bundle=root/'rhel10-golden.vmwarevm';bundle.mkdir();(bundle/'keep').write_text('preserve')
   iso=root/'Rocky-10-aarch64-dvd.iso';iso.write_bytes(b'fixture')
   with patch.object(self.auto,'ask_hash',side_effect=AssertionError('must not ask')):
    with self.assertRaisesRegex(RuntimeError,'Existing golden preserved'):self.auto.install(root,iso)
   self.assertEqual((bundle/'keep').read_text(),'preserve')
 def test_existing_output_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   source=Path(tmp)/'source.iso';out=Path(tmp)/'output.iso';source.write_bytes(b'source');out.write_bytes(b'keep')
   with self.assertRaisesRegex(RuntimeError,'exists; preserved'):self.auto.build_iso(source,out,self.data,self.hash,self.hash)
   self.assertEqual(out.read_bytes(),b'keep');self.assertEqual(source.read_bytes(),b'source')
 def test_password_hashing_uses_stdin(self):
  captured=[]
  with patch.object(self.auto.getpass,'getpass',side_effect=['lab-password-123','lab-password-123']),patch.object(self.auto,'run',side_effect=lambda *args,**kw:captured.append((args,kw)) or self.hash):
   self.assertEqual(self.auto.ask_hash('Root'),self.hash)
  self.assertNotIn('lab-password-123',str(captured[0][0]))
  self.assertEqual(captured[0][1]['input'],'lab-password-123\n')
 def test_password_mismatch_refused(self):
  with patch.object(self.auto.getpass,'getpass',side_effect=['lab-password-123','different-password']):
   with self.assertRaisesRegex(RuntimeError,'verschillen'):self.auto.ask_hash('Root')
 def test_password_abort_leaves_no_install_media(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);iso=root/'Rocky-10-aarch64-dvd.iso';iso.write_bytes(b'fixture')
   with patch.object(self.auto.shutil,'which',return_value='/fixture/tool'),patch.object(self.auto,'ask_hash',side_effect=RuntimeError('mismatch')):
    with self.assertRaisesRegex(RuntimeError,'mismatch'):self.auto.install(root,iso)
   self.assertFalse((root/'auto-install').exists());self.assertFalse((root/'rhel10-golden.vmwarevm').exists())
 def auto_bundle(self,root):
  root=root.resolve()
  bundle=root/'rhel10-golden.vmwarevm';bundle.mkdir()
  iso=root/'Rocky-10-aarch64-dvd.iso';iso.write_bytes(b'fixture')
  vmx=bundle/'rhel10-golden.vmx'
  data={**self.data,'owner':self.auto.fusion.OWNER,'node':'golden','schema':2,'phase':'ready','auto_install':{'id':self.data['id'],'original_iso':str(iso),'iso':str(root/'auto.iso')}}
  self.auto.fusion.save(vmx,{'bios.bootorder':'cdrom,hdd','sata0:0.filename':str(root/'auto.iso'),'sata0:0.startconnected':'TRUE'})
  self.auto.fusion.mark(bundle,data);return vmx,data,iso
 def test_boot_detaches_automatic_media_before_start(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,iso=self.auto_bundle(root);events=[]
   with patch.object(self.auto.fusion,'off'),patch.object(self.auto.fusion,'vr',side_effect=lambda *args:events.append(args)):
    self.auto.action(root,boot=True)
   e=self.auto.fusion.load(vmx)
   self.assertEqual(e['sata0:0.filename'],str(iso));self.assertEqual(e['sata0:0.startconnected'],'FALSE');self.assertEqual(e['bios.bootorder'],'hdd,cdrom')
   self.assertEqual(events,[('start',vmx,'gui')])
 def test_running_vm_refused_without_edit(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,iso=self.auto_bundle(root);original=vmx.read_bytes()
   with patch.object(self.auto.fusion,'off',side_effect=RuntimeError('running')),patch.object(self.auto.fusion,'vr',side_effect=AssertionError('must not start')):
    with self.assertRaisesRegex(RuntimeError,'running'):self.auto.action(root,boot=True)
   self.assertEqual(vmx.read_bytes(),original)
 def test_installer_restart_after_detach_refused(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,iso=self.auto_bundle(root);data['auto_install']['boot_original']=True;self.auto.fusion.mark(vmx.parent,data)
   with patch.object(self.auto.fusion,'off'),patch.object(self.auto.fusion,'vr',side_effect=AssertionError('must not start')):
    with self.assertRaisesRegex(RuntimeError,'already detached'):self.auto.action(root)
 def repair_bundle(self,root):
  vmx,data,source=self.auto_bundle(root)
  folder=vmx.parent.parent/'auto-install';folder.mkdir()
  old=folder/'Rocky-10-aarch64-dvd-auto.iso';old.write_bytes(b'old media')
  data['auto_install']['iso']=str(old);self.auto.fusion.mark(vmx.parent,data)
  evidence={'install_id':data['id'],'output_sha256':self.auto.checksum(old),'source_sha256':self.auto.checksum(source)}
  (folder/'media-check.json').write_text(json.dumps(evidence))
  (vmx.parent/'system.vmdk').write_bytes(b'disk must remain untouched')
  return vmx,data,source,old,folder
 def extract_old_ks(self,*args,**kwargs):
  Path(args[-1]).write_text(self.auto.kickstart(self.data,self.hash,self.hash));return ''
 def test_repair_preserves_disk_passwords_and_old_iso(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,source,old,folder=self.repair_bundle(root);seen=[]
   def builder(src,out,state,rh,sh):
    seen.append((rh,sh,state['id']));out.write_bytes(b'new media');return {'source_sha256':self.auto.checksum(src),'output_sha256':self.auto.checksum(out)}
   with patch.object(self.auto.fusion,'off'),patch.object(self.auto,'run',side_effect=self.extract_old_ks),patch.object(self.auto,'build_iso',side_effect=builder),patch.object(self.auto.fusion,'vr',side_effect=AssertionError('must not start automatically')):
    self.auto.repair_media(root)
   self.assertEqual(seen,[(self.hash,self.hash,data['id'])])
   self.assertEqual(old.read_bytes(),b'old media');self.assertEqual((vmx.parent/'system.vmdk').read_bytes(),b'disk must remain untouched')
   self.assertNotEqual(self.auto.fusion.load(vmx)['sata0:0.filename'],str(old))
   self.assertTrue(vmx.with_suffix('.vmx.before-zramfix').exists())
 def test_repair_rejects_modified_old_media(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,source,old,folder=self.repair_bundle(root);before=vmx.read_bytes();old.write_bytes(b'tampered')
   with patch.object(self.auto.fusion,'off'),patch.object(self.auto,'build_iso',side_effect=AssertionError('must not build')):
    with self.assertRaisesRegex(RuntimeError,'checksum mismatch'):self.auto.repair_media(root)
   self.assertEqual(vmx.read_bytes(),before)
 def test_repair_refuses_running_guest(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,source,old,folder=self.repair_bundle(root);before=vmx.read_bytes()
   with patch.object(self.auto.fusion,'off',side_effect=RuntimeError('running')),patch.object(self.auto,'build_iso',side_effect=AssertionError('must not build')):
    with self.assertRaisesRegex(RuntimeError,'running'):self.auto.repair_media(root)
   self.assertEqual(vmx.read_bytes(),before)
 def test_repair_refuses_already_booted_installed_system(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,source,old,folder=self.repair_bundle(root);data['auto_install']['boot_original']=True;self.auto.fusion.mark(vmx.parent,data)
   with patch.object(self.auto.fusion,'off',side_effect=AssertionError('must stop first')):
    with self.assertRaisesRegex(RuntimeError,'BEFORE installation'):self.auto.repair_media(root)
 def test_repair_build_failure_preserves_configuration(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);vmx,data,source,old,folder=self.repair_bundle(root);before=vmx.read_bytes();manifest=(vmx.parent/'fusion-state.json').read_bytes()
   with patch.object(self.auto.fusion,'off'),patch.object(self.auto,'run',side_effect=self.extract_old_ks),patch.object(self.auto,'build_iso',side_effect=RuntimeError('build failed')):
    with self.assertRaisesRegex(RuntimeError,'build failed'):self.auto.repair_media(root)
   self.assertEqual(vmx.read_bytes(),before);self.assertEqual((vmx.parent/'fusion-state.json').read_bytes(),manifest)
 def guard_result(self,capacity='32212254720',signature='',disks='nvme0n1 disk',wrongmac=False):
  import os
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);bin=root/'bin';bin.mkdir();net=root/'net';net.mkdir();efi=root/'efi';efi.mkdir();device=root/'disk';device.touch()
   for name,mac in [('nat',self.data['mac0']),('lab',self.data['mac1'])]:
    folder=net/name;folder.mkdir();(folder/'address').write_text(('00:50:56:00:00:00' if wrongmac and name=='lab' else mac)+'\n')
   stubs={'uname':'echo aarch64','blockdev':'echo '+capacity,'wipefs':"printf '%s' '"+signature+"'",'lsblk':"if [[ $1 == -dnr ]]; then printf '%s\\n' '"+disks+"'; else echo disk; fi"}
   for name,body in stubs.items():
    path=bin/name;path.write_text('#!/bin/bash\n'+body+'\n');path.chmod(0o755)
   pre=re.search(r'%pre[^\n]*\n(.*?)\n%end',self.auto.kickstart(self.data,self.hash,self.hash),re.S)[1]
   pre=pre.replace('/sys/firmware/efi',str(efi)).replace('/sys/class/net',str(net)).replace('-b /dev/nvme0n1','-e '+str(device)).replace('/dev/nvme0n1',str(device))
   return subprocess.run(['bash'],input=pre,text=True,capture_output=True,env={**os.environ,'PATH':str(bin)+':'+os.environ['PATH']}).returncode
 def test_pre_guard_accepts_empty_expected_fixture(self):self.assertEqual(self.guard_result(),0)
 def test_pre_guard_refuses_existing_signature(self):self.assertNotEqual(self.guard_result(signature='PTTYPE gpt'),0)
 def test_pre_guard_refuses_wrong_capacity(self):self.assertNotEqual(self.guard_result(capacity='10737418240'),0)
 def test_pre_guard_refuses_extra_disk(self):self.assertNotEqual(self.guard_result(disks='nvme0n1 disk\nnvme0n2 disk'),0)
 def test_pre_guard_accepts_real_installer_zram_layout(self):
  self.assertEqual(self.guard_result(disks='loop0 loop\nsr0 rom\nzram0 disk\nnvme0n1 disk'),0)
 def test_pre_guard_still_refuses_extra_disk_with_zram(self):
  self.assertNotEqual(self.guard_result(disks='zram0 disk\nnvme0n1 disk\nnvme0n2 disk'),0)
 def test_pre_guard_refuses_unexpected_single_hardware_disk(self):
  self.assertNotEqual(self.guard_result(disks='zram0 disk\nsda disk'),0)
 def test_pre_guard_refuses_wrong_vm_mac(self):self.assertNotEqual(self.guard_result(wrongmac=True),0)


class SudoDenial(unittest.TestCase):
 def check_report(self,report,status):
  source=(ROOT/'RHCSA-Lab-Scripts/guest-golden.sh').read_text()
  function=source[source.index('sudo_denied() {'):source.index('# Do not remove arbitrary sudoers')]
  with tempfile.TemporaryDirectory() as directory:
   sudo=Path(directory)/'sudo'
   import shlex
   sudo.write_text('#!/bin/bash\nprintf %s '+shlex.quote(report)+'\nexit '+str(status)+'\n');sudo.chmod(0o700)
   result=subprocess.run(['bash','-c', 'PATH='+shlex.quote(directory)+':$PATH\n'+function+'\nsudo_denied student'],capture_output=True,text=True)
   return result.returncode
 def test_denied_zero_exit(self):
  self.assertEqual(self.check_report('User student is not allowed to run sudo on rhel10-golden.\n',0),0)
 def test_denied_nonzero_exit(self):
  self.assertEqual(self.check_report('User student is not allowed to run sudo on rhel10-golden.\n',1),0)
 def test_privileges_rejected(self):
  self.assertNotEqual(self.check_report('User student may run the following commands on host:\n (ALL) ALL\n',0),0)
 def test_query_error_rejected(self):
  self.assertNotEqual(self.check_report('sudo: unable to initialize policy plugin\n',1),0)
 def test_other_user_denial_rejected(self):
  self.assertNotEqual(self.check_report('User somebody is not allowed to run sudo on host.\n',0),0)

class SealRetry(unittest.TestCase):
 def test_missing_dbus_and_retry_keeps_original(self):
  source=(ROOT/'RHCSA-Lab-Scripts/guest-seal.sh').read_text()
  block=source[source.index('mkdir -p /var/lib/rhcsa-fusion'):source.index('ssh-keygen -lf')]
  with tempfile.TemporaryDirectory() as directory:
   base=Path(directory);(base/'etc').mkdir();(base/'etc/machine-id').write_text('original-id\n')
   block=block.replace('/var/lib/',str(base)+'/var/lib/').replace('/etc/machine-id',str(base)+'/etc/machine-id')
   for attempt in range(2):
    result=subprocess.run(['bash','-euc',block],capture_output=True,text=True)
    self.assertEqual(result.returncode,0,result.stderr)
    self.assertTrue((base/'var/lib/dbus').is_dir())
    self.assertEqual((base/'var/lib/rhcsa-fusion/golden-machine-id').read_text(),'original-id\n')
    (base/'etc/machine-id').write_text('')

def static():
 scripts=blocks=inner=0
 for path in ROOT.rglob('*.py'):ast.parse(path.read_text())
 for path in ROOT.rglob('*.sh'):
  p=subprocess.run(['bash','-n',str(path)],capture_output=True,text=True);assert p.returncode==0,(path,p.stderr);scripts+=1
 for path in ROOT.glob('*.md'):
  for code in re.findall(r'```(?:bash|sh)\n(.*?)\n```',path.read_text(),re.S):
   p=subprocess.run(['bash','-n'],input=code,text=True,capture_output=True);assert p.returncode==0,(path,p.stderr,code);blocks+=1
   for embedded in re.findall(r"<<'?EOF'?\n(#!/bin/bash\n.*?)\nEOF",code,re.S):
    p=subprocess.run(['bash','-n'],input=embedded,text=True,capture_output=True);assert p.returncode==0,(path,p.stderr);inner+=1
 print(f'Syntax: {scripts} shell files, {blocks} command blocks, {inner} embedded scripts. Guest execution NOT implied.')
class ExecutabilityReview(unittest.TestCase):
 def test_all_105_tasks_have_beginconditions(self):
  for ex in (1,2,3):
   for kind in ('opdrachten','antwoorden'):
    txt=(ROOT/f'Examen-{ex}-{kind}.md').read_text()
    self.assertEqual(txt.count('**Beginvoorwaarde:**'),35)
 def test_no_malformed_commands_or_missing_journal_filter(self):
  txt='\n'.join(p.read_text() for p in ROOT.glob('Examen-*-antwoorden.md'))
  for pattern in (r'^vi-[fc]',r'^-u ',r'^-l -U',r'_COMM=\s+[>]',r'reboot -h now'):
   self.assertIsNone(re.search(pattern,txt,re.M),pattern)
 def test_network_answers_do_not_ask_for_uuid(self):
  for ex,task in ((1,4),(2,4),(3,15)):
   txt=(ROOT/f'Examen-{ex}-antwoorden.md').read_text()
   sec=re.search(rf'\*\*T{task} —.*?(?=\n---|\Z)',txt,re.S).group()
   self.assertNotIn("read -r -p 'Host-only profile UUID",sec)
   self.assertEqual(sec.count('configure_lab()'),2)
 def network_case(self,profiles):
  txt=(ROOT/'Examen-1-antwoorden.md').read_text()
  function=re.search(r'configure_lab\(\) \{.*?^\}',txt,re.S|re.M).group()
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);log=d/'calls';fixture=d/'profiles';fixture.write_text(profiles)
   nm=d/'nmcli';nm.write_text('#!/bin/bash\nif [[ "$1" == -t ]]; then cat "$FIXTURE"; else printf "%s\n" "$*" >> "$LOG"; fi\n');nm.chmod(0o755)
   host=d/'hostnamectl';host.write_text('#!/bin/bash\nprintf "%s\n" "$*" >> "$LOG"\n');host.chmod(0o755)
   import os
   env=dict(os.environ,PATH=str(d)+':'+os.environ['PATH'],LOG=str(log),FIXTURE=str(fixture))
   result=subprocess.run(['/bin/bash','-c',function+'\nconfigure_lab'],env=env,capture_output=True,text=True)
   return result,log.read_text() if log.exists() else ''
 def test_network_selects_lab_not_nat(self):
  result,log=self.network_case('nat-uuid:fusion-nat\nlab-uuid:fusion-lab\n')
  self.assertEqual(result.returncode,0)
  self.assertIn('mod uuid lab-uuid',log)
  self.assertNotIn('nat-uuid',log)
 def test_network_rerun_uses_renamed_profile(self):
  result,log=self.network_case('nat-uuid:fusion-nat\nlab-uuid:lab-static\n')
  self.assertEqual(result.returncode,0)
  self.assertIn('up uuid lab-uuid',log)
 def test_network_duplicate_profiles_stop_before_change(self):
  result,log=self.network_case('one:fusion-lab\ntwo:lab-static\n')
  self.assertNotEqual(result.returncode,0)
  self.assertEqual(log,'')
 def test_network_missing_profile_stops_before_change(self):
  result,log=self.network_case('nat-uuid:fusion-nat\n')
  self.assertNotEqual(result.returncode,0)
  self.assertEqual(log,'')
 def test_web_permissions_override_login_umask(self):
  txt=(ROOT/'Examen-1-antwoorden.md').read_text()
  self.assertIn('chmod 755 /webtest',txt)
  self.assertIn('chmod 644 /webtest/index.html',txt)
 def test_reboot_ends_its_command_block(self):
  for p in ROOT.glob('Examen-*-antwoorden.md'):
   for block in re.findall(r'```bash\n(.*?)\n```',p.read_text(),re.S):
    if '\nreboot\n' in '\n'+block+'\n':
     self.assertEqual(block.splitlines()[-1],'reboot',p.name)

if __name__=='__main__':
 static();unittest.main(verbosity=2)
