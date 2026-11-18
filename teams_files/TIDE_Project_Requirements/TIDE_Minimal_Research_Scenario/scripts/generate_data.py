"""Create new synthetic starter fixtures; does not start any project services."""
from pathlib import Path
import csv,random,math,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
def one(path,seed,offset):
    rng=random.Random(seed);temp=24.0+offset
    start=datetime.datetime(2026,1,1,tzinfo=datetime.timezone.utc)
    with path.open('w',encoding='utf-8',newline='') as f:
        out=csv.writer(f,lineterminator='\n')
        out.writerow(['timestamp','control_input','flow_rate','temperature','target_temp'])
        for i in range(2400):
            control=0.5+0.25*math.sin(i/31)+rng.uniform(-.05,.05)
            flow=8+offset+math.sin(i/19)+rng.uniform(-.2,.2)
            next_temp=.88*temp+2*control+.08*flow+1.2+offset*.05+rng.gauss(0,.1)
            stamp=(start+datetime.timedelta(minutes=i)).isoformat().replace('+00:00','Z')
            out.writerow([stamp,f'{control:.6f}', '' if i%97==0 else f'{flow:.6f}',f'{temp:.6f}',f'{next_temp:.6f}'])
            temp=next_temp
    return {'path':path.relative_to(ROOT).as_posix(),'rows':2400,'seed':seed,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'synthetic':True}
def main():
    (DATA/'restricted').mkdir(parents=True,exist_ok=True)
    values=[one(DATA/'p1-process.csv',1101,0),one(DATA/'restricted/p2-process.csv',2202,1.5)]
    obj={'generator_version':'1.0.0','record_count_each':2400,'artifacts':values}
    (DATA/'data-manifest.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Generated P1/P2 synthetic inputs. Regeneration after edits requires refreshing metadata checksums.')
if __name__=='__main__':main()
