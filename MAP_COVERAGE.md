# 地图补全审计 / Map recovery audit

核验日期：2026-10-28。开始时本地 `main` 与 `git fetch origin main` 后的
`origin/main` 均为 `b360af039bed06d57ceb0b1a09aaed0a5439ea66`，工作区干净。
本报告只描述本地研究、候选制作和测试；**没有生产发布授权动作**。
应用仍为 0.1.3，未修改 Core TSV、原生运行代码、签名信任或安装包。

## 统计口径

- 已收录：17 个稳定 MapCatalog ID。
- 已发布：11/17 = **64.7%**，不是本轮新完成数量。
- 已发布包覆盖：33/66 个**已定义**原生楼层 = **50.0%**。
  Tutorial 尚无楼层定义，不能把 0 层当作已完成，66 也不是游戏总楼层的最终证明。
- 开发树已有 66/66 层预览和细节文件，但其中有未获再分发许可的 raster/tile
  派生图；**文件存在不等于可发布，也不等于独立几何通过**。
- 可检查的生产 SVG 包 33 层、Customs 候选 5 层、Lab 候选 3 层、Reserve
  部分候选 2 层，共 43/66 层有此类本地衍生产物（65.2%）。这仅是资产覆盖率。
- 本轮新增 COMPLETE：**0**；未重新完成独立几何和用户 GUI 验收的既有 11 张标为
  UNVERIFIED（本轮严格证据维度），**不撤销其历史交付和验收记录**。
  不将 PARTIAL、BLOCKED、UNVERIFIED 计入 COMPLETE；总量审计不能计算完整验收率，
  JSON 的 `completionCount` 为 null，不虚报 100%。

`tools/resources/map_coverage.json` 列出每层来源、哈希、许可、投影、顺序、高度区域、
开发文件、生产包和显式候选包。`stages` 分开记录收录、包完整性、正式列出和未执行的
原生/GUI 验收。未签名候选永远不增加 `publishedCount`。清单审计不是签名权威。

## 17 张地图覆盖表

楼层按当前 `order` 展示，不擅自重新编号。`P` 为生产包层数，`C` 为未发布候选完整
预览/细节层数；两者不是独立坐标准确性得分。`S` 为已发布 SVG 包的逐文件来源清单
及 CC BY-NC-SA 4.0 归属记录；源码/图像版本不自动等于当前游戏几何版本。

