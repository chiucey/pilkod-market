---
name: blender-h3-dcc
description: Use for Blender white-model handoffs, mcode-dcc-inbox assets, H3 rendering, Blender extension installation, or conversational Blender blockouts. M3 analyzes and validates the video; H3 renders it while preserving the source shot structure.
---

# Blender 白模 → H3 成片（参考适配与密集动作验收版）

白模是最终视频的**时空合同**。H3 只能改变外观，不得改变镜头、切点、相机轨迹、
动作时序、场景布局、相对位置、可见性、遮挡和明确的光照空间关系。
每个可见源实例必须一对一守恒：可以换材质和设计，但不得合并、拆分、删除、替换或重组成
新的背景构图。

M3 是工作流 Agent：完整观看视频、建立 Render Contract、组织 H3 生成，并做最终
多模态验收。不预设主体必须是人：同一套合同必须能处理单人、多人、动物、载具、
产品、建筑、纯环境和特效。外观参考由显式路由决定作用于全世界、指定实体、环境、
材质或灯光，不根据参考图中最显眼的内容自行缩小作用范围。脚本只负责
帧数、时长、画幅、结构优先的 prompt 预算、锚点和切镜候选等确定性工作，不能代替
M3 的视觉判断。

## M3 执行纪律

按下面 6 个阶段顺序执行。脚本未通过时不得进入下一阶段。

- 不手写 H3 结构化 prompt；必须使用脚本生成的 `h3_prompt.txt`。
- 不手工裁剪、改写或二次优化 `h3_prompt.txt`。脚本必须把完整语义压入 6500 字符
  安全预算，并保留全部镜头、实体和锚点标签。
- 不修改脚本写入的源视频数据、时间码、镜头数和硬约束。
- 不删除 `source_inventory` 条目，不把多个 `source_id` 当作一个可丢弃的“环境组”。
- `M3_FILL` 表示必须观看视频后填写；不得原样保留或凭缩略图猜测。
- 为了让 M3 稳定执行，每个描述字段只写一个可见事实，不写推理过程。anchor 中的
  `orientation / motion_state / spatial_relations` 各用 3–8 个英文词；同一事实不在多个字段重复。
- 美术质量不能抵消结构失败。新增切镜、跳轴或动作改写一律失败。
- 某个主体好看不能抵消其他实体失配。除非参考路由明确限定，默认要求所有实体、材质、
  灯光和氛围属于同一个世界。
- “保留白模”只表示保留运动、屏幕位置、包围范围、数量、遮挡和时序；绝不表示
  保留源建模材质、不完整代理结构或视口占位外观。
- 每个实体的运动合同都必须保持；不得把连续运动改成停止，也不得把静止实体自行动起来。
- 参考图只提供允许的外观属性。参考中的定格姿态、取景、布局、额外持有/附着物、夸张变形物、
  新实体和文字都必须先识别并隔离，不得进入实体最终设计。此规则适用于任何题材，不依赖人物、武器或椅子等特例词。
- 不得用“仍是一镜到底”抵消镜头路径失配。跟拍、环绕、推拉、摇移、目标距离、方位角、仰俯和焦距变化
  必须分开判定。
- 未通过最终验收，不得把视频称为“渲染完成”。
- 与用户沟通使用用户的语言；合同和 appearance JSON 的描述字段使用清晰英文，
  便于脚本直接生成 H3 prompt。

## 1. 定位素材

优先使用用户给出的 `mcode-dcc-inbox/<时间戳>/`：

- 新扩展的粘贴指令只会明确给出一个 `preview_video.mp4`。它是唯一待渲染视频；自动检查其
  同目录的 `manifest.json` 作为 preflight 结构侧车，不遍历或整包加载收件夹，更不得把
  manifest JSON 全文写进对话或 H3 prompt。
- 兼容旧指令时，如果只拿到收件夹路径，就解析该目录下 manifest 的 `files` 条目来确定对应
  `preview_video*.mp4`；不要读取 `instruction.txt`，也不要把目录内所有文件一起作为模型输入。
