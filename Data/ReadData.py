import json 
from pathlib import Path
import random
from m1_tasks import feature_ranges, top_differences, make_thumbnail
BASE=Path(__file__).resolve().parent
WEB=BASE.parent/"web"
IMG_OUT=WEB/"img"
IMG_OUT.mkdir(parents=True,exist_ok=True)
print(BASE)
print(WEB)
def read_json(name):
    with(BASE/name).open(encoding="utf-8")as f:
        return json.load(f)
silver=read_json("silver.json")
pairs=read_json("pairs.json")
predictions=read_json("predictions.json")
paintings=read_json("paintings.json")
features=read_json("features.json")
judge_weights=read_json("judge_weights.json")
def index_by(rows,field):
    result={}
    for row in rows:
        result[row[field]]=row
    return result
silver_by_id=index_by(silver,"pair_id")
painting_by_id=index_by(paintings,"object_id")
pred_by_id=index_by(predictions,"pair_id")



def get_pair_id(pair):
    return pair["pair_id"]
ordered=sorted(pairs,key=get_pair_id)
rng=random.Random(7)
N=60
selected=rng.sample(ordered,N)
print(selected[0])
ranges=feature_ranges(features)
print(len(ranges))
used_files=set()
output=[]
for pair in selected:
    pid=pair["pair_id"]
    A=painting_by_id[pair["A"]]
    B=painting_by_id[pair["B"]]
    fa=features[str(pair["A"])]
    fb=features[str(pair["B"])]
    top=top_differences(fa,fb,ranges)
    used_files.add(A["file"])
    used_files.add(B["file"])
    output.append({
        "pair_id":pid,
        "img_A":A["file"],
        "img_B":B["file"],
        "q_A":silver_by_id[pid]["q_A"],
        "model_q_A":pred_by_id[pid]["model_q_A"],
        "top_features":top,
    })

for filename in sorted(used_files):
    make_thumbnail(BASE/"images"/filename,IMG_OUT/filename)
print(len(used_files))

with (WEB/"app_data.json").open("w",encoding="utf-8") as f:
    json.dump(output,f,ensure_ascii=False,indent=2)

print(len(output))

count=0
for obj in output:
    if 0.4<=obj["q_A"]<=0.6:
        count+=1
print(count)
