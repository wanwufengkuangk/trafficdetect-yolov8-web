from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image, ImageOps, ImageDraw

outdir = Path(r"C:\Users\89657\Desktop\yolov8\paper_assets")
outdir.mkdir(parents=True, exist_ok=True)
font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")
bold_font = FontProperties(fname=r"C:\Windows\Fonts\msyhbd.ttc")

# Figure 1: system architecture
fig, ax = plt.subplots(figsize=(12, 4.8), dpi=180)
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.8)
ax.axis('off')
boxes = [
    (0.4, 1.6, 2.0, 1.2, '原始数据与标注\nBDD100K / 标注文件', '#d8eefe'),
    (3.0, 1.6, 2.2, 1.2, '数据转换与校验\nYOLO格式重建', '#dff5e1'),
    (5.8, 1.6, 2.2, 1.2, '模型训练与验证\nYOLOv8s改进变体', '#fff0cc'),
    (8.6, 1.6, 1.9, 1.2, '后端推理服务\nFastAPI', '#f7dfef'),
    (10.8, 1.6, 0.8, 1.2, '前端展示\nWeb', '#efe9ff'),
]
for x, y, w, h, t, c in boxes:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03,rounding_size=0.08', facecolor=c, edgecolor='#444', linewidth=1.4))
    ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=10, fontproperties=font)
for i in range(len(boxes) - 1):
    x1 = boxes[i][0] + boxes[i][2]
    x2 = boxes[i + 1][0]
    ax.add_patch(FancyArrowPatch((x1 + 0.1, 2.2), (x2 - 0.1, 2.2), arrowstyle='-|>', mutation_scale=14, linewidth=1.5, color='#555'))
ax.text(6, 4.35, 'TrafficDetect 系统总体架构图', ha='center', fontsize=14, fontproperties=bold_font)
ax.text(6, 0.75, '统一配置驱动数据处理、模型训练、服务推理与网页展示闭环', ha='center', fontsize=9, color='#444', fontproperties=font)
fig.tight_layout()
fig.savefig(outdir / 'system_architecture.png', bbox_inches='tight')
plt.close(fig)

# Figure 2: model architecture
fig, ax = plt.subplots(figsize=(12, 5.2), dpi=180)
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.2)
ax.axis('off')
ax.text(6, 4.8, '改进 YOLOv8s 结构示意图', ha='center', fontsize=14, fontproperties=bold_font)
parts = [
    (0.6, 2.0, 1.8, 1.0, '输入图像\n640×640', '#d8eefe'),
    (2.8, 2.0, 2.0, 1.0, 'Backbone\nYOLOv8s', '#fff0cc'),
    (5.2, 2.0, 2.0, 1.0, 'Neck / FPN-PAN\n特征融合', '#dff5e1'),
    (7.6, 2.0, 1.8, 1.0, 'Detect Head\nP3/P4/P5', '#f7dfef'),
    (9.8, 2.0, 1.6, 1.0, '输出结果\nBoxes + Scores', '#efe9ff'),
]
for x, y, w, h, t, c in parts:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03,rounding_size=0.08', facecolor=c, edgecolor='#444', linewidth=1.4))
    ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=10, fontproperties=font)
for i in range(len(parts) - 1):
    ax.add_patch(FancyArrowPatch((parts[i][0] + parts[i][2] + 0.08, 2.5), (parts[i + 1][0] - 0.08, 2.5), arrowstyle='-|>', mutation_scale=14, linewidth=1.5, color='#555'))
adds = [
    (2.95, 3.45, 1.7, 0.75, 'CBAM 模块\n骨干关键阶段', '#ffd9c7'),
    (7.65, 3.45, 1.7, 0.75, '新增 P2 检测分支\n高分辨率小目标', '#cfe8ff'),
    (5.35, 0.75, 1.7, 0.75, 'WIoU 损失\n边框回归优化', '#ffe7a8'),
]
for x, y, w, h, t, c in adds:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03,rounding_size=0.08', facecolor=c, edgecolor='#b05a2b', linewidth=1.3, linestyle='--'))
    ax.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=9.5, fontproperties=font)
ax.add_patch(FancyArrowPatch((3.8, 3.45), (3.8, 3.03), arrowstyle='-|>', mutation_scale=12, linewidth=1.3, color='#b05a2b'))
ax.add_patch(FancyArrowPatch((8.5, 3.45), (8.5, 3.03), arrowstyle='-|>', mutation_scale=12, linewidth=1.3, color='#b05a2b'))
ax.add_patch(FancyArrowPatch((6.2, 1.5), (6.2, 1.98), arrowstyle='-|>', mutation_scale=12, linewidth=1.3, color='#b05a2b'))
ax.text(6, 0.25, '相较于标准 YOLOv8s，本文主要增加 P2 分支、CBAM 注意力与 WIoU 回归损失', ha='center', fontsize=9, color='#444', fontproperties=font)
fig.tight_layout()
fig.savefig(outdir / 'model_architecture.png', bbox_inches='tight')
plt.close(fig)

# Figure 4: detection examples montage
paths = [
    Path(r"C:\Users\89657\Desktop\yolov8\result\train_bdd_full\val_batch0_pred.jpg"),
    Path(r"C:\Users\89657\Desktop\yolov8\result\train_bdd_full\val_batch1_pred.jpg"),
    Path(r"C:\Users\89657\Desktop\yolov8\result\train_bdd_full\val_batch2_pred.jpg"),
]
ims = []
for p in paths:
    im = Image.open(p).convert('RGB')
    im = ImageOps.contain(im, (880, 280))
    canvas = Image.new('RGB', (900, 320), 'white')
    canvas.paste(im, ((900 - im.width) // 2, 20))
    d = ImageDraw.Draw(canvas)
    d.text((20, 290), p.stem, fill=(30, 30, 30))
    ims.append(canvas)
montage = Image.new('RGB', (900, 320 * len(ims)), '#f5f5f5')
for i, im in enumerate(ims):
    montage.paste(im, (0, 320 * i))
montage.save(outdir / 'detection_examples.png')

for name in ['system_architecture.png', 'model_architecture.png', 'detection_examples.png']:
    p = outdir / name
    print(p)
    print(p.stat().st_size)
