# 项目部署说明

## 1. 部署目标

本说明用于在 Windows 上创建一个新的 Conda 环境并部署当前项目，使其达到以下状态：

- 可以启动 PyQt5 桌面界面
- 可以加载 `models/best.pt`
- 可以进行图片、视频和摄像头推理

当前说明只覆盖推理部署，不覆盖训练链路修复。仓库内的训练脚本和数据集配置路径目前并不匹配当前目录结构。

## 2. 推荐环境

- 操作系统：Windows
- Python：3.10
- Conda 环境名：`yolov8`
- GPU：NVIDIA GPU
- PyTorch：CUDA 12.8 对应轮子

## 3. 创建环境

```powershell
conda create -n yolov8 python=3.10 -y
conda activate yolov8
```

## 4. 安装依赖

先安装 GPU 版 PyTorch：

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

再安装项目依赖：

```powershell
pip install ultralytics PyQt5==5.15.9 opencv-python pillow numpy matplotlib pandas pyyaml dill
```

如果你希望直接按本次验证通过的版本安装，也可以使用：

```powershell
pip install -r requirements.txt
```

说明：

- `dill` 是当前 `models/best.pt` 成功加载所需的额外依赖，缺少时主程序会在模型加载阶段报错。
- `requirements.txt` 记录的是当前机器上已经验证通过的一组版本。

## 5. 启动项目

进入项目目录并启动：

```powershell
conda activate yolov8
cd C:\Users\89657\Desktop\yolov8
python MainProgram.py
```

## 6. 部署后检查

建议按下面顺序检查：

### 6.1 环境检查

```powershell
python --version
python -c "import torch; print('torch:', torch.__version__); print('cuda:', torch.cuda.is_available()); print('gpu:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
python -c "from ultralytics import YOLO; print('ultralytics ok')"
python -c "from PyQt5 import QtWidgets; print('PyQt5 ok')"
python -c "import cv2, PIL, numpy; print('opencv/pillow/numpy ok')"
```

### 6.2 资源检查

```powershell
python -c "import os; print('MainProgram.py', os.path.exists('MainProgram.py')); print('model', os.path.exists('models/best.pt')); print('font', os.path.exists('Font/platech.ttf')); print('css', os.path.exists('UIProgram/style.css')); print('bg', os.path.exists('UIProgram/ui_imgs/bg22.png'))"
```

### 6.3 功能检查

- 启动后点击“打开图片”
- 优先选择一个示例图片进行推理
- 确认界面能显示检测结果、类别、置信度、坐标和目标数
- 测试“保存”按钮是否能正常输出结果文件到 `save_data`

## 7. 本次实际验证结果

本仓库已在 `yolov8` 环境下完成以下验证：

- Python 版本：`3.10.20`
- PyTorch 版本：`2.11.0+cu128`
- CUDA 可用：`True`
- GPU 识别成功：`NVIDIA GeForce RTX 2050`
- `ultralytics`、`PyQt5`、`opencv-python` 可正常导入
- 主程序模块可以正常导入
- 主窗口可以成功启动
- 已脚本化完成一次单图检测
- 已生成验证输出文件：`save_data/verify_detect_result.jpg`

## 8. 常见问题

### 8.1 模型加载时报 `No module named 'dill'`

安装：

```powershell
pip install dill
```

### 8.2 `torch.cuda.is_available()` 为 `False`

优先检查：

- 是否装成了 CPU 版 PyTorch
- 显卡驱动是否正常
- 当前环境是否确实使用了 `yolov8`

### 8.3 训练跑不通

这不属于本部署文档的范围。当前仓库里的训练配置路径与实际仓库路径不一致，需要单独修正后才能训练。