- 新扩展导出的 manifest v3 包含 `structure_evidence`：Blender 对每个可渲染源对象分配稳定
  `source_id`，并采样对象的屏幕包围盒、世界位置/尺寸以及相机位姿、镜头焦距和偏移。
  有该证据时优先使用，但仍须对照视频检查遮挡和语义。
- 文件夹失效时，检查 `~/mcode-dcc-inbox/` 最新目录并核对 manifest。
- 一个都没有时，请用户先从 Blender 发送白模。

只处理已导出的素材不需要启动 Blender。安装扩展、再次导出或后台搭 Blender 场景时，
先读 [Blender 操作](references/blender-operations.md)，并完成其中的安装验证。

## 2. Preflight 与 Render Contract

为每个待生成镜头创建独立工作目录，然后运行：

```bash
python3 "<技能目录>/scripts/m3_render_workflow.py" preflight \
  --source "<preview_video.mp4>" \
  --manifest "<manifest.json>" \
  --workdir "<工作目录>"
```

脚本生成 `preflight.json`、`render_contract.json`、`appearance.json` 和
`source_anchor_frames/`，M3 先看完整视频，再用锚点帧逐项填写合同。

M3 必须完整观看源视频，再填写 `render_contract.json`：

- `watched_full_source` 改为 `true`。
- 先完成 `source_inventory`。有 Blender `structure_evidence` 时，脚本已按稳定 `source_id`
  列出所有采样中可见的源对象；M3 核对名称、类型、首末可见时间和 `identity_cues`，
  不得删除。旧 manifest 只有 `V001` 占位时，M3 必须通过完整视频和锚点建立
  `V001...Vnnn` 的可见实例清单；每个独立座位、块体、支撑物、前景遮挡物或重复实例
  都需要独立 `source_id`。
- `entities` 是语义/风格分组，不是删减源实例的手段。每个 entity 的
  `source_instance_ids` 必须精确列出成员，`instance_count` 必须与数量一致，
  `conservation_rule` 保持 `one_to_one_no_merge_split_delete_or_replace`。同风格的重复实例
  可属于同一 entity，但 H3 仍必须逐个保留。所有 inventory id 必须被分配且只分配一次。
- 每个 entity 填写 `entity_class`、`importance`、源视频角色、结构约束和自己的
  `motion_contract`。`motion_contract.mode` 只能是 `locomotion / rigid_travel / articulation /
  manipulation / deformation / effect_evolution / static / camera_only`。`static` 也是硬约束，
  表示实体不得被自行动画化。
- 逐镜头填写 `camera_contract`。分开标注镜头运动类型、跟踪目标、世界路径、目标距离趋势、
  方位角趋势、仰俯趋势、焦距趋势、屏幕构图规则和禁止替代。`motion_type` 只能是
  `static / tracking / dolly / orbit / pan_tilt / crane / handheld / compound`。不得把主体自身
  移动误当相机推进，也不得把跟拍误写为环绕或正面居中推近。
- 把源视频中的持有、接触、支撑、依附、搬运、交错遮挡等关系写入 `interaction_contracts`；
  无交互时保持空数组。这一层阻止 H3 自行增加握持物、落地支撑或改变附着关系。
- 逐个填写 anchors。`composition` 记录景别、画面平衡与深度；`tracked_instances` 必须在
  每个锚点精确出现全部 `source_id`。每个追踪项填写可见性、中心 X/Y、包围盒宽/高百分比、语义化朝向、
  当前运动状态和与其他实体/画面地标的相对关系。百分比按整幅画面左上角为 0、右下角
  为 100 估算即可。`offscreen` 实体的四个数值写 `null`，并在关系字段写明离开哪一侧。
- Blender 证据已填入的包围盒只需 M3 核对和修正遮挡状态；纯视频模式由 M3 估算。
  即使某个实例当前在画外，也必须保留一条 `offscreen` 记录，避免后续进画时被遗忘。
