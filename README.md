# BERET · 贝雷帽女孩 / AirPods Pro 3

基于用户提供的正、侧、背三视图进行的风格化三维重建。分为**头部下壳**和**独立贝雷帽上盖**，上盖固定到原充电盒上盖，借用原盒铰链开启。网页加载的就是交付 STL，没有另用展示用的假模型。

**版本状态：V1.0 打印试配原型，未做实物装配。** 保留参考的帽型、圆扣、大眼睛、刘海与发梢，但三张图片无法给出完整曲面，当前模型是可修改的风格化重建，并非逐面扫描复刻。

## 文件

| 文件 | 用途 |
| --- | --- |
| `models/lower-shell.stl` | 头部下壳；Z=0 附近朝下，单位 mm |
| `models/beret-lid-print.stl` | 独立帽盖；已经平移到 Z=0，开口朝下 |
| `models/beret-lid.stl` | 帽盖的装配坐标版本，用于网页和装配查看 |
| `models/fit-ring.stl` | 5 mm 高的内腔试配环，正式打印前先试装 |
| `models/device-envelope.stl` | 设备近似尺寸包络；仅供检查，**不要当作耳机打印件** |
| `models/beret-studio.blend` | Blender 场景，含灯光、材质及开盖姿态 |
| `docs/design-sheet.pdf` / `.svg` | A3 尺寸设计图，外轮廓投影来自 STL |
| `docs/mesh-validation.json` | 网格与离散开盖碰撞检查结果 |
| `scripts/build_model.py` | 参数化建模与 STL 导出源文件 |
| `scripts/drawings.py` / `render.py` | 图纸与实物网格渲染脚本 |
| `index.html` / `viewer.js` / `style.css` | 无构建步骤的静态展示网站 |

STL 本身不储存单位。导入切片软件后选择 **mm**，缩放 **100%**。不要为了调松紧整体缩放角色，应修改内腔参数。

## 尺寸依据与假设

