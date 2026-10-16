#!/usr/bin/env python3
"""Read-only evidence checks. Not an exam score. No command shell/eval or repairs."""
import argparse,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def match(output,kind,expected):
    if kind=='equal':return output.strip()==str(expected)
    if kind=='line':return str(expected) in output.splitlines()
    if kind=='token':return str(expected) in output.split()
    if kind=='json-address':
        return any(a.get('local')==expected for nic in json.loads(output) for a in nic.get('addr_info',[]))
    if kind=='swap':
        rows=json.loads(output).get('swapdevices',[])
        return any(row.get('name')==expected['name'] and int(row.get('prio',-999))==expected['prio'] for row in rows)
    if kind=='numeric':return float(output.strip())==float(expected)
    if kind=='module':return any(line.split() and line.split()[0]==expected for line in output.splitlines())
    if kind=='same-inode':
        rows=output.splitlines();return len(rows)==2 and rows[0]==rows[1]
    if kind=='nonempty':return bool(output.strip())
    raise ValueError('Unknown matcher '+kind)

def execute(check):
    try:
        p=subprocess.run(check['argv'],capture_output=True,text=True,timeout=60,env={**os.environ,'LC_ALL':'C'})
        if p.returncode not in check.get('valid_rc',[0]):
            return 'ERROR',f"exit {p.returncode}: {p.stderr.strip() or p.stdout.strip()}"
        good=match(p.stdout,check['match'],check.get('expected'))
        return ('PASS' if good else 'FAIL'),p.stdout.strip()[:700]
    except (OSError,subprocess.TimeoutExpired,ValueError,TypeError) as e:return 'ERROR',str(e)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exam',type=int,choices=[1,2,3],required=True)
    p.add_argument('--node',required=True)
    p.add_argument('--json',action='store_true')
    args=p.parse_args()
    spec=json.loads((ROOT/'tools/checks.json').read_text())
    if args.node not in spec[str(args.exam)]:p.error('Wrong node for exam')
    if os.geteuid()!=0:p.error('Run as root inside the Linux guest')
    name=subprocess.run(['hostname','-s'],capture_output=True,text=True,check=True).stdout.strip()
    if name not in [args.node,'rhel10-'+args.node]:p.error('Guest hostname does not match --node')
    results=[]
    for task in spec[str(args.exam)][args.node]:
        outcomes=[]
        for check in task['checks']:
            status,detail=execute(check)
            outcomes.append(dict(status=status,label=check['label'],detail=detail))
        # Every task has manual subcriteria; never claim full PASS from spot checks.
        status='ERROR' if any(x['status']=='ERROR' for x in outcomes) else ('FAIL' if any(x['status']=='FAIL' for x in outcomes) else 'MANUAL')
        results.append(dict(task=task['task'],status=status,checks=outcomes,manual=task['manual']))
    if args.json:print(json.dumps(results,indent=2))
    else:
        for result in results:
            print(f"T{result['task']:02d}: {result['status']}")
            for c in result['checks']:print('  '+c['status']+' '+c['label']+' — '+c['detail'])
            print('  MANUAL '+result['manual'])
        print('No exam score. Complete manual checks, reboot checks and peer tests separately.')
    return 2 if any(x['status']=='ERROR' for x in results) else (1 if any(x['status']=='FAIL' for x in results) else 0)
if __name__=='__main__':sys.exit(main())