- `shot_scale` 只能使用 `extreme_wide / wide / full / medium_full / medium / close /
  extreme_close`。朝向用适合当前实体的短英文描述，例如生物的视角、载具的车头指向、
  产品的正面方位或特效的扩张方向；不强迫非人实体使用人体朝向枚举。
- 单镜头保持 `shot_count: 1`；不要因为画面变化自行增加 Shot。
- 有切镜候选时必须查看候选前后画面，再决定是否为真实切镜。

提交合同前做一次八域覆盖检查：镜头/切点、相机外参路径、镜头内参/焦距、源实例数量与身份、
逐实体运动、接触/附着交互、深度/遮挡/出入画，以及光照空间逻辑。任意一域只写“保持原样”而没有可检查事实，
都视为未完成。

完成后运行：

```bash
python3 "<技能目录>/scripts/m3_render_workflow.py" check-contract \
  --contract "<工作目录>/render_contract.json"
```

失败就修正 JSON，不得绕过检查。

## 3. 建立全场景风格合同

用户尚未说明时，只问一次：

> 这段白模想怎么渲染？
> - 一键渲染（推荐）：M3 根据造型、动作和镜头选择稳定风格。
> - 自定义渲染：用一句话描述最终效果，或提供效果参考图。

填写 `appearance.json`。先写只含美术语言的 `style_source_summary`（不得描述参考图姿态、构图或物件关系），再对每个参考输入建立一条
`reference_routes`；没有外观参考时保持空数组，不虚构参考。

### 参考图结构支配门

提交前必须先判断每张参考图的用途和结构支配风险，不能只靠 prompt 声明“不要继承姿态”。

1. 先确定用途：用户需要精确保留参考对象身份、完整造型或装备时为 `identity_and_style`；
   只需要画风、色彩、材质、细节密度或灯光时为 `style_only`。不明确时默认 `style_only`。
2. 出现以下任一情况就标记高风险：完整落地/锁定姿态或完整对象展示；居中静态构图与白模运动、景别冲突；
   参考含白模没有的大型持有、附着、拖曳或遮挡轮廓；背景透视或场景布局占主导；目标风格和材质在图中占比过小；
   参考主视角与白模主要视角明显矛盾。人物、动物、载具、产品、建筑和纯环境都使用同一判断，不按题材写特例规则。
3. `style_only` 且高风险时，优先使用一张**非破坏性的风格裁切副本**：保留能代表身份线索、色板、材质、
   表面细节和光照的区域，排除完整落地姿态、展示台/地平线、白模不支持的附着轮廓和主导背景布局；不得拉伸，
   不覆盖原图，并先目视确认裁切仍清晰。不同题材都按“保留外观证据、减少完整结构模板”处理。
4. 使用风格裁切是为了降低结构竞争，提交时只传裁切副本，不同时传原图；否则原图会把被排除的构图重新带回 H3。
   无法可靠裁切时保留原图并向用户说明结构风险，不擅自删除用户要求保留的身份信息。
5. `identity_and_style` 不得为了稳定性静默裁掉用户要求的完整造型。保留原图、完整记录风险，并明确说明：身份/装备保真
   与白模动作/镜头保真可能竞争。若结构优先，建议用户另给中近景、多视角或与白模动作相容的参考。
6. 无法判断问题来自画幅比例还是构图内容时，不凭一次随机生成下结论。固定白模、prompt、参数和种子条件，使用同图原版与裁切版
   做 A/B；可行时各生成两次。只有同方向重复出现的差异才用于修改默认策略。

- `reference_routes.scope` 只能使用 `global_world / entity_set / environment_only /
  materials_only / lighting_only`。`entity_set` 和 `environment_only` 必须在 `target_entities`
  中列出实际 entity label；其他 scope 可留空表示全局。
- 参考中某个人或物最显眼，不等于参考只对它生效。用户说“整个画面按这个风格”时必须
  使用 `global_world`；用户明确限定对象或属性时才使用更窄路由。
