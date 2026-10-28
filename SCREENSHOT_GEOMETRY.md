# Phase 3：游戏原生截图几何实测

起点：`0883248fe838c56201f7408898fbe77cb71e4474`，工作区干净。
本轮仅增加离线开发工具和采集协议，复用 Phase 2 校准器。
不生成/修改地图、NVR1、应用、生产资源目录或签名；不运行游戏输入自动化、
不读游戏内存、不注入、不修改反作弊。原图不复制、不改名、不删除、不上传。

## 1. 先提供一张，不必立即测完地图

在游戏设置中确认 **游戏自己的 Screenshot/截图按键**，进任意地图手动拍一张。
不是微信截图、Windows 截图工具或 Steam F12。保留游戏保存的完整原文件名和 PNG。
默认位置为当前用户 Documents 下 `Escape from Tarkov/Screenshots`，也支持明确指定
采集目录。通过聊天传送时建议 ZIP，防止平台重命名或重新编码；或只提供本机路径。

第一张用于核对本机实际游戏文件名和 PNG，并不等于地图几何验收。不能将改名的普通
图片、本文示例或合成测试图当作真实游戏采集。用户隐私原图不提交源码仓库。

## 2. 文件名调查与解析边界

实际检索参考了工具作者公开源码，未运行或引入其按键、清理、上传功能：

