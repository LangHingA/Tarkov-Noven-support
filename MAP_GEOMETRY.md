# Phase 2：地图几何恢复与独立校准

后续 [Phase 3 原生截图实测流程](SCREENSHOT_GEOMETRY.md) 提供只读截图解析、哈希、
人工配对与本校准器桥接；无真实截图时仍保持 UNKNOWN，不替换本报告的历史证据。

日期：2026-10-28。实际起点 `4740597a18886ea343154fe8604d2a60be095bde`，
工作区干净。本轮为本地研究，不重复开发资源生命周期，不改变生产目录、签名、
应用 0.1.3、地图稳定 ID、Core TSV 或原生坐标。全量楼层清单仍见
[MAP_COVERAGE.md](MAP_COVERAGE.md) 和生成的 `tools/resources/map_coverage.json`。

**结果：没有地图进入 READY_FOR_PUBLICATION_REVIEW 或 COMPLETE。**
新增了可复核的来源谱系、解析矩阵、Lab 实体裁切诊断、48 个待辨认图像采集位置及
校准工具；尚未获得同一物理实体的独立世界观测。数值未知保持 UNKNOWN。

## 1. 本轮可靠新增证据

### 公开 API 已恢复可读，不沿用旧 403 结论

本轮实际 HTTPS 获取以下公开端点均为 200，证书验证保持开启：