- `safe_style_attributes` 只写 1–6 条短的外观属性，例如时代、形制语言、色彩、材质、细节密度、
  灯光；不得写姿态、镜头、布局、运动或新增对象。脚本会完整保留这些短项，不再把数组压缩成残缺字符串。
- 逐张参考填写 `reference_structure_review`。`risk_flags` 只能选：`explicit_pose / camera_or_framing /
  environment_layout / held_or_attached_elements / large_deforming_or_occluding_elements /
  source_unsupported_entities / text_or_branding`；把具体风险写入 `blocked_reference_details`，并保持
  `mitigation_applied: true`。完整展示姿态归入 `explicit_pose`，主体占比/景别冲突归入 `camera_or_framing`，
  背景透视主导归入 `environment_layout`；高风险图必须先完成上面的原图/裁切选择，不能只填风险后原样提交。
  没有风险时两个数组都可为空。
- `structure_transfer_policy` 必须保持
  `appearance_only_no_pose_framing_motion_layout_or_new_elements`。脚本还会不可压缩地写入完整排除集：
  pose、body configuration、camera、framing、motion、timing、layout、count、bbox、visibility、occlusion、
  source-unsupported elements。参考图与白模冲突时，永远以白模时空合同为准。
- `global_style_bible`：完整填写世界年代、视觉语言、色板、材质语言、环境设计、
  物件设计、灯光与氛围；每项只写可见设计要点，不重复时空结构描述。
- `entity_appearances`：键必须与合同里的全部 entity label 完全一致，每项都填写
  `semantic_target`、`final_materials_and_detail`、`style_route`，并保持脚本给出的
  `source_visual_policy / silhouette_policy / source_unsupported_additions`。每个实体
  都必须有明确成品设计；`final_materials_and_detail` 必须写材质、
  构造、边缘处理和表面光照响应。
- 所有实体的 `source_visual_policy` 都保持脚本给出的 `spatiotemporal_evidence_only`。
  这表示白模给出运动、尺寸、轮廓、位置、数量、可见性、遮挡和时序证据，但不把占位外观
  当作最终设计。
- `silhouette_policy` 保持 `stay_within_source_bounds_and_articulation_envelope`；
  `source_unsupported_additions` 必须保持空数组。参考中有但白模没有的持有物、附着物、披挂、文字或背景对象，
  只能记入路由的 blocked details，不能写入 `semantic_target` 或 `final_materials_and_detail`。
- 不修改 `blockout_rejection`。语义不确定的占位体也必须在原包围范围内选择符合
  World Style 的成品设计，禁止保留源建模占位感、默认视口材质、不完整的代理结构或未经设计的占位外观。
- `sound`：声音方向。
- `watched_references`：确认外观输入后设为 `true`；没有参考图也设为 `true`，
  表示已确认无需读取。

`global_world` 下，从参考提炼年代、形制、材质、色彩、细节密度和氛围，并应用到
整个画面中的全部实体，同时保持白模规定的数量、位置、尺度、可见时机和遮挡关系。
参考图不得覆盖白模的时空结构；用户未要求时不增加实体、品牌、对白或可读文字。

## 4. 生成 H3 prompt 并提交

先按 `preflight.json.timeline_plan` 准备 H3 技术参考：

```bash
python3 "<技能目录>/scripts/h3_timeline_contract.py" prepare-reference \
  --source "<preview_video.mp4>" \
  --output "<工作目录>/h3_reference.mp4" \
  --num-frames <timeline_plan.num_frames>
```

若 `strict_single_pass_recommended` 为 `false`，不要直接提交；读取
[分段续接](references/segmented-continuation.md)。

生成固定 prompt：

```bash
python3 "<技能目录>/scripts/m3_render_workflow.py" build-prompt \
  --contract "<工作目录>/render_contract.json" \
  --appearance "<工作目录>/appearance.json" \
  --output "<工作目录>/h3_prompt.txt"
```