| 地图 / 稳定 ID | 当前全部楼层（显示顺序） | P / C | 来源、坐标与当前状态 |
| --- | --- | --- | --- |
| 工厂 `55f2d3fd4bdc2d5f408b4567` | Third_Floor, Second_Floor, Ground_Floor, Basement | 4 / 0 | S；原生投影保留；UNVERIFIED，已发布 |
| 海关 `56f40101d2720b2a4d8b45d6` | Second_Floor, 4th_Floor, Third_Floor, Ground_Level, Underground_Level | 0 / 5 | Shebuka/acidphantasm 五层 SVG；BLOCKED，缺独立地标 |
| 森林 `5704e3c2d2720bac5b8b4567` | Ground_Level | 1 / 0 | S；UNVERIFIED，已发布 |
| 灯塔 `5704e4dad2720bb55b8b4567` | Ground_Level | 1 / 0 | S；UNVERIFIED，已发布 |
| 海岸线 `5704e554d2720bac5b8b456e` | Third_Floor, Second_Floor, Ground_Level, Underground_Level | 4 / 0 | S；UNVERIFIED，已发布 |
| 储备站 `5704e5fad2720bc05b8b4567` | 4th_Floor, 3rd_Floor, 2nd_Floor, 5th_Floor, Ground_Level, Bunkers | 0 / 2 | Shebuka 两层 SVG；BLOCKED，上层四层缺素材/独立标定 |
| 立交桥 `5714dbc024597771384a510d` | Second_Floor, First_Floor, Ground_Level | 3 / 0 | S；原生 B1/1F/2F 语义不变；UNVERIFIED，已发布 |
| 街区 `5714dc692459777137212e12` | Fifth_Floor, Fourth_Floor, Third_Floor, Second_Floor, Ground_Level, Underground_Level | 6 / 0 | S；UNVERIFIED，已发布 |
| 夜间工厂 `59fc81d786f774390775787e` | Third_Floor, Second_Floor, Ground_Floor, Basement | 4 / 0 | S；独立资源 ID，共享既有图像；UNVERIFIED，已发布 |
| 实验室 `5b0fc42d86f7744a585f9105` | Second_Level, Base, Technical | 0 / 3 | Shebuka SVG；BLOCKED，缺独立图像/世界地标 |
| 中心区 `653e6760052c01c1c805532f` | Third_Floor, Second_Floor, Ground_Level, Underground_Level | 4 / 0 | S；UNVERIFIED，已发布 |
| 中心区 21+ `65b8d6f5cdde2479cb2a3125` | Third_Floor, Second_Floor, Ground_Level, Underground_Level | 4 / 0 | S；保留独立 ID；UNVERIFIED，已发布 |
| 码头 `65cc8f81a9aac3e77d0cfd3e` | Ground_Level | 1 / 0 | S；UNVERIFIED，已发布 |
| 迷宫 `6733700029c367a3d40b02af` | Base | 1 / 0 | acidphantasm SVG、资产专属 CC 许可；UNVERIFIED，已发布 |
| 中心区教程 `68236e8153654e8c1200798a` | 未定义；不是零层地图 | 0 / 0 | BLOCKED，无专属投影/楼层/可验证等价关系 |
| 破冰船 `69af492a4819ea4ba10a69c5` | Bridge_Roof, Bridge, Stairs_blocked, Officers_Deck, Accommodation_upper, Accommodation_mid, Accommodation_lower, Gym_Canteen, Helipad, Base, Storage_Security, Fuel_Pumps, Fuel_Pumps_lower, Engine_Room_upper, Engine_Room, Control_Room | 0 / 0 | BLOCKED，16 层原生切片；新来源仍缺层间/坐标/独立权利核验 |
| 实验室 Dark `6a294a5b5eb5f9a1700417b7` | Second_Level, Base, Technical | 0 / 0 | BLOCKED，投影共享不证明可达空间/撤离语义等价 |

## 固定来源与本轮联网证据

2026-10-28 读取的上游仓库 HEAD：

| 项目 | 固定 revision | 本轮结论 |
| --- | --- | --- |
| the-hideout/tarkov-dev-svg-maps | `5a8b6115d1c0cf56f2ebaac1a96fa5ae3074d178` | 与已有来源相同，无新增 Reserve 上层或新 Labs SVG |
| acidphantasm/SPT-DynamicMaps | `4944764f5f6c42d152dca6bd1b5371c4f6212a9e` | 与保留候选一致；有五层 Customs、两层 Reserve、三层 Labs |
| the-hideout/tarkov-dev | `ec44177bd3c21aa2b33938153acd0a96dbd939aa` | maps.json 109,867 字节，SHA-256 `c53a327dcdcff67a49b9fe2d150731edb4c1611dfc2f75db2ce97444dee2ef77`，与本地布局快照相同 |
| jeanlannce/NormalMaps | `fe3ce5cf5c2e3e187658c2d67405fef6d0659cf0` | Reserve/Labs 分层 Git blob 与 SPT 来源相同；不是额外几何证据 |

生产 `maps/manifest.json` 匿名 HTTPS 200，包络 SHA-256
`38441b9a2794bf61efe68045bf821108b91f8b11614532ef7f331a1246fd773c`，
仍为 11 项，和保留目录完全一致。原生 CNG 工具对该相同包络及 11 个本地包校验通过。
没有对六张缺失地图创建 GitHub asset、签名或上传，也没有改 `stable/release.json`。

本机直接读取 `json.tarkov.dev/regular/maps` 和 `pve/maps` 得到 HTTP 403，不能声称
获得最新游戏坐标。以下比较明确使用保留快照：regular SHA-256
`8b169057c8a26ef631ef5866cdf2cc77c6a7d44d32047f786803c6b0f7b7e73f`，PvE
`424b414ed484781506a62629014d4f2442baac70f6658e773b4106916e21aed2`。
没有覆盖快照、尝试绕过访问控制或以网站更新时间冒充游戏构建版本。

