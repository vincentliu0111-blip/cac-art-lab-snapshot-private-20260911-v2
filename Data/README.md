# CAC 参赛 app · 数据包

这一包是**数据**，不含 app 代码。app 的每一行由 Vincent 自己写。

全部画作来自**大都会艺术博物馆开放获取接口**，均为**公有领域**（`isPublicDomain` 为真），可以公开展示。

---

## 一、包里有什么

| 文件 | 内容 | 条数 |
|---|---|---|
| `images/` | 画作图片，文件名 = `<object_id>.jpg`，长边约 600 像素 | 300 |
| `paintings.json` | 每幅画的基本信息 | 300 |
| `pairs.json` | 要拿来两两比较的画对 | 594 |
| `silver.json` | 每一对上，6 个 AI 裁判合成后的结论 | 594 |
| `predictions.json` | 每一对上，模型的预测 | 594 |
| `features.json` | 每幅画的 28 个画面特征 | 300 |
| `votes/` | 6 个裁判各自的原始投票 | 6 个文件 |
| `judge_weights.json` | 6 个裁判各自的权重 | 6 |

---

## 二、每个字段是什么意思

### paintings.json

一个数组，每条是一幅画。

| 字段 | 含义 |
|---|---|
| `object_id` | 博物馆藏品编号。**图片文件名就是它**，也是 `pairs.json` 里 A、B 引用的值 |
| `period` | 所属时期，三选一：`1300-1599` / `1600-1799` / `1800-1914` |
| `title` | 画名 |
| `artist` | 作者 |
| `date` | 创作年代（原文照录，形如 `ca. 1640–48`） |
| `begin_date` | 创作年代的起始年（整数） |
| `classification` | 藏品分类，全部为 `Paintings` |
| `width` / `height` | 图片像素宽高 |
| `bytes` | 图片字节数 |
| `file` | 图片文件名 |

🔴 **`title` 和 `artist` 不要显示在选画的界面上。** 整个研究的前提就是「只看画面」——
一旦让人看见作者和画名，他的选择就不再只受画面影响，你收上来的数据也就不能和裁判的比了。
这两个字段留在包里，是为了在**结果页**或分歧回顾时才用得上。

### pairs.json

| 字段 | 含义 |
|---|---|
| `pair_id` | 这一对的编号，16 位十六进制字符串。**其余所有文件都用它来对应** |
| `A` / `B` | 这一对里两幅画的 `object_id` |
| `period` | 这一对所属时期。**同一对里两幅画一定同时期** |

### silver.json —— 裁判的结论

| 字段 | 含义 |
|---|---|
| `pair_id` | 对应 `pairs.json` |
| `q_A` | **裁判加权之后，A 更美的概率**。0 到 1 之间的小数 |
| `n_judges` | 参与这一对的裁判数，全部为 6 |

**`q_A` 怎么读**：

- `q_A = 0.83` → 裁判们比较一致地更看好 **A**
- `q_A = 0.17` → 比较一致地更看好 **B**
- `q_A = 0.52` → **裁判们自己都拿不准**，这一对是分歧对

🔴 **不要把它直接压成「裁判选了 A」这么一句话。** 这个数的大小本身就是信息 ——
`0.51` 和 `0.97` 在界面上应该看得出区别。

### predictions.json —— 模型的预测

| 字段 | 含义 |
|---|---|
| `pair_id` | 对应 `pairs.json` |
| `model_q_A` | **模型预测 A 更美的概率**，0 到 1 之间 |

模型只看画面算出来的数，从来没看过裁判在这 594 对上的票（这 300 幅画一幅都没参与过训练）。

**它的成绩**：把 `model_q_A > 0.5` 当作「模型选 A」，和 `q_A > 0.5` 那一边比，
**594 对里对了 462 对，77.8%**（瞎猜是 50%）。这个数可以直接写进 app 和视频里。

### features.json —— 28 个画面特征

一个字典，键是 `object_id` 的字符串形式，值是那幅画的 28 个特征。
特征名的前缀就是它所属的组：

**`O_` 秩序（8 个）** —— 画面组织得好不好

| 特征名 | 含义 |
|---|---|
| `O_symmetry_lr` / `O_symmetry_tb` | 左右 / 上下对称程度 |
| `O_balance_lr` / `O_balance_tb` | 左右 / 上下的视觉重量是否均衡 |
| `O_centrality` | 视觉重心是否靠近画面中心 |
| `O_rule_of_thirds` | 主要内容是否落在三分线上 |
| `O_edge_orient_concentration` | 线条方向集不集中（越集中越规整） |
| `O_hue_dominant_share` | 主色调占了多大比例（色系统一程度） |

