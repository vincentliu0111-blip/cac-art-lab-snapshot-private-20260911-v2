"""M1 数据与缩略图验收。Mac：在仓库根目录执行 python tools/check_m1.py。
读取 Data/ 与 web/，通过后写 verification.txt。
按 N 保存一次输出指纹，第二次通过才确认同设置重复输出一致。
"""
import hashlib
import json
import math
import platform
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def read(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def main():
    try:
        from PIL import Image
    except ImportError:
        raise ValueError("缺少 Pillow：先激活 .venv，再执行 python -m pip install Pillow")
    data = ROOT / "Data"
    result_file = ROOT / "web" / "app_data.json"
    rows = read(result_file)
    require(isinstance(rows, list), "app_data.json 最外层应是 list")
    n = len(rows)
    require(n in (40, 60), "请先生成 40 或 60 条结果")
    pairs = read(data / "pairs.json")
    silver = {r["pair_id"]: r["q_A"] for r in read(data / "silver.json")}
    pred = {r["pair_id"]: r["model_q_A"] for r in read(data / "predictions.json")}
    art = {r["object_id"]: r for r in read(data / "paintings.json")}
    features = read(data / "features.json")
    expected = random.Random(7).sample(sorted(pairs, key=lambda r:r["pair_id"]), n)
    require([r["pair_id"] for r in rows] == [r["pair_id"] for r in expected],
            "编号/顺序不符合按 pair_id 排序后 seed=7 抽样；检查是否循环 selected，且每轮更新 pid")
    names = sorted(next(iter(features.values())))
    spans = {}
    for name in names:
        vals = [f[name] for f in features.values()]
        spans[name] = max(vals) - min(vals)
    referenced = set()
    for row, pair in zip(rows, expected):
        pid = pair["pair_id"]
        require(row["q_A"] == silver[pid], f"{pid}: q_A 与源数据不一致")
        require(row["model_q_A"] == pred[pid], f"{pid}: model_q_A 与源数据不一致")
        for side in ("A", "B"):
            filename = art[pair[side]]["file"]
            require(row[f"img_{side}"] == filename, f"{pid}: img_{side} 文件名或顺序错误")
            referenced.add(filename)
        a, b = features[str(pair["A"])], features[str(pair["B"])]
        delta = {k:a[k]-b[k] for k in names}
        scaled = {k:delta[k]/spans[k] if spans[k] else 0.0 for k in names}
        ranked = sorted(names, key=lambda k:(-abs(scaled[k]), k))[:3]
        top = row["top_features"]
        require(len(top) == 3, f"{pid}: top_features 必须有 3 条")
        require([t["name"] for t in top] == ranked, f"{pid}: top 3 排序或尺度处理错误")
        for t in top:
            k = t["name"]
            require(t["group"] == k.split("_", 1)[0], f"{pid}: 特征组名错误")
            require(math.isclose(t["delta"], delta[k], abs_tol=1e-6), f"{pid}: delta 应为 A-B")
            require(math.isclose(t["scaled_delta"], scaled[k], abs_tol=1e-6), f"{pid}: scaled_delta 错误")
    fingerprint = hashlib.sha256(result_file.read_bytes())
    for name in sorted(referenced):
        path = ROOT / "web" / "img" / name
        with Image.open(path) as im, Image.open(data / "images" / name) as original:
            require(im.format == "JPEG", f"{name}: 应导出为 JPEG")
            w, h = im.size
            sw, sh = original.size
            require(max(w, h) <= 400, f"{name}: 长边超过 400")
            target_scale = min(400 / sw, 400 / sh, 1)
            require(abs(w - sw * target_scale) <= 1.5 and abs(h - sh * target_scale) <= 1.5,
                    f"{name}: 未按原比例生成约 400 px 缩略图")
        fingerprint.update(name.encode())
        fingerprint.update(path.read_bytes())
    close = sum(.4 <= row["q_A"] <= .6 for row in rows)
    known = {60:(5,106), 40:(3,75)}
    require((close,len(referenced)) == known[n], "区间统计或图片引用数不符")
    cache = ROOT / ".homework_check.json"
    history = read(cache) if cache.exists() else {}
    key = f"N={n},seed=7,Python={platform.python_version()}"
    digest = fingerprint.hexdigest()
    previous = history.get(key)
    require(previous is None or previous == digest,
            "相同 N 的 JSON/图片与上次检查不同。若刚修正代码，可删除仓库根目录 .homework_check.json，再重新做两次验收")
    history[key] = digest
    cache.write_text(json.dumps(history, indent=2), encoding="utf-8")
    message = (f"PASS N={n}: 区间内={close}; 引用图片={len(referenced)}; "
               "字段关联/top3/缩略图=通过; " +
               ("复现=通过" if previous else "复现=待验证，请重跑 ReadData.py 后再运行本检查"))
    print(message)
    if previous:
        report = ROOT / "verification.txt"
        text = report.read_text(encoding="utf-8") if report.exists() else "M1 验收记录\n"
        text += f"{message}\nPython={platform.python_version()}\nSHA256={digest}\n"
        report.write_text(text, encoding="utf-8")
        print("已记录到 verification.txt")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, IndexError, StopIteration) as exc:
        print(f"FAIL: {exc}")
        print("请检查对应文件/字段；本脚本不修改 Data 或 web。")
        sys.exit(1)