脚本同时生成 `h3_prompt_budget.json`。必须确认：

- `within_budget` 为 `true`。
- `protected_content_valid` 和 `ready_to_submit` 均为 `true`。
- `prompt_characters` 不超过 6500，且必然低于 Pilkod 官方在线 H3/CLI 提交通道的
  7000 字符限制；不要把该数字描述成 H3 模型底层上下文极限。
- `protected_content` 包含全部镜头标签、实体保留项、锚点时间码以及结构/风格区块。
- 检查 prompt 中的 `[INSTANCE REGISTRY]`、`[ENTITY CONSERVATION]`、`[INTERACTIONS]`、
  必要时的 `[STATIC LOCK]` 和每个 `source_id`；任何
  source id 缺失都不得提交。
- 检查每条参考路由的 `safe= / risks= / block= / policy= / exclude=` 都完整出现且没有省略号；
  任一安全属性或被阻断细节缺失都不得提交。

脚本使用可扩展的紧凑结构而不是重复自然语言：`[INSTANCE REGISTRY]` 一次性映射全部
source id，连续实例使用范围表达，静态实体合并为一条 `[STATIC LOCK]`，锚点用
`V/P/O/D` 编码逐实例可见性、包围盒和动态状态。它仍保护全部 source id、一对一数量、
逐锚点可见性/位置/包围盒、主要/动态实例的朝向与运动、动态实体运动锁、完整静态实体锁、
镜头分解、交互关系、参考路由、实体语义与材质映射以及白模占位外观拒绝规则。
即使原始合同超过一万字符，
也不得由 M3 取前
6991 字符、删除后半段锚点或自行总结；预算检查失败就停止提交。

加载 `video-creater` 插件的 `write-h3-prompts` 技能并提交，固定参数：

- 模型：`MiniMax-H3`。
- 任务：Ref2VA `video editing`，不是宽松 reference generation。
- `reference_video_paths`：`h3_reference.mp4`。
- 用户外观参考图才进入 `reference_image_paths`；其作用范围必须与 `reference_routes`
  一致。每条路由只提交“参考图结构支配门”选定的原图或裁切副本，不得为了保险把两者同时提交。
  `global_world` 时不得只提取参考中最显眼实体的外观。
- prompt：原样使用已通过预算报告的 `h3_prompt.txt`，不要再让 prompt 优化器增删、
  总结或裁剪。
- duration：使用 `preflight.json.timeline_plan.generation_duration`。
- 先生成基础分辨率。结构通过后才允许 2K Regenerate。
- 付费确认后只提交一次。

单镜头且在接口上限内必须整段生成，不得预先切成 2–3 秒，也不得只用首尾帧
替代参考视频。

## 5. 技术还原与 QA 包

H3 返回后先映射回白模时间轴和画幅：

```bash
python3 "<技能目录>/scripts/h3_timeline_contract.py" conform-result \
  --source "<preview_video.mp4>" --result "<H3 原始结果>" \
  --output "<工作目录>/conformed_result.mp4"
```

再生成 M3 验收包：

```bash
python3 "<技能目录>/scripts/m3_render_workflow.py" prepare-qa \
  --source "<preview_video.mp4>" \
  --result "<工作目录>/conformed_result.mp4" \
  --contract "<工作目录>/render_contract.json" \
  --appearance "<工作目录>/appearance.json" \
  --workdir "<工作目录>"
```

脚本生成 `qa_review.json`、锚点目录 `qa_frames/` 和 9–21 个等间隔动作对照帧目录
`qa_motion_frames/`。M3 必须：

1. 完整观看白模和还原后的成片。
2. 查看全部成对锚点帧、全部 `motion_frame_pairs` 及新增切镜候选。背景随相机产生的视差
   不能当作主体自身运动；必须分别判断主体根节点位移、关节/形变相位与接触时序。
