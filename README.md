# 化工设计与 CAD 制图 Skill

面向 Codex 等支持 SKILL.md 的 AI 工具，提供化工设计与制图的工作方法、项目绘图约定、表单和校审清单。

## 支持的工作

- 厂区总平面、道路、竖向与管廊
- PFD 工艺流程图与 P&ID 管道仪表流程图
- 车间与设备布置、标高与检修空间
- 管道布置、轴测、设备图及管口方位
- 图层、线宽、文字、单位与比例设置
- 设备、管线与仪表的一致性检查

技能名称：`chemical-plant-cad-design`。便携包版本：1.0.0。

## 安装

下载本仓库 ZIP 并解压，进入 `portable` 文件夹。需要 Python 3.9 或更高版本，安装器仅使用标准库。

Windows：

```powershell
py -3 install.py --verify-only
py -3 install.py --dry-run
py -3 install.py
```

macOS / Linux：

```bash
python3 install.py --verify-only
python3 install.py --dry-run
python3 install.py
```

默认目标为 `~/.agents/skills/chemical-plant-cad-design`。使用既有 `.codex/skills` 或 `CODEX_HOME/skills` 环境时，安装命令改为：

```bash
python install.py --profile codex --dry-run
python install.py --profile codex
```

也可通过 `--target` 明确指定技能父目录。安装后重新打开 Codex，确认技能已被发现。已有同名且内容不同的技能不会被自动覆盖。

完整说明与无 Python 手动安装方法见 [便携包说明](portable/README.md)。

## 使用示例

```text
使用 $chemical-plant-cad-design，整理厂区总图设计输入，
先完成已确认厂界的基础底图，缺少的物料危险性和设备条件集中列出。
```

```text
使用 $chemical-plant-cad-design，核查这份 P&ID 与设备表的位号、数量和跨图连接，
先出问题清单，保留原图。
```

## 独立阅读

不使用 AI 技能也可以直接阅读 [规范目录](portable/规范/README.md)。

## 工具与适用范围

本仓库提供规则和参考资料；实际建模、绘图、DWG 编辑及打印需要目标电脑具备相应工具。通用 `cad`、`dxf` 等技能需另外安装。

资料中的项目默认约定、历史课程资料与现行标准有各自适用范围，工程使用须核验当前项目的标准与设计输入。原始 PDF/PPT/DWG 和商业 CAD 软件不随包提供。

## 验证

便携包附文件 SHA-256 校验与安装器测试：

```bash
python -B portable/install.py --verify-only
python -B portable/tests/test_install.py
```

[迁移验收记录](portable/迁移验收记录.md) 说明已有验证及目标电脑尚需完成的检查。

## 资料来源与许可

历史资料来源见 [资料来源与标准核验记录](portable/规范/13_资料来源与标准核验记录.md)。本仓库暂未附开源许可证；第三方资料的权利归相应权利人。