- [tarkovxyz-agent 固定源码](https://github.com/TheoM83/tarkovxyz-agent/blob/c323d0c8a51f0ef092186c81173e9b6781f6acb4/tarkovxyz.py)，
  源码 SHA-256 `e6bbd1ccbfa1dd6f1d19e3a44f578aa5f36050973d941aaf884776068cadd669`。
  描述日期、XYZ、四元数、额外数字、重名序号；数字可能含科学计数法。
- [同项目 README](https://github.com/TheoM83/tarkovxyz-agent/blob/c323d0c8a51f0ef092186c81173e9b6781f6acb4/README.md)
  提供文件名示例与默认目录。这是格式参考，不是本机原图，也不是 BSG 官方格式保证。
- [TanukiTarkovMap](https://github.com/siakun/TanukiTarkovMap/tree/5019a887a816ee60bfc8e64deec2e564abc64149)
  的说明还出现无分隔下划线的样式。本轮没有对应原始 PNG，不猜测兼容或默默修补它。

当前解析的完整结构：

```text
YYYY-MM-DD[HH-MM]_X, Y, Z_QX, QY, QZ, QW_EXTRA (INDEX).png
```

解析器独立实现，完整匹配文件名，支持负值、十进制/科学计数法和大小写 PNG 扩展名。
拒绝无坐标图、非法日期/时间、路径注入、非有限/过大数字、缺失字段、改扩展名或尾随
垃圾。不猜测其他版本格式，不将科学计数法误拆成字段。保留原文件名、原始 XYZ、
四元数和额外字段；时间区和坐标参考原点仍是 UNKNOWN，不从 EXTRA 推断站位。

文件检查为真实 PNG 格式、尺寸界限及完整性验证，并对完整原字节计算 SHA-256。
文件读取前后大小/mtime/inode 改变则拒绝本次导入，等待游戏完成写入后人工再运行。
哈希验证字节身份，**不证明文件名坐标真实、不证明文件由游戏产生**。

## 3. 本地只读导入命令

在应用源码根运行，复用已存在的 Pillow/地图工具环境，不安装新依赖：

```powershell
$env:PYTHONPATH = "$PWD\build\map-tools;$PWD\tools\resources"
$env:PYTHONDONTWRITEBYTECODE = '1'
python tools/resources/eft_screenshot_capture.py --output build/map-recovery-20261028/my-capture-001
# 自定义采集目录：增加 --directory '用户明确提供的原始截图目录'
```

每次 output 必须是新目录，且不能与截图目录互相嵌套。没有截图目录时输出明确的
`NO_SCREENSHOT_DIRECTORY` 和零样本，不创建原生截图目录。程序不递归扫描，不看其他
账户或整块磁盘；仅检查指定目录的 PNG。上限为 256 图、单图 64 MiB、合集 256 MiB、
单轴 16384、总像素 64 Mi；选择小的专项采集目录即可，不用创建大型构建。
链接/reparse 路径拒绝；无原生图片写入或清理动作。
Phase 2 的 128 个来源上限仍生效；按楼层小批采集，不能把批量导入当作放宽校准契约。

输出：

- `captures.json`：原始文件名、SHA-256、XYZ、尺寸、解析状态和拒绝原因。
- `measurements.json`：待人工填写的配对记录，所有确认默认 false，UV 和不确定度为空。

目录自身缺失、没有有效样本、导入有效记录但原生来源未确认是不同状态。
Windows 默认目录通过当前用户 Documents 查询，不硬编码用户名/盘符。

## 4. 人工独立配对格式

在导出的 measurements.json 中，先填写顶层 mapId。每条记录填写以下字段；文件名
和截图哈希保持导入值，不手写修改 XYZ。

| 字段 | 含义 |
| --- | --- |
| id / floorId | 独立观测 ID / 原生稳定楼层 ID，不能从截图名猜地图或楼层 |
| originalFilename / screenshotSha256 | 原始完整文件名和原字节身份；导入拟合前再次核验 |
| role | 预先选定 fit 或 holdout；不能看过误差后调换 |
| landmarkName / region | 同一实际站位的明确名称 / 实际建筑或区域 |
| image / imageLocator | 人工观察的原 SVG viewBox `[u,v]` 及精确定位说明 |
| imageSha256 | 对应候选原始 SVG 哈希，不是截图、预览 PNG 或标注 overlay 的哈希 |
| imageSelectionMethod | 只接受 `manual-source-svg`，不得先用世界投影算 UV |
| worldSemantic / imageSemantic | 明确区分 player-position、room-boundary、building-corner、extraction-area-center、interactive-object；未知保持原默认值 |
| gameVersion / mode / sessionId | 实际游戏版本、PvP/PvE、独立采集批次；不拿网页日期冒充游戏版本 |
| evidenceSource / reviewRecord / reviewer | 现场记录、同一实体与来源独立性复核记录和复核者 |
| coordinateReferenceEvidence | 玩家/相机/其他原点的实测确认、姿态和参考依据 |
| uncertaintyWorld / uncertaintyEvidence | 有依据的合成不确定度和计算说明，须含读点、文件名舍入、站位/参考点偏移等影响 |
| confirmations | nativeOrigin、mapAndFloor、coordinateReference、samePhysicalEntity、independentImagePick、independentWorldSource，全为人工明确确认 |

文件名位置不能直接赋予墙角/房间边界/交互物语义。当前桥接只将**人工确认的玩家
站位**配到图中的同一玩家站位；其他语义保留为 PENDING 研究记录，不加入拟合。
本轮不做偏移换算。一个人在墙旁站立，不等于测出了墙面位置。

先盲于投影结果在候选原 SVG 上独立读 UV，再与原生截图站位配对。可使用既有
`geometry-phase2-evidence/<map>/<floor>.observations.svg` 定位源组，但它不是已验收
控制点，也不是预览 PNG 像素坐标。使用显示原 viewBox 单位的编辑器读点；不能把
桌面鼠标坐标、DPI 缩放后坐标或 1024 宽预览坐标直接填成原 SVG 坐标。

截图原点确认可由用户人工在固定站位朝不同方向拍摄并记录姿态，比较 XYZ/四元数；
必要时人工比较站立/蹲姿。此检查不由工具操作游戏，也不自动证明玩家脚底坐标。
若参考原点或合成误差无法确认，保留对应 false/空值，不为凑点填 0.2 或勾 true。

## 5. 两个专项采集清单

### Customs 第四层：建议先做 8 个不同站位

稳定 mapId：`56f40101d2720b2a4d8b45d6`；floorId：`4th_Floor`。
候选原 SVG：`Customs-Fourth_Floor.svg`，SHA-256
`d4bd72d8fd9f5e7f8e7c64f6848863b87c425843aaf058a78d6f256a9dc6cba0`。
两栋建筑暂按原图 Fourth_Floor 的第一个/第二个 path 标为 A/B，不凭名称猜游戏实体。
每栋均取分散站位，拟合组和留出组都必须覆盖两栋。

| ID | 组 | 现场采集目标；只有图像和游戏均能辨认才使用 |
| --- | --- | --- |
| A-F1 / B-F1 | fit | 各栋入口平台可站立的明确阈线/地面标识 |
| A-F2 / B-F2 | fit | 各栋另一方位楼梯平台的可站立交点，不能沿同一边挤点 |
| A-H1 / B-H1 | holdout | 各栋远侧平台可站立的固定地面特征 |
| A-H2 / B-H2 | holdout | 各栋另一出口/连接处的固定地面特征，未用于拟合 |

这些是**待辨认的目标类型**，不是已确认游戏中存在的标记。拍摄应显示平台、入口、
楼梯和周围建筑上下文，并另记实际高度和层间关系。图中找不到同一地面细节，或玩家
无法准确站位时换目标并在拟合前登记；不能拿预测世界坐标、API 中心或重复照片填数。

### The Lab Technical：先认定被裁房间，再采分散点

稳定 mapId：`5b0fc42d86f7744a585f9105`；floorId：`Technical`。
候选原 SVG：Labs.svg（保留目录中为 SOURCE.svg），SHA-256
`099a9eaabc305431d906151e03c45d6f06bb885ec46234735e93cc2ab02a222a`。

本轮只读定位到 `Technical_Level / Rooms / path[27]`（1 起始索引），路径起点
`(344.427,11.1899)`，矩形到 `(361.816,25.1887)`。它与前轮裁切条带相交；
这是源 SVG 几何，不是游戏世界坐标。**实际游戏房间身份尚未确认，不能编造房名。**

- 先提供房间、门口及相邻走廊上下文，人工确认同一实体。
- fit：房间内可辨认站位、相邻通道固定地面位置、远端楼梯平台，各取不同位置。
- holdout：房间另一侧可辨认站位、另一走廊位置、不同楼梯平台，不参与拟合。
- 能到达哪里与墙在哪里分别记录。站位只能证明对应可达位置，不能变成墙面坐标。
- 若无法认定 path[27] 的游戏实体，其他已辨认的电梯/楼梯可以研究全局标定，但不能
  代替局部裁切附近的实测，也不能据此宣布裁切已修复。

每个有效点保留游戏原图和上下文；同一截图即使改文件名也不能充当两个独立观测。
最低要求仍是每层 >=3 非共线 fit + >=3 分散 holdout、合成不确定度 <=0.25、
留出 RMSE <=0.5、最大误差 <=1.0 世界单位，并做局部结构审核。没有降低门槛。

## 6. 接入现有校准器

```powershell
python tools/resources/import_screenshot_geometry.py --directory '原始截图目录' --template 'build/map-recovery-20261028/geometry-phase2-evidence/customs/controls.json' --annotations '人工填写的measurements.json' --image '已保留的Customs-Fourth_Floor.svg完整路径' --output build/map-recovery-20261028/my-customs-measurement-001
# Lab：template 改为 .../lab/controls.json；image 使用 .../lab-final/upstream/SOURCE.svg
```

每次处理同一份源 SVG，可接受它所包含的多个楼层；不同源 SVG 分别记录。
工具读取明确目录内的原图，重新核验完整文件名/PNG/哈希及原 SVG 身份，然后输出：

- measurements.json：保留人工记录、截图原始 XYZ、SHA-256、语义和 pending 原因。
- controls.json：仅将所有确认完成的同一站位配对交给 Phase 2，原 XYZ 不改；拟合用 x/z，
  y 仍保留于证据。手写 worldXYZ 覆盖字段被忽略，实际值重新来自原文件名。
- report.json / report.md / residuals.svg：复用 7 类变换、固定 fit/holdout、分布和误差输出。

哈希不符、重复截图、越界 UV、错误地图/楼层/图像、路径逃逸或非法数字会拒绝。
缺人工确认、错误实体语义、缺/超出不确定度时记录为 PENDING，不导出为拟合点。
缺点/退化数据误差保持 UNKNOWN。源码中的合成测试并非游戏测量，不充当控制点。
`publicationAuthorized:false` 始终不变；来源声明和勾选不能自动认证截图或发布地图。

## 7. 本轮结果与剩余证据

本机查询的当前用户 Documents 和 OneDrive 默认 EFT 截图目录不存在；未扫描其他
私人目录、未接触游戏进程。实际默认目录命令输出 `NO_SCREENSHOT_DIRECTORY`，
有效图 0。已告知用户如何提供一张保留文件名的原 PNG；尚未收到真实样本。

在 `build/map-recovery-20261028/` 保存小型本地报告：

- `phase3-native-scan/`：默认目录实际查询和空采集清单。
- `phase3-customs-report/`：复用真实保留 SVG/Phase 2 模板，0 配对，五层 UNKNOWN。
- `phase3-lab-report/`：复用真实保留 SVG/Phase 2 模板，0 配对，三层 UNKNOWN。
- `phase3-final-evidence/{customs,lab}/`：最终 CLI 报告，Markdown 同时显示原生采集
  PENDING 边界；前两份早期报告保留，不覆盖。

截图解析/配对新增测试覆盖普通/负值/科学计数法、非法格式/日期、完整原图哈希和
不改原文件、损坏 PNG、大小/数量限制、目录隔离、固定分组、实体语义、独立读点、
原图变更、同图重复、XYZ 不被覆盖及实际 CLI 桥接。全部使用明确标记的合成图和坐标。
资源工具全套 **76/76 PASS**（截图/配对新增 21 项）；地图生成器全套 **45/45 PASS**。
这些是离线工程测试，不是实测或 GUI 验收。`git diff --check` 通过（Git 有行尾转换
提示，不声称 warning-clean）。未重新生成地图资产或重复资源生命周期测试。

| 验收项 | 实际状态 |
| --- | --- |
| 解析器及只读导入工程 | 已实现并做离线测试 |
| 本机真实原生截图格式验证 | PENDING，真实原图 0 张 |
| 真实独立配对 | Customs 0、Lab 0 |
| 真实 fit / holdout 误差 | UNKNOWN，不虚构零误差 |
| Customs 第四层 / Lab Technical 几何 | BLOCKED，不进入发布审核 |
| 玩家站位与边界/房间身份确认 | PENDING，不能由哈希或软件勾选代替 |
| GUI / 完整 Debug-Release CTest | 本轮未执行；仅开发工具/文档变化，无应用改动 |

下一步先拿到 **一张原始游戏 PNG** 验证实际命名及字节，再开展上述专项现场采集。
没有新 NVR1、资源发布、签名变更、main 推送或应用安装，不增加候选地图数量。
