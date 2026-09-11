# UE5.8 3D 游戏项目的 Codex 技能、Agent 与项目规范调研 v4

版本：2026-09-11  
适用项目：G:\NewWorld，未来 UE5.8 3D 游戏项目  
目标：把 Codex、skills、agents、MCP、AIART、AI Voice、Blender MCP 和 UE5.8 资产/工程规范整合成可执行的开发手册。  

本文不是工具清单，而是项目操作规范。后续让 Codex 做游戏功能、资产制作、UE 调试、性能分析、UI、音频或发布工作时，应优先引用本文、项目 AGENTS.md、项目上下文文件和对应 skill。

## 1. 执行结论

当前最值得采用的路线是：

1. 先建立项目级规则，而不是一开始堆工具。根目录需要 AGENTS.md，另建 .agents/ue-project-context.md 保存 UE 版本、模块、插件、平台、C++/Blueprint 边界、验证命令和资产目录。
2. 游戏开发 skill 优先安装两类：通用游戏开发技能库 gamedev-skills/awesome-gamedev-agent-skills，UE 专项 C++ 技能库 quodsoler/unreal-engine-skills。前者覆盖玩法、资产、音频、UI、关卡、发布；后者覆盖 UE C++、GAS、动画、渲染、音频、UMG、测试等更细的 API 规则。
3. 高星通用 agent/rule/plugin 仓库只选择性借鉴，不建议全量安装。wshobson/agents、ChrisWiles/claude-code-showcase、cc-sdd、ai-ready、michaelshimeles/skills 的价值主要在工作流：项目记忆、技能触发、hook/CI、review agent、证据式验收、worktree 隔离和文档回写。
4. UE5.8 本机安装已经包含实验性 AI/MCP 能力：ModelContextProtocol、AIAssistant、MCPClientToolset，以及 UMG、Niagara、PCG、AI Module 等 Toolset。本项目已选择性接入 MCP 相关 Editor Toolsets，但仍保持手动启动、tool search、staging 写入和审计优先。
5. UE live editor MCP 很有价值，但必须按阶段使用。Epic 官方 Claude 插件、UnrealClaude、VibeUE、soft-ue-cli 和社区 Unreal MCP 的共同经验是：让 AI 看到编辑器、运行 PIE、截图自检、用 Python 或工具集批量改 Blueprint/资产。对 NewWorld，UE MCP 只作为受控编辑器自动化入口，不作为可信构建系统。
6. Blender MCP 不应被当成“自动美术师”。它更适合场景查询、程序化 blockout、硬表面、模块化资产、批量修复、材质槽、pivot、碰撞、LOD、导出和截图自检；复杂有机模型、角色、表情、权重、头发、布料仍要结合 AI 3D 生成、DCC 工具和人工审美。
7. AI 资产不能从生成结果直接入库。必须走 brief、manifest、候选生成、确定 seed、成组生产、DCC 清理、UE 导入、场景内验证、Data Validation、来源记录的流程。
8. NewWorld 已完成 UE5.8 C++ 项目初始化（无用模板内容已清理）、项目级 AGENTS/skills/agents、vendored skills、资产登记模板和 MCP 工程化接入；后续重点是用检查脚本和审计模板约束每一次 AI/MCP 写操作。

## 2. 调研依据与可信度