**`R_` 丰富（8 个）** —— 画面内容多不多

| 特征名 | 含义 |
|---|---|
| `R_color_count` | 颜色数量 |
| `R_hue_entropy` | 色相的杂乱程度 |
| `R_saturation_mean` | 平均饱和度 |
| `R_brightness_std` | 明暗变化幅度 |
| `R_edge_density` | 边缘密度（线条多不多） |
| `R_texture_roughness` | 纹理粗糙度 |
| `R_local_entropy` | 局部信息量 |
| `R_high_freq_ratio` | 高频成分占比（细节多不多） |

**`N_` 暂未归类（12 个）** —— 既不明确属于秩序、也不明确属于丰富

`N_aspect_ratio` 长宽比 · `N_log_pixels` 像素量的对数 · `N_bytes_per_pixel` 每像素字节数 ·
`N_sharpness` 清晰度 · `N_brightness_mean` 平均亮度 · `N_contrast_p95_p05` 对比度 ·
`N_dark_ratio` / `N_bright_ratio` 暗部 / 亮部占比 · `N_grayscale_ratio` 接近灰度的程度 ·
`N_mean_r` / `N_mean_g` / `N_mean_b` 三通道平均值

🔴 **`N_` 这一组要小心。** 里面混着两类不同性质的东西：一类是画面上还没归好类的性质，
另一类其实是**博物馆拍照和存档留下的痕迹**（清晰度、每像素字节数、长宽比都属于后者）。
在「为什么」面板里，**优先展示 `O_` 和 `R_` 的差异**；`N_` 的差异不适合说成「这幅画因此更美」。

**取值范围**：绝大多数特征已归一到 0–1，个别（如 `N_log_pixels`、`R_color_count`）不在这个区间。
**比较两幅画时用差值，不要直接比绝对值** —— 不同特征的量纲不一样。

### votes/ —— 6 个裁判的原始票

每个文件是一个裁判，结构：

| 字段 | 含义 |
|---|---|
| `judge_id` | 裁判编号，如 `OAI_SOL_M` |
| `vendor` / `model` / `effort` | 厂商 / 模型 / 推理强度 |
| `prompt` | 问它的那句话（所有裁判完全相同） |
| `votes` | 数组，每条 = `{pair_id, presentation, choice}` |

`presentation` 有两种：`normal` = 正常摆放；`swapped` = **把 A、B 左右调换后再问一次**。
`choice` 是 `"A"` 或 `"B"`，**指的是它当时看到的左右位置**。

🔴 **为什么要交换着问两遍**：实测发现同一个裁判重复问几乎不改口，但把两幅画左右一换，
**约有两成会改选另一幅** —— 这是位置偏差的实锤。`silver.json` 里的 `q_A` 就是把这件事算进去之后的结果。

### judge_weights.json

字典，键是裁判编号，值是它在合成 `q_A` 时的权重（6 个加起来为 1）。
权重按各裁判自身的一致性给：越自洽的裁判权重越高。

---

## 三、动手之前先自己核一遍

打开终端，在这个文件夹里跑（这几行不算作业，是确认包没缺东西）：

```bash
python3 -c "import json;print(len(json.load(open('pairs.json'))))"        # 应输出 594
python3 -c "import json;print(len(json.load(open('paintings.json'))))"    # 应输出 300
ls images | wc -l                                                        # 应输出 300
```

再确认三件事对得上：

1. `pairs.json` 里出现的每个 `A`、`B`，在 `images/` 里都能找到对应的 jpg；
2. `pairs.json`、`silver.json`、`predictions.json` 三个文件的 `pair_id` 集合完全一样；
3. `features.json` 的键，和 `paintings.json` 里的 `object_id` 一一对应。

**这三条如果有一条对不上，先反馈，不要绕过去。**

---

## 四、许可与出处

- 图片：大都会艺术博物馆 Open Access，公有领域，可在公开网页展示。app 的 README 里要注明出处。
- 裁判票、特征值、模型预测：本项目自行产出，供本 app 使用。
- 🔴 提交材料里要写清楚：**这份数据来自一项已完成的研究，app 是在它之上做的**。这一条如实写，不会扣分。