## 六条研究结论

### 1. Customs：五层资产存在，几何门禁不变

复用保留的 candidate-v2，而不是重新下载卫星图或再次大规模生成。五层独立 SVG
及许可证哈希、第四层两块实际建筑轮廓和油井/panda 高度区域，见
[已固定的验收协议及来源表](docs/MAP_SVG_EXTENSION.md#customs-final-validation-protocol-2026-10-20)。
地面必须保留 First_Floor 伴随组；第四层不是把 Third_Floor 改名。

每层仍缺至少三组独立拟合点和三组空间分散留出点，第四层须覆盖两块建筑；点位语义须
是同一墙角、门槛或楼梯实体。已有 SVG 顶点和 API 锁/撤离坐标没有可靠的物理配对表。
保留既定不确定度 <=0.25、留出 RMSE <=0.5、最大误差 <=1.0 世界单位标准。
本轮未伪造配对；各层图像到世界的留出 RMSE/max 均 **N/A**，不是零误差或失败数值。

旧 NVR1 未变：2,925,966 字节，安装 2,923,784 字节，SHA-256
`544b925dc1c56d5c9ad040e1e9d70b2511d0b344456de467b0a064936e011905`。
本轮重新通过隔离的原生五层 PvP/PvE 加载、损坏校验、修复、离线重启及删除。
缩放手感、楼层切换视觉和实际标记 GUI 验收未执行。

### 2. Reserve：PARTIAL 素材，整体 BLOCKED

固定 SPT 上述 revision 下 `Plugin/Resources/Maps/Reserve_TarkovData/`：

| 输入 | 字节 | SHA-256 |
| --- | --- | --- |
| Layers/Reserve-Ground_Level.svg | 69,660 | `804dec62ad3ec4dc74f6bbb973c342165e9c373750be275b22ff3c60151a9d94` |
| Layers/Reserve-Bunkers.svg | 3,181 | `2436a8e2662016383f56ed14b5eb9f7f0c5fcc91352733a8db4eb5bec546806b` |
| Reserve_TarkovData.jsonc | 20,134 | `a68466f405add8c7d3ad8c1e757457fbc556ad80741163e5cb2eac14c630c5d0` |

Shebuka 原作；SPT-DynamicMaps 提供分层版本；同目录 `Shebuka-LICENSE.md` 是资产的
CC BY-NC-SA 4.0 文本，SHA-256 `1349a4b6148492b44f629e64eed676612e234fe9a839e4f3b277c1482c8849f1`。
来源链接、原 SVG、完整许可、上游反作弊声明和 Noven 转换记录随本地候选保存。
JSONC 只作本地校准输入，不套用 SVG 许可分发它。

检查了组合 SVG 的实际组：Ground_Level 包含地形、道路、围栏、树木、岩石、铁路、
地堡入口、Buildings 和 Misc；另一组 Bunkers 只有两块路径。没有被隐藏名称掩盖的
2nd/3rd/4th/5th 几何。NormalMaps 的复制件也不增加楼层。
不能由建筑地面轮廓推导房间、楼梯和通道的上层布局。

本轮生成两层 1024x929 预览、4096x3715 细节及两种原生图像路径，**不生成 NVR1**。
按来源旋转 180、x[-303.5,292]、z[-275,271.5] 转换到原生 180、x[-303,289]、
z[-293,244]；世界轴映射保留，不以 API 的朝向值 195.209 替换底图投影角。
这些是来源标定下的候选，不是独立实测通过。
原生 Ground/Bunkers 高度区间与 SPT 简化两层分类不同，故没有导入其高度规则。
还需四层合法素材、逐物体楼层对应、独立图像地标及原生完整加载验收。

### 3. Lab：新增三层完整格式候选，但不是几何 PASS

Shebuka Labs.svg 固定到上述 SVG 项目 revision，SHA-256
`099a9eaabc305431d906151e03c45d6f06bb885ec46234735e93cc2ab02a222a`。
图像 viewBox 720x586；Technical_Level -> Technical、First_Level -> Base、
Second_Level -> Second_Level；未改原生显示顺序、高度边界、270 度投影或真实标记。
原 JSONC SHA-256 `d7929df2f686a01dcd7c13a608c9cc98f8c4e0866a668994828df7ddeeb342ad`。

本轮从固定 SVG 生成三层 1024x746 预览和 4096x2985 细节；每层保留原 SVG、
完整 CC 许可、上游声明、来源和转换记录。来源包含矢量箭头，不引入外部图标/栅格。
`.satellite` 是 0.1.3 固定文件名，其内容为新生成 SVG 衍生图，不是卫星底图。

最终**未签名本地候选** `5b0fc42d86f7744a585f9105-0.0.1.nvr`：
1,591,243 字节，安装 1,590,220 字节，SHA-256
`dd1ffd112d896083b07ca67910bf5550d91c9c8740f7c6ab2fc7f7f8b7a6fb8e`。
真实来源离线重复生成字节一致；原生三层 PvP/PvE 加载、PNG 解码、损坏验证、修复、
离线重启和删除通过。`publishable:false`；没有 GitHub asset ID。

重新运行 19 点**世界标注**比较仍不等于 SVG 像素测量；来源校准也不是独立证据。
每层独立图像/世界配对仍为 0/0，留出图像 RMSE/max 为 N/A。
不拿撤离区域中心冒充门槛，不以旧图范围外的中心证明 SVG 过时，也不据此发布。
Technical 候选在目标画布上边缘有有效 alpha，需要实物边界核验，不能仅凭非空渲染
声称完整无裁剪。

### 4. Dark Lab：共享投影不是共享布局的完整证明

Tarkov.dev 当前布局的 `the-lab` 配置显式 `altMaps: [the-lab-dark]`；本地三层、
投影、高度区域也相同。此证据支持坐标框架共用，**不证明所有房间、可达区域相同**。
保留 regular/PvE 数据均为普通 Lab 7 个撤离、17 把锁、15 个开关、134 个出生点；
Dark 为 0/0/0/145。缺失字段不是“没有门/撤离”的证明，出生点也不能验证墙角。
没有可验证的 Dark 物理差异表或独立图像地标，因此未复制 Lab 包、未生成假完整资源。

### 5. Icebreaker：找到合法性研究线索，但不是 16 层校准资源

原默认素材仍来自 TarkovBOT.eu，其 tile 可访问性不构成图片再分发许可。
本轮读取 [re3mr 原作者发布页](https://reemr.se/icebreaker/) 和
[作者 FAQ](https://reemr.se/about/)，并完整校验其
[1.7 原图](https://reemr.se/maps/Icebreaker/re3mrIcebreaker.png)：
7680x4320，4,161,523 字节，SHA-256
`13d5cead3b2949981f4dfb8445b2280f3a8e5cc9ba30cee42a1c301e311d3329`。
初次 HTTPS 200 超时后精确续传 HTTP 206，最终 PNG 完整解码；这是来源检索，
**不是 Noven 生产 NVR1 下载验收**。

可见作品是 14 幅 deck 拼图（10 至 -3），不是可直接加载的 16 层同投影图片。
Engine_Room_upper、Fuel_Pumps_lower 需明确在对应甲板上的实体区域/高度关系，
Control_Room 与 Lower Automation 的同名/异名对应也尚未证实。
不能裁出 14 张后复制两张凑 16 层。原生投影 142.5x131.9 与作品船体标示的
34x168 米不是可直接互换的校准尺寸；不据此擅自更改原生世界坐标。

许可须逐元素处理：作者页面声明 CC BY-NC-SA 4.0，但作品版权链接实际指向 2.0；
FAQ 另请网站/app 再托管者联系作者。这些声明需准确记录，不自行发明“伴侣 app 禁止”
条款，也不把站点软件许可当素材许可。原图底部明确将**侧视船体**归于 BSG，任务区域
信息和协作者也有独立归属。作者的开放许可不是这些独立内容的自动授权。
本轮没有下载 RAR/PSD/游戏文件，也未向作者发送消息；只保留研究原图，不打包、不发布。
下一步可研究排除侧视图/独立图标后的作者自绘甲板、确认具体 CC 版本、取得逐层配对
和世界地标；不能直接复制有独立权利声明的素材或把栅格追描称作原创。

### 6. Tutorial：资源包不能补 Core 楼层契约

稳定 ID 已存在，两模式快照均有 17 个出生点，撤离/锁/开关均未提供；没有原生
floor/reference/extents。当前 Tarkov.dev `maps.json` 只把标准 Ground Zero 别名
到 Ground Zero 21+，**没有** Tutorial 别名或布局定义。
`MapPage::BindMapImages()` 对缺失参考/楼层明确返回 missing-reference；NVR1 只容许
`maps/` 下数据，不能授权替换 `assets/data/` 的 Core TSV。
需先取得教程可达范围、楼层和与普通版本的独立等价/差异证据，再通过受测的未来 Core
数据版本交付。没有凭名称复制 Ground Zero 文件，也未为此改动已发布 0.1.3。

## 本地复验与验证边界

使用已有 `resvg-py==0.5.0`、`Pillow==12.2.0`，未引入依赖。工具不安装入 Core。

```powershell
$env:PYTHONPATH = "$PWD\build\map-tools;$PWD\tools\resources"
$env:PYTHONDONTWRITEBYTECODE = '1'
python -m unittest discover -s tools/resources -p 'test_*.py' -v
python -m unittest discover -s tools/maps_generator/tests -p 'test_*.py' -v
python tools/resources/prepare_recovery_svg.py --assets assets --map-id 5704e5fad2720bc05b8b4567 --output <NEW-RESERVE-DIR>
python tools/resources/prepare_recovery_svg.py --assets assets --map-id 5b0fc42d86f7744a585f9105 --output <NEW-LAB-DIR>
# 离线复验：增加 --upstream <上述目录/upstream>，固定哈希不符即失败。
python tools/resources/audit_map_coverage.py --assets assets --catalog <SIGNED-PRODUCTION-CATALOG> --packages <PRODUCTION-PACKAGES> --candidate <CUSTOMS-CANDIDATE-CATALOG> --candidate <LAB-CANDIDATE-CATALOG> --output <NEW-REPORT.json>
```

| 检查 | 本轮结果 |
| --- | --- |
| 资源工具离线测试 | 37/37 PASS；新增 7 项覆盖候选/生产区分、两层不伪装全包、确定性、保留旧输出、写前预算、PvE 合同及源哈希失败 |
| Maps generator 离线测试 | 45/45 PASS |
| 实际来源候选重复输出 | 最终 Lab NVR1 字节一致；审计报告重复结果一致 |
| 签名和现有包完整性 | 原生 CNG 验证生产相同包络和 11 包 PASS；不重新签名 |
| Customs / Lab 原生生命周期 | 本轮隔离 native tool 两地图均 PASS；不是 GUI 或实物几何证明 |
| PvP/PvE floors/references/extents | 本地三份 TSV 各自逐行一致；未改动 |
| 图片观察 | 5 张新候选预览非空、可解码；不能替代独立几何或用户缩放操作验收 |
| 世界标注诊断 | Lab 原有 19 点脚本成功；仅世界框架比较，非图像校准 |
| diff / 文件审计 | `git diff --check` PASS；未提交候选二进制、快照、日志或机器路径 |
| 新地图真实远端生命周期 / GUI | 未执行；无合格生产候选，且本轮不允许改生产频道 |
| 完整 Debug/Release 构建 / CTest | 未执行：无 C++、Core 数据、UI、安装及安全运行代码改动；不宣称完整里程碑 PASS |

仅工具/测试、生成的只读覆盖 JSON 和公开报告发生变化。
既有候选 223 文件 / 25,453,839 字节及其保留摘要未变；没有清理旧目录、终止进程、
读取用户状态或签名私钥。新增工作在忽略的 `build/` 隔离根，不写真实 LocalAppData，
不再创建多份大型应用构建/安装包。机器路径、精确占用和最后提交号另在交付中给出。

**结论：本轮本地补全与审计取得可复验产物，但六张均未通过全部发布标准；保持
11 项生产目录不变。独立几何、缺失楼层/权利及 Tutorial Core 契约是实际剩余阻塞。**