| 来源 | 字节 | SHA-256 |
| --- | --- | --- |
| [regular/maps](https://json.tarkov.dev/regular/maps) | 8,700,573 | `423d52d7a731e5a89b30668783e82e1caf6012846f7780bd1ff92f0b84140f63` |
| [pve/maps](https://json.tarkov.dev/pve/maps) | 8,738,480 | `56032f4674b1fa59b2c93f6cd122ecdea8571971c8e5ebd7a37f3221b47819c9` |

保存在 `build/map-recovery-20261028/phase2-{regular,pve}-maps.json`，不提交公开
快照。获取日期不等于游戏构建版本；端点未提供足以认证实际游戏几何版本的控制点表。
Python HTTPS 曾报本机 CA 链错误；随后使用 Windows Schannel curl 成功，未关闭 TLS
验证、未改证书或安全策略。

| 地图 | extracts / locks / switches / spawns（regular） | 新证据及边界 |
| --- | --- | --- |
| Customs | 28 / 37 / 1 / 278 | 两个新锁 ID 都是 `lockType:trunk`，不是固定建筑地标 |
| Reserve | 11 / 34 / 3 / 167 | 未增加上层轮廓或房间面数据 |
| Lab | 7 / 17 / 15 / 134 | 原有锁、开关、撤离点位置未变化；仍缺图像实体配对 |
| Dark Lab | 0 / 0 / 0 / 145 | `maps/laboratory_dark_preset.bundle`，普通版为 `maps/laboratory_preset.bundle` |
| Tutorial | 0 / 0 / 0 / 17 | `maps/sandbox_start_preset.bundle`，普通版为 `maps/sandbox_preset.bundle` |
| Icebreaker | 1 / 11 / 0 / 56 | 有世界对象位置，不提供甲板边界/图像地标对应 |

六图 locks/extracts/switches 在本轮 regular/PvE 快照逐记录一致；Customs spawns
两模式不完全相同，不合并或覆盖。出生点顺序、记录 ID 或数量变化不能直接证明墙体变化。
两后备箱新增点分别为 x/y/z `(206.57,0.62,175.26)` 和
`(-269.53,1.67,-133.86)`；不是为了通过验收而导入的建筑控制点。

### 多个仓库不是多份独立测量

本轮用 GitHub API 读取完整、非 truncated 文件树：

| 仓库 | 实际 HEAD | 结论 |
| --- | --- | --- |
| [TarkovTracker/tarkovdata](https://github.com/TarkovTracker/tarkovdata/tree/1b9bc2acbea0e873244d1819cba9d9fe0f14e26c) | `1b9bc2acbea0e873244d1819cba9d9fe0f14e26c` | Labs/Reserve SVG 与 Shebuka 仓库分别是相同 Git blob |
| [the-hideout/tarkov-dev-svg-maps](https://github.com/the-hideout/tarkov-dev-svg-maps/tree/5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178) | `5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178` | Reserve 仍只有 Ground_Level、Bunkers；无新 Lab 图 |
| [acidphantasm/SPT-DynamicMaps](https://github.com/acidphantasm/SPT-DynamicMaps/tree/4944764f5f6c42d152dca6bd1b5371c4f6212a9e) | `4944764f5f6c42d152dca6bd1b5371c4f6212a9e` | 与保留分层 SVG、JSONC 同版本 |
| [jeanlannce/NormalMaps](https://github.com/jeanlannce/NormalMaps/tree/fe3ce5cf5c2e3e187658c2d67405fef6d0659cf0) | `fe3ce5cf5c2e3e187658c2d67405fef6d0659cf0` | Labs/Reserve 分层与 SPT 相同，不补独立证据或上层素材 |

Labs blob：`d3fbfa5925e3988c43c9ab781c76c682fcb2e640`；Reserve blob：
`c5fc16f051cf860b94bec9ecb2372cb139c8ffa9`。这是 Git 对象 ID，不冒充文件 SHA-256。
相关软件 MIT 许可不能替代图像许可；保留 Shebuka/acidphantasm 的资产专属
CC BY-NC-SA 4.0、原作者/来源、既有修改、反作弊声明和本地转换记录。

## 2. Customs：五层解析投影，不是独立精度 PASS

固定 SPT 来源、原 SVG SHA-256 及许可详见
[既有来源表](docs/MAP_SVG_EXTENSION.md#customs-acceptance-result-blocked)。
五层候选和其 223 文件保留根不变。本轮不重新封包或覆盖候选。

来源 JSONC：180 度，x `[-372,698]`，z `[-306,235]`。
Ground SVG viewBox 为 `1062.48 x 535.17`，其余四层为
`1062.4827 x 535.174`。以原始 SVG `(u,v)` 表示：

```text
x = 698 - 1070*u/viewWidth
z = -306 + 541*v/viewHeight
native U = 698 - x
native V = z + 307
```

这推导出来源到原生图的缩放和 V 方向 1 世界单位的留边，不是拟合出的修正。
Ground/其他层 viewBox 小数精度对相同画布点造成的最大矩形角差约
`0.0048727585` 世界单位；它只界定画布参数差，**不证明跨层楼梯对齐**。
不能把同一来源的轮廓、配置和坐标互相变换后称作独立验收。

| 原生层 | 原始组 / 覆盖 | 新图像采集位置数 | 独立 fit / holdout | 留出 RMSE / max |
| --- | --- | --- | --- | --- |
| Ground_Level | Ground_Level；运行候选还保留 First_Floor 伴随组 | 6 | 0 / 0 | UNKNOWN / UNKNOWN |
| Second_Floor | Second_Floor | 6 | 0 / 0 | UNKNOWN / UNKNOWN |
| Third_Floor | Third_Floor | 6 | 0 / 0 | UNKNOWN / UNKNOWN |
| 4th_Floor | Fourth_Floor，两块实际建筑而非第三层改名 | 6 | 0 / 0 | UNKNOWN / UNKNOWN |
| Underground_Level | Underground_Level | 6 | 0 / 0 | UNKNOWN / UNKNOWN |

图像采集点是原始路径起点/多边形顶点，不是假定的门槛或墙角身份。第四层仍须分别
核验两块建筑，不能只在一条边采六点。原生第四层区域、高度和真实世界点未改动。
原始组内有明确 transform 的节点不被工具当成根坐标直接读入。

**BLOCKED 的具体缺口：**每层至少 3 个非共线拟合点和 3 个不同留出点，每点有
同一实体的图像/世界观测、物理位置解释、实际游戏版本和总不确定度；还需跨层楼梯
对应及第四层两栋建筑的实体证据。没有这些输入，不进行虚假残差拟合。

## 3. Lab：两套不相同的来源标定和确定的候选裁切

原图 SHA-256 仍为
`099a9eaabc305431d906151e03c45d6f06bb885ec46234735e93cc2ab02a222a`，
viewBox `720 x 586`，三层映射和完整许可不变。

### 相同 SVG 的来源元数据不一致，不能任取一套作为真值

[tarkovdata maps.json 固定版本](https://raw.githubusercontent.com/TarkovTracker/tarkovdata/1b9bc2acbea0e873244d1819cba9d9fe0f14e26c/maps.json)
7,322 字节，SHA-256
`8d163ce259449f9a922c372ebd1b019f25044cd81727570874d6d52e10dd14ac`，
Lab 标定为 x `[-287,-91]`，z `[-477,-193]`，270 度。
保留 SPT JSONC 则是 x `[-292,-96]`，z `[-441,-223]`，270 度。

```text
SPT declared frame:        x = -292 + 196*v/586; z = -441 + 218*u/720
tarkovdata declared frame: x = -287 + 196*v/586; z = -477 + 284*u/720
frame difference:         dx = 5; dz = -36 + 66*u/720
```

这不是一个统一的平移偏差；世界标注能吻合，不代表这两套像素映射均正确。
原生当前范围还采用 maxX `-80`，未擅自改成历史 `-91`。
公开仓库复用和参数差异都不能决定哪个墙角对应真实世界点。

### 源实体裁切可复现，但成因仍需要独立几何判断

当前候选保留 SPT 世界标定，转换到不变的原生 `284 x 207` 坐标画布：

```text
native U = 218*u/720 + 36
native V = 196*v/586 - 5
```

因此源图 `v < 14.9489795918367` 位于原生上边界以外。
在原 SVG 4 倍采样 `2880 x 2344`、移除 shadow filter、alpha >=250 条件下：

| 原生层 / 源组 | 源不透明像素 | 被原生边界裁掉的不透明像素 |
| --- | --- | --- |
| Technical / Technical_Level | 1,526,345 | **1,463** |
| Base / First_Level | 3,640,145 | 0 |
| Second_Level / Second_Level | 2,027,432 | 0 |

像素中心判定保留矩形 `[0,60,2880,2344]`；不是把抗锯齿/阴影当作房间。
单独渲染 Technical 子组确认被裁的是 `Rooms`，`Arrows/Doors/Details` 在该条带
没有被裁的高 alpha 像素。此结果证明**候选丢失来源 Rooms 图形**，尚不能证明这些
轮廓对应当前游戏的可达空间，也不能判定来源标定或原生范围谁对。不得因此改正确
坐标、把画布整体拉伸、删去房间图形，或宣称整个 SVG 过时。

三层各有 6 个原 SVG 图像采集位置，独立 fit/holdout 都是 **0/0**；
图像—世界留出误差均 UNKNOWN。Lab 仍 BLOCKED，并新增精确的边界核验事项。

### 撤离语义复验

本轮新 API 上重新运行旧 19 点世界标注诊断：identity 6 点训练 RMSE
`0.0119849466`，13 点留出 RMSE `0.00518826935`、max `0.0142919514`。
**这只是来源世界标注一致性，不是独立 SVG 图像误差。**
Parking Gate 旧点到 API 区域中心距离 `22.95521193`，Hangar Gate 为
`21.90065981`；两 API 点距对应矩形中心均约 `0.00707107`。这支持区域中心语义，
不能把它们当物理门槛/铰链位置。入口、激活范围和区域中心须分开记录。

## 4. 其余四条研究线的具体结果

### Reserve：PARTIAL 2/6，整体 BLOCKED

Shebuka 组合 SVG、SPT 分层和 NormalMaps 复制件仍只有 Ground_Level/Bunkers。
核对文件树、来源组和作者命名，未发现四层被漏选的合法矢量。tarkovdata 同样仅列
两层，且它的旧 z `[-338,336]` 与 SPT `[-275,271.5]` 不同；不能混配校准参数。
[re3mr 自述页面](https://reemr.se/reserve/) 提供地面 3D 和 tunnels 2D/3D，
没有建立完整六层正投影契约；没有下载 131 MB PSD，也没有拿透视地面图填上层。

仍缺 `2nd_Floor/3rd_Floor/4th_Floor/5th_Floor` 的实际房间、通道和楼梯矢量，
以及每层物理地标/高度对应。保留上一轮两层预览和细节，不造 NVR1 完整包。

### Dark Lab：BLOCKED，不因同投影直接复制

当前 API 明确引用不同的 dark preset；普通版/暗版锁、开关、撤离数据并不齐备。
`coordinateToCardinalRotation` 普通 270、暗版 180 是朝向字段，**不是修改底图旋转的
授权**，不能用它取代现有 MapProjection。三层、原生投影一致只说明客户端共享框架。
需分别核验同一实体的位置、房间可达性、封锁门/楼梯和实际撤离/开关差异。

### Icebreaker：BLOCKED，形成 16 切片采集清单

继续使用保留 re3mr 1.7 原图，SHA-256
`13d5cead3b2949981f4dfb8445b2280f3a8e5cc9ba30cee42a1c301e311d3329`；
没有再次复制大图或创建包。下表右列仅为**需实测的候选对应**，不是验证完成：

| 原生切片 | 原生 y 规则 | 作者 deck / 待核验事项 |
| --- | --- | --- |
| Bridge_Roof | [43.8,10000) | 10，核实屋顶路径和上下通道 |
| Bridge | [40.7,43.7) | 9，核实驾驶室入口 |
| Stairs_blocked | [37.6,40.6) | 8，核实封闭区域边界 |
| Officers_Deck | [34.5,37.5) | 7，核实走廊与楼梯 |
| Accommodation_upper | [31.4,34.4) | 6 |
| Accommodation_mid | [28.3,31.3) | 5 |
| Accommodation_lower | [25.3,28.2) | 4 |
| Gym_Canteen | [22.2,25.2) | 3 |
| Helipad | [19.57,22.1) | 2 |
| Base | 原生默认回落，不是一个精确 y 区间 | 1 Infirmary；不能仅由顺序推定其上下界 |
| Storage_Security | [15,18.93) | 0 |
| Fuel_Pumps | [11.9,14.9) | -1；与下切片的可达层差未知 |
| Fuel_Pumps_lower | [8.8,11.8) | -1 或过渡平台？须确认，不能重复上图 |
| Engine_Room_upper | [5.7,8.7) | -2 的上层平台？须确认，不能重复主层 |
| Engine_Room | [3.6,5.6) | -2 |
| Control_Room | [-10000,3.5) | -3 Lower Automation；身份/轮廓尚未证明一致 |

高度规则存在小空隙并回落 Base，不由 deck 编号臆造等距高度。
[作者更新记录](https://reemr.se/icebreaker/) 明确提及封闭房间、通道可达性和
lower automation 命名的修订，因此不能仅靠名称完成映射。当前图有单独归属 BSG 的
侧视船体，以及任务/协作者归属，不能推定作者的 CC 授权覆盖所有元素。
CC 版本链接差异和 FAQ 的再托管说明见前轮报告；不发明伴侣软件禁令，亦不直接
重托管独立权利内容。下一步需要可排除独立元素的作者甲板几何和实际层间测量。

### Ground Zero Tutorial：BLOCKED，有专属预设但无专属契约

新 API 提供独立 scenePath 和 17 个出生点，其包围盒为 x `[-45.97,199.1788]`、
y `[16.28865,24.195]`、z `[-58.68419,40.08581]`。**出生点包围盒不是地图边界**，
不能据此定义 floors/projection。缺少可达区域、封路、楼层高度、出口的独立记录。
当前资源契约不能替换 Core TSV；即使以后证实可共享部分 Ground Zero 几何，仍需
单独验证教程定义并通过未来应用数据版本交付，不在本轮改动已发布 0.1.3。

## 5. 可执行的证据获取方案

### 最小交付表：不是再提供另一份同源标注

每个实际物理地标交付：稳定 map/floor ID、明确的门槛中点/可达地面角/楼梯平台角、
原始 SVG locator 和 `(u,v)`、同一实体的世界 `(x,y,z)`、实际游戏版本、模式、
带上下文的合法可见画面或独立公开测量来源、文件 SHA-256、原始坐标语义、偏移和
合成不确定度、来源谱系/修改史。保留原始点，不把最近的 API 点自动认成对应实体。

可以人工在游戏允许的练习/正常场景采集用户可见画面及游戏自带的坐标信息；须先
确认截图坐标记录的是玩家/相机/其他原点，**不能直接当作铰链或墙角坐标**。优先选
可站立、可复测的地面阈值或平台标线，并独立测量必要偏移。若无法把合成不确定度
控制在 0.25 内，该点不验收。本轮不进行内存读取、注入、游戏解包或自动化操作。

| 区域 | 具体待取得的实体证据；取得后再与图像位置配对 |
| --- | --- |
| Customs Ground | 地图西/中/东固定建筑的地面入口/楼梯平台，不用后备箱和撤离中心 |
| Customs Second | 宿舍及工业建筑的实际二层平台、走廊门槛；跨至少两栋建筑 |
| Customs Third | 三层宿舍和工业高层中可辨认平台/墙角；不将不同建筑当同一楼梯 |
| Customs Fourth | 两块 oilrig/panda 来源轮廓各自的可达平台/转角、位置和高度；fit/holdout 都覆盖两栋 |
| Customs Underground | 对应各地下建筑/楼梯的地面转折点，不用整个地下撤离体积中心 |
| Lab Technical | 主/医疗电梯实体阈值、两端楼梯平台和管道转角；特别核实被裁 Rooms 上边界 |
| Lab Base | 蓝/黑/武器测试房门口及分散楼梯；停车/机库门须独立标记阈值而非区域中心 |
| Lab Second | 红/紫/经理办公室、军械库和另一端楼梯，固定同一参考点语义 |

这些是采集区域建议，不声称已确认其与 48 个 SVG 顶点一一对应。每层先确认或
替换目标，再预先登记 >=3 fit 和 >=3 holdout，留下变更记录，随后才拟合。
跨层需同一楼梯/电梯的配对平面坐标与实际层高记录，不能仅比较组名或像素接近。

Reserve 四个上层需作者可再分发的分层原作，或在独立授权/原创测绘基础上新绘房间
及楼梯；原作/测绘过程、派生许可、修改史均须明确，不用复制地面或追描许可不清图片。
Dark 需逐层可达性/门控差异表；Icebreaker 需每个平台分叉两侧的高度和可见几何，
尤其两组 upper/lower；Tutorial 需教程专属路线/封锁/出口/高度和坐标框架证明。

拿到资料后，按 [GEOMETRY.md](tools/resources/GEOMETRY.md) 填入 `controls.json`，
复核源哈希和独立性，再运行工具。7 类模型只用固定 fit 点；holdout 不用于训练或
删除异常。每层 RMSE <=0.5、max <=1.0、不确定度 <=0.25，且没有未解释的局部差异，
才继续全楼层/许可/原生/GUI审核。工具数值通过不自动给发布权。

## 6. 本地产物与测试

新增工具：`calibrate_map_geometry.py`（模型/分布/残差/证据门禁）和
`prepare_geometry_requests.py`（固定来源图像采集目标与裁切诊断）；输入契约、命令和
独立性边界见 [工具说明](tools/resources/GEOMETRY.md)。不引入依赖。

复用隔离根 `build/map-recovery-20261028/`：

- `geometry-phase2-evidence/`：最终 23 个文件，含 48 个待辨认图像位置、源哈希、
  逐层观察 SVG、两个 UNKNOWN 校准报告、解析矩阵/裁切证据及完整许可/声明。
- `geometry-phase2-cli-{customs,lab}/`：实际 CLI 的 JSON/Markdown/残差 SVG 输出。
- `geometry-phase2/`、`geometry-phase2-final/`：保留的早期诊断，不覆盖旧记录。
- 两份本轮公开 API 快照：约 16.63 MiB；不创建新 C++/安装/应用副本。

没有新增 NVR1：上一轮 Lab 三层和 Customs 五层候选已足够承载后续研究。
Reserve 维持 2/6 素材，其余地图没有不真实的候选包。

| 检查 | 本轮结果 |
| --- | --- |
| 资源工具全套离线测试 | 55/55 PASS（原 37 + 新增 18） |
| Maps generator 全套离线测试 | 45/45 PASS |
| 固定原始来源生成复验 | 23 文件离线重复字节一致；已有输出根拒绝覆盖 |
| 真实图像配对校准 CLI | Customs 五层、Lab 三层均输出 0/0、UNKNOWN，不伪造误差 |
| 解析投影 | 0/37/90/180/195.209/270 度和非零 viewBox 原点与既有生成器一致 |
| 安全/反自证 | 同图像/配置谱系或相同哈希拒绝作独立来源；缺证据、超不确定度、退化集合保持 UNKNOWN；重复点/无效坐标/阈值覆盖拒绝 |
| 生产目录 / 既有候选 | 匿名重取包络 11,296 字节，SHA-256 `38441b9a2794bf61efe68045bf821108b91f8b11614532ef7f331a1246fd773c`，与前轮已验证的 11 项包络身份相同；本轮不重复 CNG 验签，不修改、不签名、不上传；保留原包哈希 |
| 原生资源生命周期 | 本轮不重复；上一轮结果明确不替代几何或 GUI |
| GUI / 新地图远端 / 完整 Debug-Release CTest | 未执行；无原生应用改动，也未达到资源发布条件 |

结论：新证据收紧了具体问题定义，但不能把工程可加载等同独立几何通过。
Customs/Lab 0 个已验证图像—世界配对，Reserve 仍缺四层；六张均 BLOCKED。
11 个既有生产记录不变。本轮不宣称全里程碑完成，不进入生产发布或其他阶段。