来源：[Apple 官方规格](https://www.apple.com/airpods-pro/specs/) 与 [MagSafe Charging Case for AirPods Pro 3 结构尺寸图](https://developer.apple.com/download/files/accessories/dimensional-drawings/magsafe-charging-case-for-airpods-pro-3.pdf)。后者为 2025-09-09 版，详细名义外包络为 **宽 62.22 × 高 47.22 × 厚 21.84 mm**（产品规格页四舍五入到 62.2 × 47.2 × 21.8 mm）。

- 默认单边余量 **0.30 mm**，内腔包络为 **62.82 × 47.82 × 22.44 mm**。这是首样起点，不代表所有打印机或材料均适配。
- 外壳总包络约 **83.68 W × 64.99 H × 42.88 D mm**，以生成图纸和验证 JSON 为准。发型与帽型导致厚度明显大于裸盒。
- 分缝 **0.60 mm**；设备底部位于模型 Z=3 mm；设备分缝自其底部 **32.50 mm**，属于根据官方图形比例设定的近似，需实测。
- 内腔使用 **R10.5 mm 圆角长方体近似**，并为下壳增加向上插入的直通截面。官方外形包含变化曲率，不能仅凭三项外包络保证贴合；试配环只验证中部截面，完整首样还要检查底角、上盖角与插入路径。
- 网页开盖轴 `[0, 9.7, 35.5] mm` 是运动演示近似。它不是实测铰链轴，不应当据此加工新铰链。0–115° 每 2.5° 的采样碰撞检查只针对这两个数字壳体，不构成实物开盖行程保证。
- 主后侧避让宽 51 mm，叠加帽盖离散扫掠修形；USB-C 底孔 14 × 8 mm；扬声器区域及另一底部声孔留开口；正面指示灯 Ø3.6 mm；右侧采用较大的通窗开放挂绳区域。孔位须对照实物复核。
- 为保持五官，正面未开大面积触控窗口。**触控配对可能需要取下保护壳**；不要假设 TPU 或 PLA 一定能透传触控。指示灯通孔并不是触控窗口。
- 帽盖外形较大，充电盒盖的自保持能力和装配胶片强度需要首样测试；未在两壳间加入跨缝卡扣、磁铁或新的转轴。

## 打印与装配

1. **先打印试配环。** 建议 TPU 95A，0.4 mm 喷嘴、0.16–0.20 mm 层高。确保环可以平稳经过盒体中部，既不挤压设备也不会直接滑脱。间隙过紧时每次将单边余量增加 0.05–0.10 mm，再生成试配环。
2. **再打印完整首样。** 下壳底朝下，帽盖使用 `beret-lid-print.stl` 开口朝下。切片中检查帽顶内侧、眼睛、耳朵、帽檐和发梢的悬垂并布置支撑。TPU 的同材支撑较难拆，优先手动涂抹、限制接触面积；有多材料设备可用兼容支撑材料。PLA/PETG 可用于外观样，但刚性材料应先增大间隙，不能强压套入。
3. 建议 3–4 道壁线；0.8–1.0 mm 顶底厚度；可从 10–15% 填充开始。实体几何中较厚的帽冠和发型会由切片填充处理，不需要 100% 填充。所有设置以切片预览和打印机能力为准。
4. 清理支撑、毛刺与通孔。试装时慢慢插入原充电盒，不要强推，发现应力、刮擦或底角卡住即退出调整。
5. 下壳贴合下半盒，帽盖单独贴合原上盖。可在帽盖内顶放 **约 0.3 mm 厚的可移除胶片/软垫**，厚度应与实际余量共同校准。先测试胶片对设备表面是否易清理；不要使用瞬干胶，也不要让胶片跨过分缝或进入原盒铰链。
6. 手动慢开帽盖，确认随原上盖运动、不会带出下壳或碰到后发束。出现干涉时减小行程，修正后侧避让和轴位参数，不能直接用力打开。
7. 用实际线缆检查 USB 插头外壳是否能进入底孔；检查声音、LED 可见性、挂绳与前部触控。如配对不可靠，取下外壳配对。
8. 当前保留厚发型背面，**默认拆壳无线充电**。没有验证带壳的 Qi、MagSafe 或 Apple Watch 充电效果；如要支持带壳无线充电，需要另开背部窗口并重新验证。

不把胶片计入模型一体结构；需要用户在装配时另备。模型为装饰保护套，不替代充电盒自身结构。

## 修改参数与重新生成

Python 3.12 环境：

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_model.py --clearance 0.30
.venv/bin/python scripts/drawings.py
inkscape docs/design-sheet.svg --export-type=pdf --export-filename=docs/design-sheet.pdf
blender -b -t 8 --python scripts/render.py
python scripts/package.py
```

Windows 的虚拟环境命令使用 `.venv/Scripts/python.exe`。Inkscape 和 Blender 为可选的图纸 PDF / 渲染工具；生成 STL 不依赖它们。

可调参数：`--width`、`--depth`、`--height`、`--seam-height` 与 `--clearance`。它们修改功能内腔，不自动重塑角色外观。大幅增加内腔尺寸会削弱壁厚或破坏局部连接；每次修改必须重做网格验证、图纸与完整试样。渲染脚本会读取 `assets/parameters.json` 中的转轴；重新生成后不要沿用旧图。

## 查看网页

网页使用本地 vendored Three.js，不请求 CDN、字体或外部模型。需要通过 HTTP 打开，以便浏览器读取 ES Modules、参数与 STL：

```sh
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

页面支持拖动旋转、缩放、正侧背视角、0–115° 帽盖角度、分件、翻转内腔和三种展示配色。配色只改变渲染材质，STL 是单体网格，未提供分色插片。WebGL 不可用时回退为实际模型渲染图，下载功能继续可用。

## GitHub Pages

文件使用相对路径，适用于 `https://用户名.github.io/仓库名/`，不需要改 base URL。

1. 把本文件夹提交到目标 GitHub 仓库的 `main` 或 `master` 分支。
2. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
3. 已附 `.github/workflows/pages.yml`，推送后自动打包静态文件并部署，也可手动运行 `Deploy GitHub Pages`。首次 Pages 部署须由仓库管理员完成上述设置。
4. 如果不使用 Actions，可在 Pages 中选择 **Deploy from a branch → main / (root)**，根目录已经有 `index.html` 和 `.nojekyll`。

仓库已包含 Pages 工作流；网站是否上线以 GitHub Actions 的部署结果及仓库 Pages 设置为准。

## 验证范围

`docs/mesh-validation.json` 记录闭合网格、正体积、单个连通组件、尺寸包络及离散开盖碰撞。数字模型通过检查也不能替代真实设备、公差、接触压力、开盖轴和使用功能的装配测试。建议首先制作一套样件，再决定最终壁厚、固定方式和材料。

Three.js 许可证见 `vendor/THREE-LICENSE.txt`。网页中的白色原盒和分件包络为近似示意，不含真实耳机内部结构；不属于打印套壳。用户参考图未复制进仓库；外观依据本次聊天中的三视图人工进行参数化重建。
