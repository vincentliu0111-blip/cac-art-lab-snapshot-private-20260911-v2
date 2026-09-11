"""特征差异计算与缩略图处理，由 ReadData.py 调用。
输入来自已有真实数据；不要在这里重新生成画作数据。
"""


def feature_ranges(features):
    """返回 {特征名: 全部画作中该特征的最大值 - 最小值}，共 28 项。"""
    ranges = {}
    names = sorted(next(iter(features.values())))
    for name in names:
        values = []
        for painting in features.values():
            values.append(painting[name])
        ranges[name] = max(values) - min(values)
    return ranges


def top_differences(a, b, ranges, limit=3):
    """a/b 是两幅画的特征字典；返回 limit 条差异记录。
    每条包含 name、group、delta、scaled_delta。
    差值方向 A-B；按 abs(scaled_delta) 降序，绝对值相同按名字升序。
    """
    differences = []
    for name in sorted(a):
        delta = a[name] - b[name]
        if ranges[name] == 0:
            scaled_delta = 0.0
        else:
            scaled_delta = delta / ranges[name]
        differences.append({
            "name": name,
            "group": name.split("_")[0],
            "delta": delta,
            "scaled_delta": scaled_delta,
        })

    def difference_size(row):
        return abs(row["scaled_delta"])

    return sorted(differences, key=difference_size, reverse=True)[:limit]


def make_thumbnail(src, dst):
    """按比例生成长边不超过 400 像素的 RGB JPEG 缩略图。"""
    from PIL import Image
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as image:
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        image.convert("RGB").save(dst, "JPEG", quality=88)