| 来源 | 类型 | 本文采用方式 |
| --- | --- | --- |
| [OpenAI Docs: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | 官方 | Codex 指令发现顺序、32 KiB 默认限制、AGENTS.override.md、Code Review Rules |
| [OpenAI Docs: Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) | 官方 | 内置 default/worker/explorer、custom agents TOML、并行 agent 使用边界 |
| [OpenAI Docs: Build skills](https://learn.chatgpt.com/docs/build-skills) | 官方 | SKILL.md 结构、progressive disclosure、skills/agents/scripts/references 组织 |
| [OpenAI Developers: Build plugins](https://developers.openai.com/plugins/build/plugins) | 官方 | plugin.json、skills、mcp.json、插件市场、本地插件、hook 信任模型 |
| [OpenAI Docs: Best practices](https://learn.chatgpt.com/guides/best-practices) | 官方 | Goal/Context/Constraints/Done when、AGENTS.md、MCP、skills、review、scheduled tasks |
| [Epic UE5.8: Asset Naming](https://dev.epicgames.com/documentation/en-us/unreal-engine/recommended-asset-naming-conventions-in-unreal-engine-projects) | 官方 | 资产命名格式和前缀原则 |
| [Epic UE5.8: FBX Static Mesh](https://dev.epicgames.com/documentation/en-us/unreal-engine/importing-static-meshes-using-fbx-in-unreal-engine) | 官方 | FBX 2020.2、导入后 Static Mesh Editor 验证 |
| [Epic UE5.8: FBX Skeletal Mesh](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-skeletal-mesh-pipeline-in-unreal-engine) | 官方 | Skeletal Mesh、morph、LOD、root bone pivot、diffuse/normal 自动导入限制 |
| [Epic UE5.8: FBX Animation](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-animation-pipeline-in-unreal-engine) | 官方 | FBX 2020.2、单 Skeletal Mesh 单文件单动画约束 |
| [Epic UE5.8: Texture Settings](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-format-support-and-settings-in-unreal-engine) | 官方 | 纹理内存、mip、TextureGroup、DXT1/DXT5 压缩规模 |
| [Epic UE5.8: Data Validation](https://dev.epicgames.com/documentation/en-us/unreal-engine/data-validation-in-unreal-engine) | 官方 | 命令行验证、UEditorValidatorBase、C++/Blueprint/Python validator |
| [Epic UE5.8: Common UI](https://dev.epicgames.com/documentation/en-us/unreal-engine/common-ui-plugin-for-advanced-user-interfaces-in-unreal-engine) | 官方 | 多层 UI、跨平台输入路由、焦点和按钮提示 |
| [Epic UE5.8: UMG Fonts](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-fonts-with-umg-in-unreal-engine) | 官方 | UMG 自定义字体必须使用 Font Asset，当前支持 Runtime cached |
| [Epic UE5.8: Audio Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/audio-engine-overview-in-unreal-engine) | 官方 | USoundWave、Sound Cue、attenuation、submix、Property Matrix |
| [Epic UE5.8: Localization](https://dev.epicgames.com/documentation/en-us/unreal-engine/localization-overview-for-unreal-engine) | 官方 | FText、ICU、String Tables、Localization Targets、LocRes |
| 本机 UE5.8: ModelContextProtocol.uplugin / Settings / ClientConfig | 本地源码 | Unreal MCP、默认端口和路径、ToolsetRegistry 接入、Codex .codex/config.toml write-once |
| 本机 UE5.8: AIAssistant.uplugin / AIAssistantConfig / SlateQuerier | 本地源码 | EditorOnly AI Assistant、默认 embedded URL、Slate UI 上下文查询、Python/WebBrowser 依赖 |
| 本机 UE5.8: UMGToolSet / NiagaraToolsets / PCGToolset | 本地源码 | meta=(AICallable) 工具、Widget/PCG/Niagara 的 AI 可调用编辑能力 |
| [Top3D: Claude Code + Unreal Engine 5](https://www.top3d.ai/learn/claude-code-unreal-engine) | 实战文章 | UnrealClaude + VibeUE 组合、截图自检、Blueprint/Python、灰盒到资产替换 |
| [Top3D: AI 3D Character Pipeline 2026](https://www.top3d.ai/learn/ai-3d-character-pipeline-2026) | 实战文章 | AI 角色从概念到 rig、retopo、UV、bake、Albedo、AccuRig、权重、UE retarget |
| [Top3D: Build a UE5 Game Level in One Day](https://www.top3d.ai/learn/build-ue5-game-level-one-day-ai) | 实战文章 | 概念拆件、AI 3D、Blender 清理、Substance/贴图、GLB/UE 场景组装 |
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | 社区 | Codex MCP 配置、Blender 场景查询/修改、Python 执行、Poly Haven/Sketchfab/Poly Pizza/Hyper3D/Hunyuan3D |
| [arjun988/blender-skills](https://github.com/arjun988/blender-skills) | 社区 | 94 个 Blender skills、reference image match、blockout 到 Unreal export 的技能链路 |
| GitHub API 快照 | 社区 | 2026-09-11 星数和仓库描述，仅作为热度和维护度参考 |

## 3. 高星 GitHub 仓库调研与采纳建议

星数为 2026-09-11 快照。星数不是质量证明，只表示社区关注度和可参考程度。

| 仓库 | 星数 | 与本项目关系 | 建议 |
| --- | ---: | --- | --- |
| [wshobson/agents](https://github.com/wshobson/agents) | 39558 | 多 harness agent/plugin 市场，覆盖 Codex、Claude、Cursor、OpenCode 等 | 借鉴插件结构、agent 分类、plugin-eval、跨 harness 生成；不要全量安装 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 34044 | 1000+ agent skills 索引 | 用于发现可借鉴技能，不作为项目依赖 |
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | 28120 | Blender MCP，支持 Codex 配置、场景查询/修改、Python 执行、Poly Haven/Sketchfab/Poly Pizza、Hyper3D Rodin、Hunyuan3D | 高价值借鉴。后续可作为 Blender 自动化候选，但本次不安装 |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | 25810 | 大型 skills/agents/plugins 库，声称支持 Codex | 只挑 skill-security-auditor、agent-designer、self-improving-agent、prompt 工具类思想 |
| [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | 24994 | 子 agent 角色索引 | 借鉴角色边界，不直接复制大型角色集合 |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | 15024 | Claude skills 索引 | 用于补充可迁移 skills，需二次筛选 |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 53848 | Claude Code 资源大合集 | 作为资源入口，不作为规范来源 |
| [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | 40755 | Cursor rules 集合 | 借鉴分层 rules 思路，UE 规则需重写成 AGENTS.md/skills |
| [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) | 6062 | 项目级 CLAUDE.md、skills、agents、commands、hooks、GitHub Actions 示例 | 高价值。借鉴技能触发、自动质量门、review agent、定期文档同步 |
| [steipete/agent-rules](https://github.com/steipete/agent-rules) | 5692 | rules/knowledge 旧仓库 | 仅借鉴思想。README 已说明主要转向新仓库 |
| [gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) | 3661 | SDD harness，把批准规格转成长任务实现 | 借鉴规格驱动开发：先批准 spec，再执行，适合 UE 功能和资产批量生产 |
| [ciembor/agent-rules-books](https://github.com/ciembor/agent-rules-books) | 2748 | 从 Clean Code、DDD、Clean Architecture 等转成 AGENTS/rules | 借鉴“经典工程原则压缩成 agent 规则”的方式 |
| [htdt/godogen](https://github.com/htdt/godogen) | 6823 | Claude/Codex 自动游戏生成，Godot/Bevy/Babylon，不是 UE | 借鉴 proof over claims、引擎指南、运行结果截图/录像验收、资产生成 skill |
| [chongdashu/unreal-mcp](https://github.com/chongdashu/unreal-mcp) | 2076 | UE5.5+ MCP，Actor、Blueprint、节点图、编辑器 viewport 控制 | 借鉴最小 Unreal MCP 工具面；实验状态，不直接接入正式项目 |
| [flopperam/unreal-engine-mcp](https://github.com/flopperam/unreal-engine-mcp) | 1082 | Unreal MCP 早期实现，项目状态已转向商业 Aura | 只做历史参考，不作为安装候选 |
| [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) | 932 | 73 个游戏开发 skills，含 Unreal 5.8、资产、音频、UI、玩法、发布 | 第一优先安装。适合 Codex/Gemini/Claude 等 Agent Skills |
| [Natfii/UnrealClaude](https://github.com/Natfii/UnrealClaude) | 902 | UE5.7 + Claude Code，MCP，截图和 actor 操作 | 借鉴“让 AI 看见 viewport”的闭环；UE5.8 兼容性需验证 |
| [ChiR24/Unreal_mcp](https://github.com/ChiR24/Unreal_mcp) | 863 | C++ Automation Bridge + TypeScript MCP，控制 UE 编辑器 | 借鉴原生桥接方式；接入前先审计写操作和 UE5.8 兼容 |
| [michaelshimeles/skills](https://github.com/michaelshimeles/skills) | 680 | AGENTS.md workflow template，worktree、证据、review loop | 借鉴“隔离工作、证据交付、review 后回写规则” |
| [kevinpbuckley/VibeUE](https://github.com/kevinpbuckley/VibeUE) | 675 | Unreal vibe coding 工具，Blueprint/Python/MCP 思路 | 借鉴 Blueprint/Python 自动化和 live editor 验证 |
| [prajwalshettydev/UnrealGenAISupport](https://github.com/prajwalshettydev/UnrealGenAISupport) | 644 | UE GenAI/MCP 插件，OpenAI、Claude、Tripo、Hunyuan3D、ElevenLabs 等 | 借鉴插件能力地图，谨慎评估依赖和 UE5.8 兼容 |
| [microsoft/Resource2Skill](https://github.com/microsoft/Resource2Skill) | 519 | 从人类资源蒸馏可执行 skills，覆盖 Blender、CAD、UE5、REAPER 音乐制作等 | 用于建设自有资产技能库的方法论 |
| [quodsoler/unreal-engine-skills](https://github.com/quodsoler/unreal-engine-skills) | 335 | 27 个 UE C++ skills，声称对 UE 源码多轮审计 | 第二优先安装。适合减少 UE API 幻觉 |
| [db-lyon/ue-mcp](https://github.com/db-lyon/ue-mcp) | 324 | Unreal 开发工具暴露为 MCP | 作为社区 UE MCP 横向对比，不作为首批安装项 |
| [tumourlove/monolith](https://github.com/tumourlove/monolith) | 303 | UE5.7/5.8 MCP，26 个 namespace、约 1400+ actions，强调 discover/guide/dispatch | 高价值借鉴：namespace dispatch、tool discovery、read-only hints、PIE/profiling、网络暴露风险说明 |
| [EpicGames/unreal-engine-skills-for-claude-code-plugin](https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin) | 275 | Epic 官方 Claude Code 插件，ModelContextProtocol，30+ toolsets | 借鉴 UE MCP 官方方向；当前不是 Codex 直接安装项 |
| [softdaddy-o/soft-ue-cli](https://github.com/softdaddy-o/soft-ue-cli) | 209 | Python CLI + UE 插件，通过 HTTP bridge 控制编辑器 | 借鉴本地桥接、截图、PIE、Blueprint/actor 自动化 |
| [johnpapa/ai-ready](https://github.com/johnpapa/ai-ready) | 201 | 自动生成 AGENTS.md、CI、issue templates，挖掘 PR review 模式 | 借鉴“让项目变 AI-ready”的检查清单 |
| [per-simmons/unreal-agent-harness](https://github.com/per-simmons/unreal-agent-harness) | 189 | UE5.8 + Unreal MCP + PCG + Blender facade kits 城市生成 harness | 借鉴“UE MCP 组织大场景、Blender 制作模块套件”的项目模式 |
| [arjun988/blender-skills](https://github.com/arjun988/blender-skills) | 182 | 94 个 Blender skills，Cursor/Claude/Kiro/Codex + Blender MCP | 借鉴技能链路和 reference image match；先阅读，不复制到本地 |
| [MRCalderon3D/everything-game-dev-code](https://github.com/MRCalderon3D/everything-game-dev-code) | 83 | 多引擎 AI 游戏开发 scaffold，42 agents、51 commands、86 skills | 借鉴游戏专用角色、命令、占位资产到正式资产替换流程 |

## 4. Codex 官方能力如何用于 UE5.8 游戏项目

### 4.1 AGENTS.md：项目长期记忆

Codex 会在工作前读取 AGENTS.md。官方说明中的关键点：

- 全局层：Codex home 下 AGENTS.override.md 优先于 AGENTS.md。
- 项目层：从项目根目录向当前目录查找，每级目录最多取一个指令文件，优先 AGENTS.override.md，再 AGENTS.md，再 fallback 文件。
- 默认合并大小限制是 32 KiB。项目规则不要写成百科；大内容放到 Docs 或 skills，由 AGENTS.md 指向。
- Code Review Rules 应放在最接近代码的 AGENTS.md 中。UE 项目根目录写全局 review 规则，插件或子模块可写局部规则。

本项目 AGENTS.md 应覆盖：

- UE5.8、Windows、项目路径和 UE 安装路径。
- C++/Blueprint 边界。
- 资产命名和目录。
- AIART/AI Voice 默认参数。
- 验证命令、日志路径、Data Validation。
- 不得随意改动 Marketplace、第三方插件、引擎源码和正式资产的规则。
- 重复出错时必须做 retrospective，并建议写入 AGENTS.md 或对应 skill。

### 4.2 Skills：把重复流程变成可加载知识

官方 skill 结构是一个目录，至少包含 SKILL.md，可选 references、scripts、assets、agents。Codex 先看到 skill 名称和 description，只有匹配任务时才读取完整内容。因此 description 要包含真实触发词，例如 “UE5.8 asset import, AIART, texture, LOD, collision, Data Validation”。

对游戏项目，skills 应按可重复流程拆分：

- 项目规范 skill：修改任何 UE 代码/资产前读取。
- 构建测试 skill：统一 UBT、Automation Spec、Data Validation、packaging 命令。
- 资产流水线 skill：统一 AIART/AI Voice、DCC 清理、UE 导入、验收。
- 内容审计 skill：检查命名、redirectors、缺材质、超预算贴图、未记录来源。
- 评审 skill：UE 生命周期、GC、反射、Tick、异步加载、网络复制、性能、资产引用。

### 4.3 Subagents 与 custom agents

Codex 内置 agents：

| Agent | 用途 |
| --- | --- |
| default | 通用任务 |
| worker | 实现和修复 |
| explorer | 只读探索、代码/文档/日志扫描 |

官方 custom agent 文件位置：

- 用户级：~/.codex/agents/
- 项目级：.codex/agents/

每个 TOML 必须包含 name、description、developer_instructions。可选 model、model_reasoning_effort、sandbox_mode、mcp_servers、skills.config 等。

UE 项目并行原则：

- 读密集任务可并行：源码探索、官方文档核对、日志摘要、资产清单、性能 trace 分析。
- 写密集任务必须拆成互不重叠的范围；大改优先使用 Git worktree。
- 主 agent 保留产品目标、设计决策和最终整合；subagent 只返回证据、结论、路径和风险。
- 资产生成、UE live editor 操作、批量改 Blueprint/Content 时，要先有 manifest 和恢复点。

### 4.4 Plugins 与 MCP

OpenAI 插件用于分发 skills 和 MCP。便携插件根目录可包含 plugin.json、skills/、mcp.json、assets/。MCP 适合把 Codex 接到外部系统，如 UE Editor、GitHub、Jira、文档站、资产数据库。

UE live editor MCP 的风险也很明确：它能直接修改 UObject、Blueprint、材质、资产数据库和编辑器状态。正式项目中应当：

- 长会话前保存、提交或 shelve。
- 禁止在没有恢复点的情况下批量修改 Content。
- 对 Blueprint/Widget/Material/Niagara 操作读取返回状态，不把工具返回当成默认成功。
- PIE、shader compile、C++ compile 期间避免执行易挂起工具。
- 先用只读工具验证编辑器可达，再执行修改。

### 4.5 UE5.8 内置 AI/MCP 能力地图

本机 G:\UnrealEngineInstalled\UE_5.8 已经包含 Epic 放入引擎的实验性 AI/MCP 相关能力。它们说明 UE5.8 的方向已经不是单纯“外部 AI 写代码”，而是让 AI 通过 ToolsetRegistry、MCP server、editor toolset 直接理解和操作编辑器对象。

| 能力 | 本机位置 | 关键事实 | 本项目采用建议 |
| --- | --- | --- | --- |
| Unreal MCP / ModelContextProtocol | Engine/Plugins/Experimental/ModelContextProtocol | FriendlyName 为 Unreal MCP；描述为 Anthropic MCP server implementation for Unreal Engine；Experimental、NoRedist、EnabledByDefault=false | NewWorld 已按 Editor target 启用；只监听 127.0.0.1:8000/mcp，手动启动 |
| ModelContextProtocol settings | ModelContextProtocolSettings.h | 默认 ServerPortNumber=8000，ServerUrlPath=/mcp，bAutoStartServer=false，bEnableToolSearch=true | 项目默认固定为 8000、/mcp、bAutoStartServer=False、bEnableToolSearch=True |
| Client config generation | ModelContextProtocolClientConfig.h/.cpp | 支持 ClaudeCode、Cursor、VSCode、Gemini、Codex；Codex 目标为项目根 .codex/config.toml，TOML write-once，已有文件时不会安全合并 | 本项目手写维护 .codex/config.toml；不让 UE 工具覆盖 |
| Console command | ModelContextProtocolEngineModule.cpp | ModelContextProtocol.GenerateClientConfig <ClaudeCode|Cursor|VSCode|Gemini|Codex|All> | 仅作为参考；项目配置已存在时不要用它覆盖 Codex TOML |
| ToolsetRegistry bridge | ModelContextProtocolEditor | bEnableToolSearch=true 时只注册 list_toolsets、describe_toolset、call_tool；真实工具按需发现和调用 | 推荐保留这种 discovery/dispatch 模式，减少上下文噪声 |
| AIAssistant | Engine/Plugins/Experimental/AIAssistant | EditorOnly、Experimental、NoRedist、EnabledByDefault=false；依赖 PythonScriptPlugin、EditorScriptingUtilities、ToolsetRegistry、WebBrowser；默认 URL 为 https://dev.epicgames.com/community/assistant/embedded | 当作编辑器内 Ask AI/文档助手入口研究，不作为资产批处理主工具 |
| UMGToolSet | Engine/Plugins/Experimental/Toolsets/UMGToolSet | 可 AICallable 创建 Widget Blueprint、添加/移动/删除/重命名 widget、查询 widget tree、绑定事件、替换模板、compile WBP | 已作为精选 Toolset 启用；UI 写入必须在 AIWork/Dev 或明确目标内 |
| NiagaraToolsets | Engine/Plugins/Experimental/Toolsets/NiagaraToolsets | 可 AICallable 查询、编辑 Niagara system/schema/topology/data/status | 已作为精选 Toolset 启用；必须截图/播放验证 bounds、overdraw、spawn rate 和 SFX 同步 |
| PCGToolset | Engine/Plugins/Experimental/Toolsets/PCGToolset | 可 AICallable 创建 PCG graph、参数、实例、节点、连接、注释、执行 instant graph | 已作为精选 Toolset 启用；必须记录 seed、参数和玩家路径验证 |
| MCPClientToolset | Engine/Plugins/Experimental/Toolsets/MCPClientToolset | 允许 ToolsetRegistry 客户连接本地或私有 MCP server | 已作为精选 Toolset 启用；连接本地/私有 MCP 前必须审计 |

UE5.8 内置 MCP 的操作边界：

1. 第一阶段只读：list_toolsets、describe_toolset、查询场景/资产/Widget/PCG/Niagara，不保存资产。
2. 第二阶段灰盒沙盒：只在 Dev 或 AIWork 路径创建临时 Actor、Widget、PCG graph、Niagara prototype。
3. 第三阶段受控写入：有 Git 恢复点、asset manifest、目标路径、命名、验收清单后才允许改 Content。
4. 第四阶段入库：Data Validation、PIE 或截图、日志、来源记录通过后，从 AIWork/Staging 移入正式目录。
5. 任何 MCP 写操作失败或返回不完整时，优先停下检查日志和当前编辑器状态，不连续重试。

NewWorld 当前接入 Codex + Unreal MCP 时，应让 Codex 在 AGENTS.md 中看到这些固定规则：

~~~text
UE MCP is experimental. Treat it as editor automation, not a trusted build system.
Start with read-only tool discovery.
Do not enable auto-start by default.
Do not overwrite .codex/config.toml; generate or edit MCP config manually.
Write only under Content/NewWorld/AIWork or Dev unless a task explicitly names a reviewed target.
After every write batch, capture evidence: changed assets, screenshot or PIE result, log excerpt, Data Validation status.
~~~

当前工程化状态：

- 项目级 Codex MCP 配置：.codex/config.toml。
- UE MCP server：unreal-mcp -> http://127.0.0.1:8000/mcp。
- Blender MCP server：blender -> uvx + Python 3.12 + blender-mcp，BLENDER_MCP_SAFE_MODE=1。
- UE MCP 启动脚本：Tools/MCP/start_ue_mcp_editor.py。
- MCP 检查脚本：Tools/MCP/check_mcp_readiness.py。
- Blender MCP 环境检查脚本：Tools/MCP/start_blender_mcp_session.py。
- Blender 静态网格 FBX 导出脚本：Tools/Assets/export_blender_static_mesh_fbx.py。
- UE MCP StaticMesh staging 导入脚本：Tools/MCP/import_static_mesh_via_ue_mcp.py。
- 资产生产路线文档：Docs/Assets/ASSET_PRODUCTION_ROUTES.md。
- 禁止项：AllToolsets、AIAssistant、bAutoStartServer=True、0.0.0.0 绑定、用户级 Codex 配置自动修改。

2026-09-11 NewWorld 实测结论：当前 UE5.8 StaticMeshTools.import_file 通过 FbxFactory 导入，直接传 .glb/.gltf 会被拒绝；该路径已验证可用输入为 FBX/OBJ。AI 3D 和 Blender 可继续使用 GLB 做中间交换，但进入 UE MCP StaticMesh 导入前必须导出或转换为 FBX/OBJ。StaticMesh 回读时，MCP UObject 参数必须使用完整 object path 的 refPath，例如 /Game/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.SM_MCP_DryRun_Blockout_A。

## 5. 当前机器能力与推荐安装清单

### 5.1 当前已可用能力

| 能力 | 当前用途 |
| --- | --- |
| imagegen | 概念图、参考图、贴图草案、UI 草图、图标草案 |
| openai-docs | Codex、skills、agents、plugins、OpenAI API 官方资料核对 |
| skill-creator | 为本项目创建可复用 Codex skills |
| skill-installer | 从 curated 或 GitHub repo/path 安装 Codex skills |
| plugin-creator | 后续把项目 skills/MCP 打包为个人或团队插件 |
| ue-trace-analysis | 读取 UE trace，做 CPU hotspot 和性能证据分析 |
| ue-plugin-abi-crash-diagnostics | UE 插件 ABI、BuildId、UObject/GC、DLL 崩溃诊断 |
| AIART OpenAPI/MCP | 图片、视频、3D、贴图、模型拆分/简化、去背景等资产生成 |
| AI Voice | TTS、SFX、音乐、视频配音、分轨、降噪、ASR、声线转换 |

AIART 默认规则：

- 图片生成未指定模式时，必须显式传 inferenceMode: "gpt"。
- 质量优先于速度和成本，除非用户明确限制。
- Hyper3D 可用且适合时使用 modelVariant: "extremeHigh"。
- Tripo 贴图可用且适合时使用 textureQuality: "detailed"。

### 5.2 推荐安装：第一批，后续参考命令，本次不执行

以下命令只写入文档，供后续项目准备阶段执行。本次调研不运行、不安装、不克隆任何仓库。

先预览：

~~~powershell
npx skills add gamedev-skills/awesome-gamedev-agent-skills --list
npx skills add quodsoler/unreal-engine-skills --list
~~~

确认 skill 列表和触发词后，再安装：

~~~powershell
npx skills add gamedev-skills/awesome-gamedev-agent-skills
npx skills add quodsoler/unreal-engine-skills
~~~

采用理由：

- gamedev-skills 提供 router、Unreal 5.8 技能、跨引擎游戏工种技能、genre 技能和 workflow 技能。它覆盖 create-game-assets、audio-design、game-ui-ux、level-design、game-feel、procedural-gen、performance-optimization、prototype-fast、steam-publish、itch-publish。
- quodsoler 提供 UE C++ 专项知识，覆盖 ue-cpp-foundations、ue-gameplay-framework、ue-gameplay-abilities、ue-animation-system、ue-materials-rendering、ue-audio-system、ue-ui-umg-slate、ue-testing-debugging、ue-project-context 等，适合降低 UE API 幻觉。

### 5.3 推荐安装：第二批候选

| 候选 | 处理方式 |
| --- | --- |
| wshobson/agents | 只选 plugin-eval、agent authoring、review、docs/testing 类思路；不全量安装 |
| alirezarezvani/claude-skills | 只评估 skill-security-auditor、agent-designer、self-improving-agent、prompt/version 工具类 |
| Resource2Skill | 用于把 Blender、UE、REAPER、Substance、内部美术规范蒸馏成本项目 skill |
| Epic Unreal Claude plugin | 暂不作为 Codex 安装项；借鉴其 ModelContextProtocol/Toolsets 方向 |
| UnrealClaude / VibeUE / soft-ue-cli | 作为社区经验参考；NewWorld 当前使用 UE5.8 内置 ModelContextProtocol |
| ahujasid/blender-mcp | NewWorld 已用项目级 Codex 配置接入本机 blender-mcp；继续借鉴 safe mode、截图、导入导出和 Python 执行边界 |
| arjun988/blender-skills | 只借鉴 Blender 技能链、reference image match、export-pipeline，不复制到本地 |
| tumourlove/monolith | 只借鉴 namespace dispatch、tool discovery、read-only hints 和安全说明；接入前需单独审计网络暴露和写操作 |

Blender MCP 当前项目级配置：

~~~powershell
# 不要为本项目运行 codex mcp add；该命令默认修改用户级 Codex 配置。
# 项目配置源是 G:\NewWorld\.codex\config.toml。
python Tools/MCP/start_blender_mcp_session.py
~~~

项目配置等价形式：

~~~toml
[mcp_servers.unreal-mcp]
url = "http://127.0.0.1:8000/mcp"

[mcp_servers.blender]
command = "C:\\Users\\happyelements\\.local\\bin\\uvx.exe"
args = ["--python", "C:\\Users\\happyelements\\AppData\\Local\\Programs\\Python\\Python312\\python.exe", "blender-mcp"]
env = { BLENDER_MCP_SAFE_MODE = "1", DISABLE_TELEMETRY = "1" }
~~~

Blender MCP 使用提醒：

- GUI 启动的 Codex/Blender 可能找不到 uvx，必要时使用 uvx.exe 绝对路径。
- 同一时间只运行一个 Blender MCP server，避免多个客户端同时控制同一个 Blender。
- BLENDER_MCP_SAFE_MODE=1 只能降低风险，不能替代保存、版本控制和人工审查。
- Blender MCP 允许执行 Python；任何文件系统、网络、外部进程、批量保存行为都要显式写入任务范围并检查结果。

## 6. UE5.8 项目规范

### 6.1 版本控制和大文件

新项目第一步：

~~~powershell
git init
git status
~~~

建议开启 Git LFS 管理 uasset、umap、fbx、glb、wav、png、exr、tga、psd、blend 等大文件。正式规则应在项目创建后写入 .gitattributes。每个可运行里程碑必须提交一次；AI 大批量操作 Content 前必须先提交或建立可恢复分支。

Source Control 使用原则：

- 从 UE Editor 外部同步或大规模切换分支前，优先关闭 Editor。
- Content Browser 中的资产改动要保存后再验证。
- AI 生成资产先进入 AIWork 或 Staging，不直接覆盖正式资产。

### 6.2 推荐目录

~~~text
Content/NewWorld/
  Core/                 全局材质、函数、输入、GameInstance、全局 DataAssets
  Gameplay/             玩法 Blueprint、Ability、组件、交互物
  Characters/           角色、骨骼、动画、AnimBP、PhysicsAsset
  Environment/          场景、地形、建筑、植被、关卡模块
  Props/                道具、可交互物、装饰物
  UI/                   WBP、CommonUI、字体、图标、样式
  Audio/                SFX、VO、BGM、SoundCue、MetaSound、Submix
  VFX/                  Niagara、flipbook、VFX 材质
  Materials/            Master Materials、Material Functions、共享 MI
  Data/                 DataTable、PrimaryDataAsset、Gameplay Tags
  Maps/                 L_、LVL_、测试地图、功能地图
  Dev/                  测试、灰盒、临时关卡
  AIWork/               AI 生成候选和 WIP，未审查不得进入正式目录
Docs/
  Art/
  Assets/
  Design/
  Engineering/
  Planning/
  QA/
  Performance/
.agents/
  skills/
  ue-project-context.md
.codex/
  agents/
~~~

### 6.3 资产命名

采用 Epic 推荐形态：[AssetTypePrefix]_[AssetName]_[Descriptor]_[OptionalVariant]

| 类型 | 前缀示例 |
| --- | --- |
| Blueprint | BP_ |
| Widget Blueprint | WBP_ |
| Static Mesh | SM_ |
| Skeletal Mesh | SK_ |
| Physics Asset | PHYS_ |
| Skeleton | SKEL_ |
| Animation Sequence | AS_ |
| Animation Blueprint | ABP_ |
| IK Rig / IK Retargeter | IKR_ / RTG_ |
| Control Rig | CR_ |
| Material / Material Instance | M_ / MI_ |
| Material Function | MF_ |
| Texture | T_ |
| Niagara System / Emitter | NS_ / NE_ |
| Sound Wave / Sound Cue | SW_ / SC_ |
| MetaSound | MS_ |
| Data Asset / Data Table | DA_ / DT_ |
| Gameplay Ability / Effect / Cue | GA_ / GE_ / GC_ |
| Input Action / Mapping Context | IA_ / IMC_ |
| Level / Level Sequence | L_ / LS_ |
| Font | Font_ |

Texture descriptor 建议：

- BC：Base Color，sRGB on。
- N：Normal，normal map compression，sRGB off。
- ORM：R=AO，G=Roughness，B=Metallic，sRGB off。
- E：Emissive，sRGB 按材质策略确认。
- M：Mask，sRGB off。

### 6.4 C++ 与 Blueprint 边界

默认规则：

- 稳定运行时逻辑、状态复制、数据结构、复杂算法、异步加载、性能敏感逻辑放 C++。
- 设计师调参、关卡摆放、简单组合、动画蓝图、Widget 视觉和 Niagara 参数绑定放 Blueprint。
- 数据驱动配置优先用 PrimaryDataAsset、DataTable、Gameplay Tags 和可软引用资产。
- 不用 Tick 实现可事件驱动的逻辑。需要 Tick 必须说明频率、关闭条件和性能理由。
- UObject 指针必须考虑 GC：成员引用用 UPROPERTY 或 TObjectPtr；异步回调用 TWeakObjectPtr。
- Editor-only 逻辑进入 Editor module 或 Editor Utility，不混进 Shipping runtime。

### 6.5 自动化验证

基础命令模板：

~~~powershell
G:\UnrealEngineInstalled\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe <PROJECT>.uproject -run=DataValidation
~~~

后续项目建立后应补充：

- UBT 编译命令。
- Automation Spec 过滤器。
- Functional Test 地图运行命令。
- Packaging smoke test。
- 日志路径：Saved/Logs、Saved/Crashes、AutomationReports。

当前 NewWorld 已将资产规则落成 UE Data Validation：NewWorldEditor 模块中的 UNewWorldAssetPolicyValidator 只验证 /Game/NewWorld，检查正式资产前缀、[Prefix]_[Name]_[Descriptor]_[Variant] 形态、AIWork staging、AI_ASSET_MANIFEST.json 状态、creation_route 记录、MCP staging 标记，以及 StaticMesh/Texture/Material 的第一层质量问题。项目已移除无用模板资产；模板内容不属于验证或运行时兼容范围，所有新增内容必须放在 Content/NewWorld 下。

Data Validation 应至少检查：

- 命名前缀。
- Content/NewWorld 外资产引用。
- AIWork 资产不得被正式关卡引用。
- 贴图尺寸、sRGB、compression、TextureGroup。
- Static Mesh pivot、collision、Nanite/LOD 设置。
- Skeletal Mesh skeleton、PhysicsAsset、LOD、材质槽。
- SoundWave 命名、响度、循环点、并发策略。
- WBP 字体、分辨率适配、CommonUI 输入路由。
- 每个 AI 或工具生成资产有 creation_route 和 provenance 记录。

## 7. 推荐项目级 agents

| Agent | 职责 | 默认写入范围 | 推荐模型/推理 |
| --- | --- | --- | --- |
| ue-architect | 模块、插件、Gameplay Framework、GAS、C++/Blueprint 边界 | Docs/Engineering，默认只读 | gpt-6-astra high 或 xhigh |
| gameplay-worker | 单个玩法功能、组件、输入、Ability、UI glue | Source、指定 Blueprint 辅助脚本、测试 | gpt-5.6-sol high |
| technical-artist | 材质、LOD、Nanite、碰撞、导入设置、DCC 检查 | Content/NewWorld/AIWork、Docs/Art | gpt-6-astra high |
| asset-pipeline | AIART/AI Voice 生成计划、manifest、命名、QA | Docs/Assets、AIWork | gpt-5.6-sol high |
| blender-mcp-artist | Blender MCP blockout、硬表面、模块化套件、清理、截图对比、导出 | Blender staging、Docs/Art，默认不碰正式 Content | gpt-5.6-sol high |
| mcp-safety-reviewer | UE/Blender MCP 操作计划审查、写入范围、恢复点、工具返回和日志核对 | 只读 | gpt-6-astra high |
| anim-rigging | 骨骼、retarget、AnimBP、Control Rig、Motion Matching | Characters、Docs/Art | gpt-6-astra high |
| audio-designer | SFX、VO、BGM、SoundCue、MetaSound、Submix | Audio、Docs/Audio | gpt-5.6-sol medium/high |
| ui-ux | UMG、CommonUI、字体、图标、HUD、菜单、可访问性 | UI、Docs/UI | gpt-5.6-sol high |
| qa-automation | Automation Spec、Functional Test、Data Validation、smoke test | Tests、Docs/QA | gpt-5.6-terra medium/high |
| performance-agent | Unreal Insights、stat 命令、预算、热点分析 | Docs/Performance，默认只读 | gpt-6-astra high |
| crash-diagnostics | Saved/Crashes、logs、ABI、GC、BuildId、UObject 崩溃 | 默认只读 | gpt-6-astra high/xhigh |
| producer | 里程碑、风险、任务切分、决策记录 | Docs/Planning | gpt-5.6-terra medium |
| ue-reviewer | PR/本地 diff 审查，缺陷优先 | 只读 | gpt-6-astra high |

并行使用方式：

- “调研 UE5.8 动画系统、资产导入、UI、音频”这类任务可一 agent 一主题。
- “实现战斗系统”应先让 explorer/architect 做只读图谱，再由 worker 在明确范围内修改。
- “替换一批资产”应由 asset-pipeline 准备 manifest，technical-artist 做导入 QA，reviewer 做最终审查。
- 每个 subagent 输出必须包含：输入、查到的证据、结论、风险、建议改动、验证方式。

## 8. 推荐项目 skills

| Skill | 触发词 | 作用 |
| --- | --- | --- |
| ue58-project-standards | UE5.8、项目规范、目录、命名、C++/Blueprint | 统一项目默认规则 |
| ue58-build-test-runner | 编译、测试、DataValidation、Automation、packaging | 输出正确命令和日志分析 |
| ue58-asset-pipeline | AIART、3D、贴图、导入、LOD、collision、provenance | 管理 AI 资产全流程 |
| ue58-content-audit | Content 审计、命名违规、redirector、材质丢失、贴图超预算 | 合并前资产检查 |
| ue58-review-checklist | review、PR、diff、UObject、GC、Tick、replication | UE 缺陷优先审查 |
| ue58-ai-production-retro | retrospective、重复错误、更新规则 | 把真实教训回写到 AGENTS 或 skill |
| ue58-mcp-editor-automation | UE MCP、ToolsetRegistry、AIAssistant、只读/写入边界 | 规范 AI 控制 UE Editor 的安全流程 |
| ue58-blender-mcp-asset | Blender MCP、reference image、image plane、blockout、cleanup、export | 规范 Codex + Blender MCP 资产制作 |
| ue58-ui-commonui | UMG、CommonUI、字体、HUD、菜单、输入焦点 | UI 专项规范 |
| ue58-audio-pipeline | SFX、VO、BGM、MetaSound、SoundCue、Submix | 音频专项规范 |
| ue58-animation-rigging | rig、retarget、Control Rig、Motion Matching、Anim Notify | 动画和绑定专项规范 |

创建原则：

- 第一版尽量短，每个 skill 只解决一个高频流程。
- 复杂参考资料放 references/，脚本放 scripts/，模板放 assets/。
- description 写真实触发词，让 Codex 自动匹配。
- 每次 AI 重复犯错两次，就让 Codex 总结规则并更新对应 skill。

## 9. AI 资产生产总流程

AI 生成物默认只是生产候选，不是可直接发布资产。

标准流程：

~~~text
需求卡片
-> Art direction brief
-> Asset manifest
-> 参考图/风格板/seed approval
-> 小批量候选生成
-> 人工或 agent 选择
-> DCC 清理与标准化
-> UE 导入与材质/碰撞/LOD/Nanite/音频/UI 设置
-> 场景内和原生尺寸验证
-> Data Validation
-> provenance 和 license 记录
-> 从 AIWork/Staging 移入正式目录
~~~

质量门：

- 风格一致：同家族资产的比例、光向、色彩、材质、细节密度一致。
- 游戏可读：在真实镜头距离、真实背景、运动状态下能读清功能和状态。
- 技术可用：尺寸、pivot、UV、法线、LOD、碰撞、材质槽、纹理通道、采样率、字体缓存、UI safe area 正确。
- 可维护：命名、目录、DataAsset、manifest、source/provenance 完整。
- 可授权：每个入库资产都记录工具、模型、日期、prompt、引用、许可证或生成声明。

### 9.1 AI 资产里的 MCP 分工

MCP 的价值不是“让 AI 一次做完美术”，而是把外部工具接入可观察、可重复、可验收的循环。

| 阶段 | Codex 主要职责 | Blender MCP 主要职责 | UE MCP 主要职责 | 人工判断 |
| --- | --- | --- | --- | --- |
| Brief | 把玩法用途、风格、预算、命名和验收写成任务合同 | 无 | 无 | 判断资产是否值得进入制作 |
| Reference | 生成/整理正交图、3/4 图、材质板、比例尺、Do/Don't | 建 image planes、相机、比例尺、blockout 场景 | 无 | 选定轮廓、比例和风格 |
| 3D candidate | 调用或规划 AI 3D 生成，多候选比较 | 导入 GLB/OBJ/FBX、检查 mesh、截图、修比例 | 无 | 决定重生成还是继续清理 |
| Cleanup | 记录问题和清理 checklist | 改 scale、origin、pivot、法线、材质槽、简化、碰撞代理、LOD 草案 | 无 | 检查近景质量和艺术一致性 |
| UE import | 生成导入任务、命名、路径、manifest | 用 Tools/Assets/export_blender_static_mesh_fbx.py 导出 FBX/OBJ；GLB 只做中间交换 | 用 Tools/MCP/import_static_mesh_via_ue_mcp.py 导入、写 metadata、保存、回读 bounds/material/LOD/Nanite、截图 | 验收真实 game camera |
| Validation | 汇总日志、截图、Data Validation、provenance | 产出前后对比截图和 .blend 来源 | 运行 PIE/Data Validation/asset query | 批准从 AIWork 移入正式目录 |

MCP 写操作必须小批量执行。推荐每次只处理一个资产或一个明确模块套件，直到流程稳定后再批量化。

## 10. 美术方向、概念图和风格板

每个游戏阶段至少有一个 Art Direction Brief。字段：

~~~text
玩家幻想：
核心动词：
目标平台：
摄像机和视角：
屏幕上典型资产尺寸：

形状语言：
轮廓优先级：
明度结构：
语义色板：
材质语言：
边缘/线条处理：
光照方向：
细节密度：
运动性格：
明确排除：

资产尺寸/比例：
透明/背景：
网格/帧/瓦片：
anchor/pivot/baseline：
过滤/mipmap/compression：
色彩空间：
面数/贴图/材质预算：
命名和目录：

已批准 seed/reference：
Do/Don't 示例：
真实游戏截图：
批准人和日期：
~~~

概念图原则：

- 用一张高质量概念图定义世界，不把它直接当生产贴图。
- 复杂角色先拆成部件：身体、手、靴子、外套、武器、帽子、面具、头发、饰品等。
- 环境概念拆成模块：地面、墙、门、桥、岩石、植被、灯、标志物、可交互物、远景背景。
- 每个部件生成白底或中性背景参考，便于 3D 工具读取。
- AIART 图片生成默认显式 inferenceMode: "gpt"。
- 不用在世艺术家名字定义风格；要写形状、色彩、材质、光照、构图、边缘处理。

### 10.1 给 Blender MCP 和 3D 生成模型的参考图规范

Blender MCP 和 3D 生成模型都依赖清晰参考。普通氛围图只能帮助风格，不能直接帮助建模。进入 3D 前至少准备以下参考：

| 参考类型 | 要求 | 用途 |
| --- | --- | --- |
| Front / Side / Back / Top 正交图 | 中性光、白底或浅灰底、无透视、无遮挡、同一比例 | 用作 Blender image plane，约束轮廓和厚度 |
| 3/4 视角效果图 | 保留真实材质、明暗、细节密度和最终镜头感觉 | 判断风格和玩家可读性 |
| Silhouette 图 | 黑白轮廓，去掉材质细节 | 让 AI 优先抓住形状语言 |
| 部件拆解图 | 标注可动件、可替换件、材质分区、不可烘进主体的元素 | 决定模型拆分、材质槽和绑定需求 |
| 比例尺图 | 加 1m 网格、人形尺、门高、手持比例或 UE mannequin 参照 | 防止 AI 生成尺寸漂移 |
| 材质色板 | Base Color、Roughness、Metallic、Emissive、污损/磨损规则 | 后续贴图和材质实例统一 |
| Do / Don't | 3 到 5 个必须保留和必须排除的例子 | 减少风格漂移和重复返工 |

参考图生成提示：

~~~text
生成用于 3D 建模的正交参考图，而不是宣传插画。
输出 front、side、back、top 四视图，白底，中性光，无透视变形，比例一致。
加 1m 比例尺和关键部件标注。
单独给一张 3/4 beauty view 展示材质、磨损和最终风格。
不要遮挡轮廓，不要强景深，不要戏剧化阴影，不要把文字/标志烘进无法编辑的位置。
~~~

Blender MCP 使用这些参考图时，先创建单位、相机和 image planes，再开始建模：

1. 设 scene unit 为 metric，按 UE 厘米导出策略记录 scale。
2. 在 X/Y/Z 对应视图放置 front、side、back、top image planes，锁定位置和旋转。
3. 用简单 primitives 建 blockout，只匹配大轮廓和比例。
4. 截取 front、side、3/4、wireframe 四张图对比参考。
5. 通过 MCP 迭代细化局部，但每轮只改一个部位。
6. 通过命名、材质槽、origin、pivot、collision proxy、LOD 或 Nanite 策略验收后再导出。

### 10.2 AI 图片生成 prompt 详细度规范

AI 图片生成的 prompt 应尽量详细，但详细信息必须在任务合同或已批准 prompt 中写清楚，不能由 agent 在最终调用 AIART 时临场私自扩写。AIART MCP 的图片/视频/3D 相关工具要求逐字使用用户原始提示词；除非用户明确要求修改提示词，否则不要翻译、改写、扩写、润色，也不要添加风格、构图、镜头、材质或质量词。

推荐流程：

1. 先让 Codex 起草详细 prompt，目标是给人审阅，而不是立刻提交生成。
2. 用户或项目负责人确认 prompt 后，把它作为 approved prompt 写入任务或 asset manifest。
3. 调用 AIART 时逐字传入 approved prompt，并显式使用项目默认参数，例如 inferenceMode: gpt。
4. 生成后记录 prompt、模型、参数、参考图、task id、候选编号和取舍理由。

详细 prompt 应包含：

| 字段 | 应写内容 |
| --- | --- |
| 用途 | 概念图、3D reference、贴图草案、UI icon、HUD mockup、广告图、透明 cutout |
| 画面主体 | 资产名称、部件、动作、状态、可读轮廓 |
| 游戏上下文 | 摄像机距离、玩家视角、屏幕占比、互动功能 |
| 风格语言 | 形状语言、边缘处理、细节密度、材质语言、色彩规则 |
| 构图和视角 | 正交/front/side/back/top、3/4、俯视、等距、UI 居中等 |
| 光照 | 中性光、无强阴影、gameplay 可读、是否允许氛围光 |
| 材质和纹理 | PBR 方向、Base Color 是否干净、磨损、污渍、roughness/metallic/emissive |
| 技术限制 | 透明背景、无文字、无水印、比例尺、参考网格、输出比例 |
| 禁止项 | 不要透视变形、不要烘焙阴影、不要多余角色、不要不可本地化文字 |

不同图片用途的重点不同：

- 3D 建模参考图：优先正交、多视图、比例尺、中性光、白底、无透视。
- 场景概念图：优先玩家路径、构图、模块拆解、地标、光照气氛和可交互物。
- 贴图草案：优先 tileable、无 baked light、PBR 通道意图和材质尺度。
- UI/icon：优先透明背景、清晰 silhouette、统一线宽、无文字或只保留已批准原文。

## 11. 3D 模型、拓扑、UV 与 UE 导入

### 11.1 Codex + Blender MCP 工作手册

Blender MCP 适合当作“可脚本化 DCC 工作台”。Codex 应先查询场景和对象，再规划修改，最后截图和导出。不要让它在一个长 prompt 里同时完成生成、清理、UV、贴图、绑定、导出和 UE 导入。

当前项目接入流程：

1. 运行 Tools/MCP/start_blender_mcp_session.py，确认 uvx、Python、Blender 路径和 BLENDER_MCP_SAFE_MODE=1。
2. 打开 Blender，启用 MCP for Blender addon，只连接一个 MCP client。
3. Codex 先调用场景查询能力，确认当前文件、单位、对象数量、collection、相机、材质和选中对象。
4. 每个资产建立 collection：REF、BLOCKOUT、HIGH、LOW、COLLISION、EXPORT。
5. 先用 image planes 和 primitives 做 blockout，截图确认轮廓。
6. 再做细节、材质槽、UV、碰撞、LOD 或 Nanite 策略。
7. 每轮修改后导出截图：front、side、3/4、wireframe、material preview。
8. 导出前运行 Blender 侧检查：非流形面、重复点、法线方向、未命名对象、未应用 scale、空材质槽、过高面数。
9. 导出到 staging，不直接覆盖正式 UE Content。
10. 静态网格进入 UE MCP 导入前，使用 Tools/Assets/export_blender_static_mesh_fbx.py 从 .blend 导出 FBX。明确传入渲染 mesh 和 UCX 碰撞对象名；脚本默认输出只能位于 Content/NewWorld/AIWork，并按 UE 厘米单位导出。
11. 如果上游 AI 3D 只产出 GLB/GLTF，先在 Blender 中检查比例、pivot、法线、材质槽和碰撞，再导出 FBX/OBJ。当前 UE MCP StaticMeshTools.import_file 路径不接受直接 GLB/GLTF。

Blender MCP 任务提示应包含：

~~~text
资产名：
用途和镜头距离：
目标尺寸：
正交参考图：
3/4 参考图：
材质槽：
poly/tri 预算：
pivot/origin：
碰撞策略：
LOD/Nanite 策略：
导出格式和路径：
UE MCP 导入格式：FBX/OBJ；GLB/GLTF 仅作为 Blender/AI 3D 中间交换
必须截图角度：
不得修改：
完成验收：
~~~

### 11.2 AI 3D 生成 vs Blender MCP 直接建模决策树

| 资产类型 | creation_route / 推荐路径 | 原因 |
| --- | --- | --- |
| 岩石、废墟、树桩、自然碎片、远景雕塑 | ai_3d_then_blender：AI 3D 生成多候选 -> Blender 清理 -> UE 导入 | 不规则轮廓对生成模型友好，人工建模性价比低 |
| 箱子、瓶罐、路障、门框、栏杆、管线、模块墙体 | blender_mcp_direct 或 procedural_tool_generated：Blender MCP 直接建模或程序化生成 | 尺寸、直线、pivot、snap、碰撞比随机细节更重要 |
| 武器、载具部件、机关、可开合道具 | hybrid：Blender MCP blockout -> 局部 AI reference/texture -> 手工或脚本细化 | 需要精确拓扑、分件、铰链、碰撞和动画轴 |
| 主角、主要敌人、脸、手、布料、头发 | manual_dcc_required：AI 概念和 3D 候选 -> 专门 retopo/rig/weight -> UE retarget | 生成模型可给体量和风格，但变形质量必须专项处理 |
| 大场景 set dressing | ue_mcp_assembly 或 procedural_tool_generated：Blender MCP/UE MCP 组装资产库和 PCG -> 截图验收 | 关键是布局、尺度、密度、遮挡、性能和可复现 seed |
| UI 3D 装饰、icon source mesh、简单 VFX mesh | blender_mcp_direct：Blender MCP 直接建模 -> 渲染/导出 | 需要干净轮廓、透明背景和可重复变体 |

重生成阈值：

- 大轮廓错、比例错、部件缺失、角色肢体错误：重新生成，不要修。
- 拓扑极乱、非流形大面积存在、UV 无法展开、材质槽混乱：重新生成或换工具。
- 局部细节脏、法线反、scale/pivot 错、少量破洞、材质名乱：Blender MCP 清理。
- 近景 hero asset 的 silhouette、材质或动画需求不达标：回到 concept/reference，不在低质量模型上堆修复。
- 三轮局部修复仍失败：写入 retrospective，换路径或人工处理。

AI 3D 生成能力使用规范：

1. 每个资产至少生成 3 个候选；hero asset 至少 5 个候选或分部件生成。
2. 输入优先使用正交 reference + 3/4 beauty view；只用文字 prompt 时必须增加尺寸、形状语言、Do/Don't、材质和用途。
3. Hyper3D 可用且适合时默认 modelVariant: extremeHigh。
4. Tripo 贴图可用且适合时默认 textureQuality: detailed。
5. Hunyuan3D、Rodin 或其他模型只在当前接口实际开放且输入匹配时选择；不要虚构全局最强排名。
6. GLB 适合作为 Blender 中间格式；NewWorld 当前已验证 UE MCP StaticMesh 导入路径使用 FbxFactory，正式 UE MCP 导入前必须转换为 FBX/OBJ。
7. 生成资产只进入 AIWork/Staging，并必须记录 creation_route、route_decision_reason、authoring_tools、prompt、模型、参数、时间、引用和许可证/provenance。

### 11.3 静态物件和环境模型

适合 AI 生成：

- 灰盒后的环境模块。
- 中远景道具。
- 风格探索和 silhouette 验证。
- 岩石、废墟、箱子、硬表面小道具、装饰物、远景建筑块。

谨慎用于：

- 主角和主要敌人。
- 近景镜头道具。
- 需要精确碰撞、开合、可拆、可破坏的机制资产。
- 需要精细绑定和换装的角色部件。

推荐技术流程：

1. 先生成或选择概念 reference。
2. AI 3D 生成多个候选，不接受第一版，选择线框和轮廓最干净的一版。
3. Blender/DCC 中修比例、单位、pivot、法线、破洞、重复点、非流形面。
4. 对高面数资产做 retopo 或 simplify。
5. UV0 用于渲染，必要时 UV1 用于 lightmap 或特殊烘焙策略。
6. Bake normal/AO，把高模细节转到低模贴图。
7. 按 UE 厘米单位导出，优先 FBX 2020.2；GLB 可作为 Blender 交换格式，但当前 UE MCP StaticMeshTools.import_file 已验证不接受直接 GLB/GLTF。
8. UE Static Mesh Editor 中检查 scale、pivot、materials、collision、Nanite、LOD、bounds。

NewWorld 已验证静态网格 staging 命令：

~~~powershell
python Tools/Assets/export_blender_static_mesh_fbx.py --blend-path Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.blend --output-fbx Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.fbx --object-names SM_MCP_DryRun_Blockout_A_Base,SM_MCP_DryRun_Blockout_A_Step,SM_MCP_DryRun_Blockout_A_Pillar,UCX_SM_MCP_DryRun_Blockout_A_00
~~~

~~~powershell
python Tools/MCP/import_static_mesh_via_ue_mcp.py --source-file Content/NewWorld/AIWork/MCP_DryRun/SM_MCP_DryRun_Blockout_A.fbx --folder-path /Game/NewWorld/AIWork/MCP_DryRun --asset-name SM_MCP_DryRun_Blockout_A --allow-overwrite --evidence-directory Docs/Planning/MCP_Evidence/2026-09-11_UE_MCP_Import_Script_DryRun
~~~

UE 官方约束：

- UE FBX import pipeline 使用 FBX 2020.2，不同版本可能不兼容。
- Static Mesh 导入后必须在 Static Mesh Editor 验证。
- 复杂碰撞可以用 per triangle，但大量复杂碰撞会影响性能；交互物优先手工 simple collision 或 UCX collision。

### 11.4 角色模型

Top3D 角色管线可借鉴的关键步骤：

1. 概念先行，因为下游会放大概念里的问题。
2. 复杂角色拆件生成，决定哪些部分以后能动，哪些烘进主体轮廓。
3. AI mesh 用多次生成选择最干净 wireframe。
4. Blender 中用少量工具修形：Grab、Elastic Grab、Mask、Smooth、Inflate + Remesh。
5. retopo 自动化只能解决大部分，关节、眼周、肩肘膝等变形区域要人工修 loops。
6. UV unwrap 可先自动，复杂部件失败时回 Blender 手工 seam。
7. UV packing 是性能优化，减少 2K/4K 贴图空白浪费。
8. Bake normal 和 AO。跳过 bake 会丢高模细节。
9. Texturing 要避免 diffuse 烘焙光照；UE PBR 更需要干净 Albedo。
10. Roughness、Metallic、Emissive 需要单独绘制或合成。
11. AccuRig/Mixamo 可做快速 humanoid rig，但 marker placement、calibration、weight paint 不能省。
12. Armpit、外套、裙摆、尾巴、头发、肩部是权重高风险区。
13. 需要物理摆动的布料、尾巴、头发要加额外骨骼或 physics bones，再在 UE Physics Asset 中设置。
14. UE 中使用经审核的原型动画或项目动画 retarget；检查 T-pose drift、脚底滑动、clipping、材质槽错位。

### 11.5 Skeletal Mesh 与 Animation 导入

UE 官方要点：

- Skeletal Mesh FBX 可带 mesh、animation、morph targets、vertex colors、LOD。
- FBX 导入自动创建材质时，主要导入 diffuse 和 normal map，不应依赖它完成完整 PBR。
- 单个 Skeletal Mesh 单个 FBX 文件当前只能导入一个动画。
- Skeletal Mesh pivot 总是在 skeleton root bone/joint。
- 多部件 Skeletal Mesh 可以共用同一 skeleton，导入时会组合，不一定有性能惩罚，并可做模块化角色。

动画规则：

- locomotion 原型可用经审核的临时动画或项目动画 retarget。
- 高级 locomotion 可评估 Motion Matching，但需要 Pose Search 数据库和调试成本。
- Anim Notify 用于脚步、攻击窗口、VFX/SFX 触发；Motion Matching 下要注意 Notify Filtering，避免短时间重复触发脚步声。
- Control Rig 适合在 UE Editor/Sequencer 内做 rig 和动画修正。
- Root motion、网络同步和 CharacterMovementComponent 策略必须提前确定。

## 12. 贴图、材质和渲染

PBR 贴图规范：

| 文件 | 通道 | 设置 |
| --- | --- | --- |
| T_Asset_BC | Base Color / Albedo | sRGB on |
| T_Asset_N | Normal | sRGB off，Normal compression |
| T_Asset_ORM | R=AO, G=Roughness, B=Metallic | sRGB off |
| T_Asset_E | Emissive | 按用途确认 |
| T_Asset_M | Mask | sRGB off |

AI 贴图经验：

- AI 贴图常把高光、阴影和环境光烘进 diffuse。进入 UE 前必须检查是否是干净 Albedo。
- 人脸和复杂局部 Multi-View 容易漂移，可用 Single-View + patch brush，再手工修。
- 标志、布章、文字、花纹更适合用 Blender stencil、clone、smear 或 Substance Painter 修。
- 先在 Blender 合成 Base Color、Normal、AO、Roughness、Metallic、Emissive，再导入 UE 验证。
- Tripo 贴图质量可用时默认 textureQuality: "detailed"，但仍要检查接缝、色彩空间和 PBR 通道。

UE 材质规则：

- 建 master material，再派生 material instance。
- 共享材质放 Materials/Core；单资产材质可放同资产目录。
- 运行时改色、伤害闪烁、溶解、湿润等用 Material Instance Dynamic 或 Material Parameter Collection。
- Nanite 资产需检查材质兼容、mask/透明策略和 fallback。
- 贴图尺寸是内存大头。默认不要给普通小道具 4K；hero asset 再按镜头需求批准。

## 13. Niagara、特效和画面反馈

Niagara 规范：

- NS_ 是系统，NE_ 是 emitter。
- User 参数才是 Blueprint/C++ 可直接驱动的外部参数。
- 先定义 gameplay event，再设计 VFX；不要先做漂亮效果再找用途。
- 每个 VFX 必须检查 bounds、culling、spawn rate、GPU/CPU sim、材质 overdraw。
- impact、muzzle flash、hit spark、pickup、status、AOE 等应有 SFX 同步点。

Game feel 规范：

- 命中反馈至少考虑：动画、VFX、SFX、相机震动、hit-stop、UI 数字/提示、控制器震动。
- 可调参数进 DataAsset 或 curve，不硬编码。
- 强反馈先在灰盒里验证，避免美术完成后发现手感不对。

## 14. 音频、语音和音乐

UE 官方要点：

- 导入音频后，UE 内部以 16-bit uncompressed .wav 存为 USoundWave。
- Sound Cue 是运行时抽象 sound object，适合随机化、参数映射、分支、attenuation、pitch/volume 变化。
- Spatialization 和 attenuation 分开配置，可用 Sound Attenuation Settings。
- 2D sound 用于 UI、音乐、非空间化反馈。
- Submix、Sound Class、Source/Bus effects 用于混音和动态控制。
- Property Matrix 适合批量改大量音频资产。
- MetaSound 适合程序化音频、可参数化音源和复杂交互声音。

AI Voice 使用场景：

- 临时 VO、旁白、NPC 台词。
- UI 点击、确认、错误、成就、警告。
- 技能释放、命中、爆炸、机关、环境点缀。
- 30-60 秒 BGM 草案或 loop。
- ASR 转写、分轨、降噪、多人对话标注。

### 14.1 AI 音频/音乐 prompt 详细度规范

音频和音乐 prompt 也应尽量详细。声音资产的质量问题常不是“生成失败”，而是 prompt 没有写清触发时机、镜头距离、循环方式、节奏、动态范围和混音位置，导致结果虽然好听但无法放进游戏。和图片一样，详细 prompt 应在起草和批准阶段完成；调用 AI Voice 或 AIART 音频能力时，应使用 approved prompt 原文，不在工具调用时临场改写。

推荐流程：

1. 先按资产类型写 brief：SFX、VO、BGM、Ambient、UI、Trailer 或 Cinematic。
2. 对 SFX 明确 one-shot、loop、tail、variation、是否可叠加、是否 2D/3D。
3. 对 BGM 明确 BPM、拍号、调性或调式、loop 点、intro/outro、动态层、可否分 stem。
4. 对 VO 明确台词原文、角色、年龄/气质、情绪、语速、停顿、发音、语言和字幕 key。
5. 用户或负责人确认后，写入 approved prompt 和 asset manifest。
6. 生成后在游戏上下文中试听：单独听、和 UI/VFX/动画一起听、在混音里听。

详细 prompt 应包含：

| 字段 | SFX/UI | BGM/Ambient | VO |
| --- | --- | --- | --- |
| 用途 | 触发事件、反馈强度、是否可连续触发 | 场景、战斗/探索/菜单状态、循环方式 | 台词用途、剧情语境、字幕 key |
| 时长 | one-shot/tail/loop、毫秒级目标 | 总时长、loop 小节、intro/outro | 单句时长、停顿位置 |
| 情绪和能量 | 轻/中/重、危险/奖励/错误 | 情绪曲线、紧张度、密度变化 | 情绪、潜台词、是否克制 |
| 节奏 | hit timing、attack/decay | BPM、拍号、groove、bar 对齐 | 语速、重音、呼吸 |
| 音色 | 材质感、机械/有机、干/湿 | 乐器、合成器、打击、音域 | 声线、年龄、口音、音色 |
| 空间 | 2D/3D、距离、房间感 | 宽度、混响、是否贴近镜头 | 近讲/远讲、空间感 |
| 技术限制 | variation 数、可叠加、峰值、无 clipping | loop 无 click/pop、可分层、可 duck | 无噪声、无爆音、口型需求 |
| 禁止项 | 不要旋律、不要人声、不要过长尾音 | 不要版权旋律、不要明显参考现有作品 | 不要改台词、不要多说、不要背景音乐 |

音乐 prompt 不建议写“像某某作曲家/某首歌”。更稳妥的写法是描述可授权的音乐特征：配器、速度、节奏密度、和声复杂度、空间、情绪曲线、混音位置和交互层。这样既利于生成，也利于后续授权和 provenance 记录。

音频入库规则：

| 类型 | 命名 | QA |
| --- | --- | --- |
| SFX | SFX_Source_Action_Variant | 响度、峰值、尾音、是否可叠加、并发策略 |
| VO | VO_Character_LineId_Take | 文本、情绪、发音、停顿、口型需求、授权 |
| BGM | BGM_Scene_Mood_BPM | loop 点、intro、bar 对齐、动态层、ducking |
| Ambient | AMB_Biome_Source_Loop | 无缝循环、空间范围、频段拥挤、随机化 |

正式混音建议：

- UI、VO、BGM、SFX、Ambient 分 Sound Class。
- 关键 gameplay SFX 优先级高于环境音。
- VO 播放时 duck BGM 或部分环境频段。
- 循环音必须听 3 次以上检查 click/pop。
- 同类 SFX 至少 3 个 variation，避免重复疲劳。

## 15. UI、字体、图标和本地化

### 15.1 UMG 与 Common UI

UE5.8 Common UI 适合多层 UI 和跨平台输入：

- 菜单、HUD、弹窗、通知、暂停、设置都应放入明确 UI layer。
- Common UI 输入路由负责焦点、gamepad/keyboard/touch 切换和返回行为。
- 使用 Common Button、Activatable Widget、Action Bar 等建立统一交互。
- HUD 用 Game and UI input mode 或 Common UI 的 input config，不要随意 UIOnly 阻断 gameplay。
- UI 样式使用 DataAsset 或统一 style，不在每个 Widget 内散落颜色和字体。

UI 验收：

- 16:9、21:9、4:3、Steam Deck/掌机、小窗口下不遮挡。
- gamepad、键鼠、触屏焦点都能操作。
- 文本最长本地化字符串不溢出。
- 图标在目标尺寸仍可读。
- 不把技术说明写进玩家 UI。

### 15.2 字体

UE 官方说明：UMG 当前只支持 Runtime cached Font Assets。项目规则：

- 所有自定义字体必须导入 Font Asset，不直接散用文件路径。
- 字体分用途：Font_UI_Body、Font_UI_Title、Font_DamageNumber、Font_Dialogue。
- 中文、英文、数字、标点、全角半角、繁简字体覆盖要单独测试。
- 字体授权必须记录在 asset register。
- UI 中不要用位图里烘焙文字，除非是 logo 或不可本地化装饰。

### 15.3 图标和 UI art

- 简单几何图标优先矢量或可重建源文件。
- AI 生成图标必须统一线宽、视角、填充方式、边缘处理和语义色。
- 图标不包含文字；文字由 UMG Text 渲染。
- 每个按钮状态至少有 normal、hover/focus、pressed、disabled。
- 触控按钮命中区域按平台最小尺寸设置，不等于视觉尺寸。

### 15.4 本地化

UE 本地化围绕 FText。规则：

- 玩家可见文本使用 FText，不用 FString 拼 UI 文本。
- 可复用文本用 String Tables，适合 UI、道具名、技能描述、任务文本。
- 简体中文文化代码用 zh-Hans，繁体用 zh-Hant。
- Localization Target 的 Config 在 Config/Localization，数据在 Content/Localization/{TargetName}。
- LocRes 是运行时加载的编译后数据；导入 PO 后必须 compile。

## 16. 关卡、PCG、Cinematics 和场景生产

关卡 AI 生产流程：

1. 一张概念图定义场景风格、构图和关键物件。
2. 把概念拆成模块资产：地面、桥、墙、门、灯、雕像、植被、标志物、远景。
3. 每个模块生成干净 reference，再生成 3D。
4. Blender 中统一 scale、origin、pivot、命名、材质槽。
5. 可在 Blender 中粗装场景检查 composition，再导出到 UE。
6. UE 中完成 lighting、post process、fog、sky、decals、VFX、音频和 playable path。
7. 用玩家角色作为尺度基准，不只看空场景截图。

PCG 使用规则：

- PCG 适合植被、碎石、装饰、路径边缘、可重复关卡模块。
- 种子、范围、密度、排除区域和 gameplay collision 必须可复现。
- 生成内容不得挡住关键路径、交互点、摄像机和导航。
- PCG 输出进入审计：实例数量、材质、碰撞、overlap、导航、性能。

Cinematics / Sequencer：

- 过场动画用 Level Sequence。
- 摄像机、Control Rig、音频、字幕、UI 隐藏/显示都要有轨道规划。
- AI 生成视频可用于方向参考或宣传草案，不直接代替游戏内过场。
- Movie Render Queue 输出与游戏实时效果要分开管理。

## 17. AI 开发游戏的经验模式

从 Top3D、godogen、everything-game-dev-code、ChrisWiles showcase 和多个 agent/rules 仓库可以总结出这些有效模式：

1. 灰盒先行。先让玩法跑通，再替换资产。不要一开始追求最终画面。
2. 每个功能一个可玩里程碑。自动奔跑、三车道、障碍、金币、分数、Game Over 都应分步交付和提交。
3. 让 AI 看到结果。UE 里用截图、PIE、日志、Data Validation；Web 游戏用 live URL 或录像；不要只看编译通过。
4. 人准备资产，agent 组织和接线。3D、贴图、权重、音频质量需要专门工具和人工判断；Codex/Claude 更适合命名、导入、替换引用、写工具脚本、搭建逻辑。
5. prompt 要写逻辑和架构。模糊请求会得到短期能跑但难扩展的 Blueprint 或代码。
6. Blueprint 自动生成通常逻辑能跑，但图会乱。重要 Blueprint 要规定布局、注释、分组和人工 review。
7. 每个里程碑提交。AI 长会话和 live editor 操作会产生大量状态变化，必须有恢复点。
8. 上下文不要无限堆。一个聊天处理一个 coherent outcome；长任务 compact 或开新任务。
9. 重复错误写回规则。真正有用的 AGENTS.md 和 skills 是从项目事故里长出来的。
10. 证据优先。性能、崩溃、资产质量、UI 适配都要求日志、截图、trace、validation report，而不是“看起来可以”。

### 17.1 AI 自我规范回写机制

不要把所有经验直接堆进 AGENTS.md。AGENTS.md 只保留高频、全局、稳定规则；细节流程进入对应 skill；一次性事故进入 retrospective。

规则沉淀触发条件：

- 同类错误出现两次，例如同一类资产反复缺 pivot、贴图反复烘焙阴影、Widget 反复溢出文本。
- 一次错误造成可见返工，例如覆盖正式资产、错误导入骨骼、误改 Content 目录、MCP 批量写坏 Blueprint。
- 发现新的 UE5.8 事实约束，例如某个 Toolset 只在 Editor 模块可用，或某个命令不能安全重复执行。

规则模板：

~~~text
规则标题：
适用范围：
触发症状：
错误反例：
正确做法：
验证方式：
应写入位置：AGENTS.md / ue58-asset-pipeline / ue58-build-test-runner / ue58-mcp-editor-automation / 仅 retrospective
负责人：
创建日期：
过期或复审条件：
~~~

写入位置判断：

| 内容 | 写入位置 |
| --- | --- |
| 全项目永远适用的禁止项和默认项 | AGENTS.md |
| 资产导入、AIART、Blender MCP、UE import、provenance | ue58-asset-pipeline 或 ue58-blender-mcp-asset |
| 编译、测试、Data Validation、日志路径 | ue58-build-test-runner |
| UE/Blender MCP 写操作、恢复点、截图和日志证据 | ue58-mcp-editor-automation |
| 单次项目事故和取舍 | Docs/Planning 或 retrospective |

## 18. Prompt 合同模板

### 18.1 通用开发任务

~~~text
目标：
实现玩家可感知的结果，不只是改代码。

上下文：
- UE 版本：
- 相关文件/模块/资产：
- 已有设计文档：
- 已知错误或日志：

约束：
- C++/Blueprint 边界：
- 性能预算：
- 不允许修改：
- 命名和目录：

完成标准：
- 构建：
- 自动化测试：
- Data Validation：
- PIE 或截图验证：
- 文档更新：
- Review：
~~~

### 18.2 AIART 图片生成任务

AI 图片 prompt 应该在任务开始时充分起草，在调用前明确批准。最终调用 AIART image_generation 时，prompt 必须使用 approved prompt 原文，也就是 verbatim 传入；agent 不应在工具调用参数里临场翻译、扩写、润色或补充风格词。

~~~text
目标：
为 [资产/场景/UI/贴图] 生成 [用途] 图片，用于 [后续 3D 建模/美术评审/贴图制作/UI 实现/宣传素材]。

Prompt 阶段：
- 需要先起草详细 prompt：是 / 否
- approved prompt：
- 负面约束是否已写入 approved prompt：是 / 否
- 允许 agent 修改 prompt：否，除非本任务后续明确批准

详细 prompt 必须包含：
- 用途：concept / reference pack / texture draft / UI icon / HUD mockup / cutout
- 主体：资产名称、部件、动作、状态、可读 silhouette
- 游戏上下文：玩家视角、镜头距离、屏幕占比、互动功能
- 风格语言：形状语言、细节密度、边缘处理、色彩规则
- 构图/视角：front / side / back / top / 3/4 / top-down / isometric / centered icon
- 光照：中性光、是否允许氛围光、是否禁止强阴影
- 材质：PBR 方向、Base Color、Roughness、Metallic、Emissive、磨损/污渍
- 技术限制：透明背景、无文字/水印、比例尺、参考网格、输出比例
- 禁止项：透视变形、baked light、多余角色、不可本地化文字、遮挡轮廓

AIART 调用默认：
- 工具：image_generation
- inferenceMode: gpt
- prompt: 使用 approved prompt 原文，不改写
- aspectRatio：
- imageCount：1-4
- referenceImagesMax：4
- promptMaxLength：2000

完成标准：
- 记录 approved prompt、参考图、模型/模式、参数、task id
- 保存候选编号和取舍理由
- 标注哪些图片可作为 style reference，哪些可作为 3D reference
- 更新 asset register 或 manifest
~~~

### 18.3 AIART 3D 资产任务

~~~text
目标：
制作 [资产名]，用于 [玩法/场景角色]。

视觉：
- 形状语言：
- 轮廓：
- 材质：
- 语义色：
- 光照：
- 排除：

技术：
- UE 路径：
- 命名：
- 尺寸/比例：
- pivot：
- 面数预算：
- 贴图尺寸：
- collision：
- LOD/Nanite：

生成默认：
- 图片 inferenceMode: gpt
- 质量优先
- Hyper3D 可用时 modelVariant: extremeHigh
- Tripo 贴图可用时 textureQuality: detailed

完成标准：
- 生成候选和来源记录
- DCC 清理建议
- UE 导入设置
- QA checklist
- assetmeta 或 register 记录
~~~

### 18.3.1 Blender MCP 建模任务

~~~text
目标：
用 Blender MCP 制作或清理 [资产名]，最终进入 UE5.8 的 [用途/场景]。

输入：
- 正交参考图：front / side / back / top
- 3/4 效果图：
- 尺寸和比例尺：
- 当前 .blend 或空场景：
- 可用资产库：

Blender 约束：
- 单位：
- collection 结构：REF / BLOCKOUT / HIGH / LOW / COLLISION / EXPORT
- 命名：
- pivot/origin：
- 材质槽：
- poly/tri 预算：
- UV 要求：
- collision proxy：
- LOD/Nanite 策略：
- 不允许修改：

执行方式：
1. 先查询 scene/object/material/camera 状态。
2. 建 reference image planes 和比例尺。
3. 先 blockout，不直接细化。
4. 每轮只修改一个明确部位。
5. 每轮输出 front、side、3/4、wireframe 或 material preview 截图。
6. 结束前检查 scale、normals、non-manifold、duplicate vertices、材质槽、对象命名、未应用 transform。

导出：
- 格式：
- staging 路径：
- UE 目标路径：
- FBX 2020.2 或 GLB 中间格式策略：

完成标准：
- 截图对比通过
- Blender QA 通过
- manifest/provenance 更新
- 未写入正式 Content，除非任务明确批准
~~~

### 18.3.2 AI 3D 生成与返工判断任务

~~~text
目标：
为 [资产名] 生成 [候选数量] 个 3D 候选，并判断继续清理还是重新生成。

输入：
- 用途和镜头距离：
- 目标尺寸：
- 正交参考图：
- 3/4 效果图：
- 材质描述：
- Do/Don't：
- 输出格式限制：

模型选择：
- 图片参考默认 inferenceMode: gpt
- Hyper3D 可用且适合时使用 modelVariant: extremeHigh
- Tripo 贴图可用且适合时使用 textureQuality: detailed
- 其他模型只在当前能力查询确认开放后使用

候选评分：
- 轮廓：
- 比例：
- 部件完整性：
- 拓扑可清理性：
- UV/贴图可修复性：
- 动画或绑定风险：
- UE 导入风险：

返工规则：
- 大轮廓错、比例错、肢体/部件错：重新生成。
- 拓扑大面积不可用、非流形严重、UV 无法展开：重新生成或换模型。
- 少量破洞、法线、pivot、材质槽、scale 问题：交给 Blender MCP 清理。
- 三轮修复仍失败：记录 retrospective，切换生产路径。

交付：
- 候选截图
- 选中候选理由
- 失败候选原因
- 清理任务清单
- manifest/provenance
~~~

### 18.4 贴图/材质任务

~~~text
目标：
为 [资产] 制作或修复 PBR 贴图和 UE 材质。

必须检查：
- Base Color 是否烘焙了阴影/高光
- Normal 是否方向正确
- ORM 通道是否正确
- sRGB 和 compression
- mip 和 TextureGroup
- 接缝、拉伸、重复纹理
- UE 材质槽和 material instance 参数

交付：
- T_Asset_BC
- T_Asset_N
- T_Asset_ORM
- T_Asset_E 可选
- M_ / MI_
- QA 记录
~~~

### 18.5 动画/绑定任务

~~~text
目标：
让 [角色] 在 UE5.8 中完成 [动作/locomotion/技能]。

上下文：
- Skeleton：
- IK Rig / Retargeter：
- AnimBP：
- Root motion 策略：
- 目标动画来源：

必须检查：
- T/A pose
- marker calibration
- armpit/cloth/shoulder/hip 权重
- retarget 后脚滑和 clipping
- Anim Notify
- Motion Matching 下 Notify Filtering
- PhysicsAsset 和 physics bones

完成标准：
- PIE 中播放通过
- 关键截图或录像
- 错误和残留风险记录
~~~

### 18.6 音频任务

~~~text
目标：
制作 [SFX/VO/BGM/Ambient]，用于 [触发场景]。

Prompt 阶段：
- 需要先起草详细 prompt：是 / 否
- approved prompt：
- 允许 agent 修改 prompt：否，除非本任务后续明确批准
- 参考音频/风格依据：只描述音乐和声音特征，不要求复制特定受保护作品

规格：
- 类型：SFX / UI / VO / BGM / Ambient / Cinematic
- 游戏上下文：
- 触发事件：
- 长度：
- 是否 loop：
- 是否 2D/3D：
- 情绪：
- 能量曲线：
- 节奏/BPM/拍号：
- 调性/调式：
- 乐器/音色：
- attack/decay/tail：
- 空间/混响：
- variation 数：
- stem 或动态层需求：
- VO 台词原文：
- VO 角色、语速、停顿、发音：
- 禁止项：
- Sound Cue / MetaSound 需求：
- attenuation / concurrency：
- Sound Class/Submix：
- loudness/peak 目标：

完成标准：
- 源文件和 UE 命名
- approved prompt、模型/声线/参数、task id、license/provenance 已记录
- 响度/峰值检查
- loop 点检查
- variation 可用性检查
- Sound Class/Submix 路由
- provenance 记录
- 在 gameplay 触发场景中试听通过
~~~

### 18.7 UI 任务

~~~text
目标：
实现 [HUD/Menu/Dialog/Inventory]。

约束：
- 使用 UMG/Common UI
- gamepad/keyboard/mouse/touch 可用
- 字体使用 Font Asset
- 玩家可见文本使用 FText/String Table
- 不使用图片烘焙正文

完成标准：
- 多分辨率截图
- 输入焦点和返回行为测试
- 最长文本不溢出
- WBP 命名和 layer 合规
~~~

### 18.8 Retro 回写任务

~~~text
请复盘最近这次 AI 开发失误。

输入：
- 原任务：
- 失败现象：
- 根因：
- 最终修复：
- 哪条规则本来能避免：

输出：
- 建议写入 AGENTS.md 的 1-3 条短规则
- 建议写入哪个 skill
- 不要写泛泛而谈的规则
~~~

## 19. 项目模板

### 19.1 AGENTS.md 初始模板

~~~md
# AGENTS.md

## Project

- Project name: NewWorld
- Engine: Unreal Engine 5.8
- UE install: G:\UnrealEngineInstalled\UE_5.8
- Primary workspace: G:\NewWorld
- Language: Chinese for project docs and user-facing planning unless requested otherwise.

## Codex workflow

- Start by reading this file and .agents/ue-project-context.md when present.
- Keep tasks scoped to one coherent outcome.
- For complex UE work, gather evidence first, then implement.
- Use subagents for read-heavy exploration, logs, docs, asset audits, and trace analysis.
- Do not run large live-editor or Content changes without a Git recovery point.
- When the same mistake happens twice, write a short retrospective and propose a rule or skill update.

## MCP workflow

- Treat UE MCP, Blender MCP, and editor toolsets as automation with side effects.
- Start with read-only discovery and scene/asset queries.
- Do not enable UE ModelContextProtocol auto-start by default.
- Do not overwrite .codex/config.toml from UE tools; generate a draft or merge manually.
- Blender MCP writes should stay in a staging .blend or export folder until QA passes.
- After any MCP write batch, report changed objects/assets, screenshot evidence, logs, and remaining risk.

## Unreal conventions

- Use UE5.8 APIs and verify version-specific behavior.
- Follow Epic-style asset prefixes and [Prefix]_[Name]_[Descriptor]_[Variant].
- Stable runtime logic belongs in C++; designer-facing tuning belongs in Blueprint/DataAssets.
- Avoid Tick unless justified by behavior and budget.
- UObject references must be GC-safe.
- Editor-only code belongs in an Editor module or Editor Utility workflow.

## AI asset rules

- AIART image generation defaults to inferenceMode: "gpt".
- Quality is preferred over speed/cost unless the task says otherwise.
- Hyper3D should use modelVariant: "extremeHigh" when available and suitable.
- Tripo texture should use textureQuality: "detailed" when available and suitable.
- AI assets enter Content/NewWorld/AIWork first.
- Blender MCP is preferred for blockout, hard surface cleanup, pivot, collision proxy, LOD prep, image-plane reference matching, and export staging.
- AI 3D generation is preferred for irregular organic candidates, style exploration, and rough high-poly sources that will be retopologized.
- Production assets require provenance, QA, UE import review, and Data Validation.

## Verification

- Compile after C++ header/reflection changes.
- Run targeted Automation tests when available.
- Run Data Validation before accepting asset-heavy changes.
- For UI, verify keyboard/mouse/gamepad and multiple resolutions.
- For performance claims, provide trace/stat/log evidence.

## Code Review Rules

- Flag unsafe UObject lifetime, missing UPROPERTY/TObjectPtr, invalid async captures, unnecessary Tick, unbounded spawning, hard references that should be soft references, replication mistakes, editor/runtime module leaks, missing validation, and unreviewed AI assets.
~~~

### 19.2 .agents/ue-project-context.md 初始模板

~~~md
# UE Project Context

Engine version: Unreal Engine 5.8
Engine install: G:\UnrealEngineInstalled\UE_5.8
Project root: G:\NewWorld
Project file: TBD
Target platforms: Windows first, others TBD
Renderer: TBD
Source build or launcher build: TBD

## Modules

Primary game module: TBD
Runtime modules: TBD
Editor modules: TBD
Plugins: EnhancedInput, CommonUI, Niagara, PCG, GameplayAbilities, MetaSounds, DataValidation as needed
Selected MCP plugins enabled for Editor targets: ModelContextProtocol, MCPClientToolset, EditorToolset, GameplayTagsToolset, UMGToolSet, NiagaraToolsets, PCGToolset, AIModuleToolset, AutomationTestToolset, SlateInspectorToolset
Experimental AI plugin kept disabled: AIAssistant

## Project rules

C++ owns stable runtime systems.
Blueprint owns designer-facing composition and tuning.
DataAssets/DataTables/Gameplay Tags own content configuration.

## Verification commands

Data Validation:
G:\UnrealEngineInstalled\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe <PROJECT>.uproject -run=DataValidation

Build, automation, packaging: TBD after .uproject exists.

## Asset policy

AIWork is staging only.
Formal assets need naming, import review, metadata, and validation.

## MCP policy

UE MCP default assumption: experimental, Editor target only, manual start, 127.0.0.1:8000/mcp, tool search enabled.
Blender MCP default assumption: safe mode on, one client connected, staging only.
No MCP tool may batch-write production Content without manifest, recovery point, screenshot/log evidence, and Data Validation plan.
~~~

### 19.3 custom agent TOML 示例

~~~toml
name = "technical-artist"
description = "UE5.8 technical art agent for AI assets, materials, textures, LODs, Nanite, collision, pivots, and Data Validation."
model = "gpt-6-astra"
model_reasoning_effort = "high"
developer_instructions = """
Work as a UE5.8 technical artist.
Inspect project context before giving asset guidance.
Treat generated assets as candidates until DCC cleanup, UE import settings, in-scene review, and provenance are complete.
Prefer evidence: asset paths, import settings, screenshots, validation output, and concrete remaining risks.
Do not overwrite production assets without a staged replacement and recovery point.
"""
~~~

~~~toml
name = "ue-reviewer"
description = "Read-only UE5.8 reviewer focused on correctness, UObject lifetime, assets, performance, tests, and production risk."
model = "gpt-6-astra"
model_reasoning_effort = "high"
developer_instructions = """
Review like an Unreal project owner.
Find bugs, regressions, unsafe UObject lifetime, missing tests, asset policy violations, performance risks, and unclear ownership.
Lead with findings ordered by severity and cite files, assets, logs, or docs.
Do not rewrite code unless the parent agent explicitly asks.
"""
~~~

~~~toml
name = "asset-pipeline"
description = "Plans and audits AIART and AI Voice asset production for UE5.8, including manifests, provenance, QA, and import handoff."
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
developer_instructions = """
Own the asset manifest and production handoff.
For every generated asset, define role, path, prompt, model, parameters, source references, license/provenance, technical contract, QA checklist, and approval state.
Never call an AI output production-ready without technical and in-engine validation.
"""
~~~

~~~toml
name = "blender-mcp-artist"
description = "Uses Blender MCP for reference-image blockout, hard-surface assets, module kits, cleanup, collision proxy, LOD prep, screenshots, and UE export staging."
model = "gpt-5.6-sol"
model_reasoning_effort = "high"
developer_instructions = """
Work as a Blender technical artist connected through MCP.
Start with scene and object inspection before editing.
Use reference image planes, metric scale, named collections, staged exports, and screenshot comparison.
Do not execute broad Python, filesystem, network, or production Content writes unless the task explicitly scopes them.
Return changed objects, screenshots needed, export paths, QA status, and remaining risks.
"""
~~~

~~~toml
name = "mcp-safety-reviewer"
description = "Read-only reviewer for UE MCP and Blender MCP operation plans, focusing on side effects, recovery points, tool scope, logs, and validation evidence."
model = "gpt-6-astra"
model_reasoning_effort = "high"
developer_instructions = """
Review MCP plans before execution.
Check whether the plan starts read-only, limits write scope, avoids config overwrite, records a recovery point, and defines screenshots/logs/Data Validation.
Flag unsafe batch writes, production asset overwrites, unbounded Python execution, network exposure, missing provenance, and vague success criteria.
Do not execute tools or edit assets.
"""
~~~

### 19.4 AI asset register 模板

~~~md
# AI Asset Register

## SM_AI_Rock_Cliff_A_WIP

- Role: greybox replacement for exploration cliff set
- Status: WIP
- creation_route: ai_3d_then_blender
- route_decision_reason: organic mid-distance cliff prop where silhouette variation matters more than exact dimensions
- authoring_tools: AIART model3d, Blender, UE MCP
- reference_pack_required: true
- route_review_status: pending
- Source tool: AIART model3d
- Model/provider: Hyper3D Gen 2.5
- Parameters: modelVariant=extremeHigh, polygonType=triangle, target faces TBD, texture size TBD
- Prompt status: draft / approved / generated
- Approved prompt: TBD
- Prompt call rule: pass approved prompt verbatim to AIART; no silent rewrite
- References: front/side/back/top orthographic, 3/4 beauty, silhouette, material swatches
- Generated at: TBD
- Task/request id: TBD
- Candidate count: TBD
- Selected candidate reason: TBD
- Blender staging file: TBD
- Blender MCP screenshots: front, side, 3/4, wireframe, material preview
- Staging path: Content/NewWorld/AIWork/Environment/Rocks/
- Final path: TBD
- License/provenance: generated, terms reviewed TBD
- DCC cleanup: scale, pivot, normals, duplicate vertices, UV, retopo, collision
- UE import QA: material slots, Nanite/LOD, collision, bounds, Data Validation
- Approval owner/date: TBD
~~~

### 19.5 JSON manifest 模板

~~~json
{
  "schema_version": 2,
  "project": "NewWorld",
  "staging_root": "Content/NewWorld/AIWork",
  "production_root": "Content/NewWorld",
  "art_direction_brief": "Docs/Art/ART_DIRECTION_BRIEF.md",
  "asset_production_routes": "Docs/Assets/ASSET_PRODUCTION_ROUTES.md",
  "assets": [
    {
      "asset_id": "SM_AI_Rock_Cliff_A_WIP",
      "asset_type": "static_mesh",
      "status": "draft_prompt",
      "creation_route": "ai_3d_then_blender",
      "route_decision_reason": "Organic mid-distance cliff prop where silhouette variation matters more than exact dimensions.",
      "authoring_tools": ["AIART model3d", "Blender", "UE MCP"],
      "reference_pack_required": true,
      "route_review_status": "pending",
      "staging_path": "Content/NewWorld/AIWork/Environment/Rocks/",
      "target_path": "TBD",
      "prompt": {
        "approved": false,
        "text": "",
        "provider": "AIART",
        "model": "Hyper3D",
        "parameters": {
          "modelVariant": "extremeHigh"
        },
        "candidate_count": 3,
        "call_rule": "pass approved prompt verbatim"
      },
      "provenance": {
        "source_tool": "",
        "script": "",
        "operation_record": "",
        "seed": "",
        "created_at": "",
        "license_or_terms": ""
      },
      "qa": {
        "selected_candidate_reason": "",
        "dcc_cleanup": false,
        "blender_mcp_screenshots": [],
        "ue_import_review": false,
        "in_scene_review": false,
        "approved_by": ""
      },
      "validation": {
        "data_validation": false,
        "lod_or_nanite_policy": "TBD",
        "collision": "simple or UCX",
        "texture_budget": "2048 default unless hero asset"
      }
    }
  ]
}
~~~

## 20. 各资产类型验收清单

| 类型 | 必须通过 |
| --- | --- |
| Concept / Styleboard | 真实 game camera、语义色、形状语言、Do/Don't、可拆资产清单 |
| AI Image Prompt | approved prompt 已写完整用途、主体、游戏上下文、风格、视角、光照、材质、技术限制和禁止项；AIART 调用逐字传入 |
| Reference Pack | front/side/back/top 正交、3/4、silhouette、比例尺、材质色板、部件拆解、无透视变形 |
| AI 3D Candidate | 多候选、轮廓/比例/拓扑/UV/贴图评分、重生成或清理判断、provenance |
| Blender MCP Output | scene 查询、image planes、单位、collection、命名、applied transform、截图对比、staging export |
| UE MCP Batch | 只读发现、写入范围、恢复点、修改资产列表、截图/PIE、日志、Data Validation 计划 |
| Static Mesh | scale、pivot、normals、UV、materials、LOD/Nanite、collision、bounds、Data Validation |
| Skeletal Mesh | skeleton、root、skin weights、PhysicsAsset、LOD、materials、retarget 姿势、clipping |
| Animation | 命名、skeleton 匹配、root motion、notifies、loop、foot sliding、blend、network 策略 |
| Texture | 分辨率、sRGB、compression、mip、BC/N/ORM/E 通道、seams、无 baked light |
| Material | master/instance、参数命名、Nanite/透明兼容、shader cost、MPC/MID 策略 |
| Niagara | User 参数、bounds、spawn rate、culling、overdraw、生命周期、SFX 同步 |
| Audio/Music Prompt | approved prompt 已写触发场景、时长、loop、BPM/节奏、音色、空间、variation、禁止项和 UE 落地方式；调用时原文传入 |
| SFX | 响度、峰值、尾音、variation、concurrency、attenuation、Sound Class/Submix |
| VO | 文本、情绪、发音、授权、口型需求、字幕 key、本地化 |
| BGM | loop、BPM、intro/outro、动态层、ducking、场景切换 |
| UI/WBP | CommonUI layer、焦点、safe area、多分辨率、最长文本、字体、图标状态 |
| Font | Font Asset、Runtime cached、中文/英文/数字覆盖、授权 |
| Localization | FText、String Table、文化代码、PO/LocRes 编译、伪本地化测试 |
| Level/PCG | 玩家尺度、可走路径、导航、碰撞、密度、遮挡、性能、可复现 seed |
| Cinematic | Level Sequence、camera、audio、subtitle、Control Rig、MRQ/实时差异 |

## 21. 首批落地优先级

1. 初始化 Git 和大文件策略。
2. 创建 UE5.8 项目后补全 .uproject、Source、Config、插件列表。
3. 写入 AGENTS.md 和 .agents/ue-project-context.md。
4. 后续确认后再安装 gamedev-skills 和 quodsoler UE skills；本次文档调研不执行安装。
5. 创建 ue58-project-standards、ue58-build-test-runner、ue58-asset-pipeline 三个核心 skills。
6. 增加 ue58-mcp-editor-automation 和 ue58-blender-mcp-asset 两个专项 skills。
7. 创建 .codex/agents 中的 ue-reviewer、technical-artist、asset-pipeline、blender-mcp-artist、mcp-safety-reviewer、qa-automation。
8. 建立 Content/NewWorld/AIWork 和 Docs/Assets/AI_ASSET_REGISTER.md。
9. 建立项目级 .codex/config.toml，接入 unreal-mcp 和 blender MCP。
10. 启用精选 UE5.8 MCP Toolsets，但保持手动启动、tool search、staging 写入和审计模板。
11. 跑 MCP readiness、Data Validation 和一次本地 review，把发现的问题回写到 AGENTS.md 或 skill。
12. 做第一个 playable vertical slice：灰盒玩法、最小 UI、临时 SFX、一个经过完整流程的 3D 资产。

## 22. 不建议一开始做的事

- 不要全量安装大型通用 skills/agents 市场。
- 不要在没有 Git 恢复点时让 live editor MCP 批量改 Content。
- 不要启用 AllToolsets、AIAssistant 或第三方 Unreal MCP 作为默认生产依赖；当前精选 UE MCP 只能手动启动并按审计流程使用。
- 不要让 Blender MCP 在没有正交参考图、尺寸和验收清单时制作复杂资产。
- 不要连续修复明显失败的 AI 3D 模型；达到返工阈值后应重新生成或换路径。
- 不要把 AI 生成模型直接放进正式目录。
- 不要把概念图当贴图，尤其是带 baked lighting 的 diffuse。
- 不要过早投入完整 Motion Matching、GAS、复杂联网或开放世界，除非 vertical slice 明确需要。
- 不要用一个长聊天推进整个项目。
- 不要只让 AI “做得更好看”；必须给风格、技术、验收和上下文。

## 23. 后续扩展

项目进入稳定开发后，再考虑：

- 把本手册拆成 Docs/Art、Docs/Engineering、Docs/QA、Docs/Production 多文档，并用 AGENTS.md 指向。
- 将 ue58 系列 skills 打包为个人或团队 plugin。
- 扩展 UE MCP Toolsets 前先做单独评审，尤其是 AllToolsets、AIAssistant、GameFeatures、GAS、LiveCoding、PluginToolset。
- 把项目通过验证的 Blender 工作流继续沉淀到 ue58-blender-mcp-asset skill。
- 持续维护 MCP 操作审计模板，记录工具调用、修改资产、截图、日志、回滚方式和验收结论。
- 扩展 Data Validation 自定义 validators，继续覆盖贴图压缩、材质实例、音频 routing、UI 字体和本地化规则。
- 建立 scheduled task：每周内容审计、每周文档漂移检查、每个里程碑性能 trace。
- 把 Blender、Substance、REAPER、AIART、AI Voice 的内部最佳实践蒸馏成项目 skills。
