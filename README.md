# NewWorld

NewWorld 是一个基于 Unreal Engine 5.8 的 3D 游戏项目模板，目标是为后续游戏研发提供清晰的工程结构、内容规范、AI 资产流程和可验证的自动化基础。

当前仓库主要完成了 UE5.8 C++ 工程初始化、编辑器模块、项目级 Codex 工作流、AI 资产登记与验证，以及 UE MCP/Blender MCP 的受控演练。游戏的具体类型、核心玩法、角色、关卡和正式内容仍待定义与制作。

## 当前阶段

项目目前处于：

```text
工程初始化与生产管线建设
        ↓
产品定义与核心玩法原型
        ↓
第一个可玩垂直切片
        ↓
全面生产
```

近期目标是完成产品定义，并制作一个 5～15 分钟可重复游玩的灰盒核心玩法原型。原型通过内部验证后，再进入垂直切片阶段。

## 技术环境

- 引擎：Unreal Engine 5.8
- 引擎路径：`G:/UnrealEngineInstalled/UE_5.8`
- 项目文件：`NewWorld.uproject`
- 当前目标平台：Windows 优先
- 运行模块：`NewWorld`
- 编辑器模块：`NewWorldEditor`
- 代码语言：C++
- 设计与调优：Blueprint、DataAssets、DataTables、Gameplay Tags

## 目录结构

```text
NewWorld/
├─ Config/                         项目与编辑器配置
├─ Content/NewWorld/               项目正式内容根目录
│  ├─ AIWork/                      AI/MCP 资产暂存区，不直接视为正式内容
│  ├─ Art/                         美术资源
│  ├─ Audio/                       音频资源
│  ├─ Blueprints/                  Blueprint 资源
│  ├─ Characters/                  角色资源
│  ├─ Environment/                 环境资源
│  ├─ Maps/                        地图资源
│  ├─ UI/                          UI 资源
│  └─ VFX/                         特效资源
├─ Docs/                           项目手册、规划、资产和提示词文档
├─ Source/NewWorld/                运行时代码
├─ Source/NewWorldEditor/          编辑器代码与 Data Validation
├─ Tools/                          AI、MCP、资产导出和项目工具
├─ .agents/                        项目上下文与技能索引
└─ .codex/                         项目级 Codex 配置、技能和 agents
```

## 开发原则

- 稳定的运行时逻辑放在 C++。
- 面向设计师的组合与调优放在 Blueprint。
- 内容配置使用 DataAssets、DataTables 和 Gameplay Tags。
- 所有项目内容放在 `Content/NewWorld` 下。
- AI/MCP 生成内容先进入 `Content/NewWorld/AIWork`，完成来源记录、清理、导入检查和验证后才能晋升为正式资产。
- 正式资产遵循 `[Prefix]_[Name]_[Descriptor]_[Variant]` 命名格式。
- UE MCP 默认仅手动启动，编辑器自动化写入必须经过范围审计和 Git 恢复点。
- 编辑器专用代码放在 `NewWorldEditor` 模块。

详细规则请先阅读 [AGENTS.md](AGENTS.md)、[项目上下文](.agents/ue-project-context.md) 和 [UE5.8 开发手册](Docs/AI_Codex_UE58_GameDev_Guide.md)。

商业游戏从立项到上线、运营和停运的阶段划分，参见 [完整游戏项目生命周期](Docs/Planning/GAME_PROJECT_LIFECYCLE.md)。

## 常用命令

在项目根目录执行。

### 生成项目文件

```powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/ThirdParty/DotNet/10.0/win-x64/dotnet.exe G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll -ProjectFiles -Project=G:/NewWorld/NewWorld.uproject -Game -Progress
```

### 编译编辑器目标

```powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Build/BatchFiles/Build.bat NewWorldEditor Win64 Development -Project=G:/NewWorld/NewWorld.uproject -WaitMutex -NoHotReload
```

### 运行项目检查

```powershell
python Tools/AI/check_ai_readiness.py
python Tools/AI/validate_ai_asset_manifest.py Docs/Assets/AI_ASSET_MANIFEST.json
python Tools/MCP/check_mcp_readiness.py
```

### 运行 UE Data Validation

```powershell
G:/UnrealEngineInstalled/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe G:/NewWorld/NewWorld.uproject -run=DataValidation -unattended -nop4 -nosplash
```

## 资产流程

AI 或 MCP 参与的资产遵循以下流程：

```text
需求与参考资料
  → 路线选择与提示词审批
  → AIWork 暂存
  → DCC 清理或 Blender 处理
  → UE 导入与场景内检查
  → 来源与 QA 记录
  → Data Validation
  → 晋升为正式内容
```

相关文档：

- [资产生产路线](Docs/Assets/ASSET_PRODUCTION_ROUTES.md)
- [AI 资产清单](Docs/Assets/AI_ASSET_MANIFEST.json)
- [AI 资产登记](Docs/Assets/AI_ASSET_REGISTER.md)
- [AI 资产 QA 清单](Docs/Assets/AI_ASSET_QA_CHECKLISTS.md)
- [MCP 操作审计](Docs/Planning/MCP_OPERATION_AUDIT.md)

## 下一步

1. 确定游戏类型、目标玩家和一句话产品定位。
2. 定义核心体验与核心玩法循环。
3. 明确首个原型的成功标准和范围边界。
4. 制作玩家、摄像机、核心动作、交互对象和灰盒地图。
5. 完成一轮 5～15 分钟的内部试玩与复盘。
6. 根据原型结果决定进入垂直切片、调整方向或停止投入。