3. 先按 `source_inventory` 逐项盘点，不按语义大类笼统评价。对每个 source id 填写
   `source_instance_reviews.status`：只能是 `preserved / missing / merged / split / replaced`，
   并给出时间码证据。任意一个不是 `preserved` 都自动导致 `structure_failed`。
4. 填写全部 `primary_screen_space_reviews.observed` 数值与时间码证据。脚本会自行计算主要实例
   的中心点和包围盒误差，不能由文字结论替代算术。每个可见实例中心点误差不超过 8 个百分点，
   包围盒宽度/高度误差不超过 10 个百分点，可见性、朝向和
   空间关系一致。多个源实例被组成一个新物件，或某个前景遮挡物没有在应出现的时间出现，
   分别判 `source_instance_conservation: false` 和 `source_instance_visibility_and_occlusion: false`。
5. 对照 `camera_contract_targets` 分开检查镜头运动类型、跟踪目标、世界路径、目标距离、方位角、
   仰俯、焦距和构图重心。“无切镜”不等于通过；跟拍被改成推近、环绕、反打或居中展示，均判
   `camera_motion_decomposition: false`。
6. 对照 `entity_motion_targets` 逐实体检查运动模式、方向、速度变化、连续性和禁止替代行为；
   对每个非 static/camera_only 实体填写 `entity_motion_reviews`：status、根位移、动作/形变相位、
   接触时序与时间码证据。status 只能是 `preserved / frozen / slowed / wrong_direction /
   wrong_phase / replaced`，三项布尔值必须逐项判断。
   运动实体被改成停止，静止实体被加入动画，或两个实体的动作被合并/对调，都判
   `entity_motion_contracts: false`。
7. 对照 `interaction_targets` 检查握持、接触、支撑、依附、搬运和交错遮挡；新增未在源视频出现的
   接触或附着关系也判 `interaction_and_contact_relations: false`。
8. 对照 `style_target` 逐实体检查是否按 `style_route` 完成语义化和材质化。任何仍像源
   建模占位、默认视口材质、不完整代理结构或未经设计的占位外观，或在不应消失时消失的源实体，都判
   `source_instance_render_completion: false`。
9. 填写 `qa_review.json` 中全部检查的 `pass` 与具体时间码证据，并设置
   `watched_full_result / reviewed_style_target / reviewed_all_comparison_frames / reviewed_all_motion_frames /
   reviewed_every_source_instance` 全部为 `true`。
10. 结构失败写 `verdict: structure_failed`；结构通过但风格失败写
   `verdict: style_failed`；两类全部通过才写 `verdict: pass`。

最后运行：

```bash
python3 "<技能目录>/scripts/m3_render_workflow.py" finalize-qa \
  --qa "<工作目录>/qa_review.json"
```

脚本会阻止技术预检失败却写 pass、漏填检查项、未完整观看、未核对风格合同，或
结构/风格任一类失败却声称完成。只要任意 source id 丢失/合并/拆分/替换、任一动态实体冻结或
运动字段不匹配、或脚本计算的主要实例屏幕误差超阈值，即使 M3 把总检查误填为 true，最终程序也会强制判结构失败。

## 6. 交付与停止条件

通过时给出简短验收摘要：时长/画幅、镜头/切点、相机、逐实体运动、场景对象、
遮挡、光照空间关系、环境/道具风格应用和全场景美术一致性。

失败时列出时间码、对象与差异，不要自动再次付费：

- 结构失败写“结构保持失败”；风格失败写“全场景风格失败”，并分别列出时间码、
  对象与差异。
- 第一次失败：展示原因和纠正方案。只有镜头连续性失败才建议分段续接；纯风格失败
  应保留整段参考视频并强化全局风格合同。
- 第二次失败：停止消耗，明确 H3 无法可靠满足本镜头合同。
- 不得用挑选局部、隐藏切镜或只展示好看的帧冒充成功。

H3 不是逐像素渲染器。本技能保证的是稳定编排和拒绝错误交付，不保证每次生成
都能通过一镜到底验收。
