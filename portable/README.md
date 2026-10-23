# 化工设计与CAD制图：便携Skill与独立规范包

发行版本：1.0.0｜2026-10-19｜skill名：`chemical-plant-cad-design`。

本包可整体复制到另一台电脑、另一个盘符或中文/空格目录。原始资料、软件、账号和缓存不随包迁移。

## 1. 包含什么

```text
portable/
  README.md                         本说明
  install.py                        Python标准库离线安装器
  manifest.json                     文件与SHA-256校验清单
  迁移验收记录.md                    本次真实验证范围及待执行项
  规范/
    README.md                       独立规范入口
    01_...md 至 14_...md             完整参考与表单
  skills/
    chemical-plant-cad-design/
      SKILL.md                      AI技能入口
      agents/openai.yaml            显示信息
      references/                   同版规范，安装后独立可用
```

- 只阅读或人工执行：复制整个`规范/`，打开其中的[README](规范/README.md)，不需要Python或Codex。
- 让AI按规范工作：安装`skills/chemical-plant-cad-design`。安装后的skill内已带完整规范，不依赖旁边的`规范/`目录。
- 需要实际绘图：目标电脑另具备适合的CAD、生成库或插件；此包没有内置AutoCAD、text-to-cad、uv、商业字体或原生DWG转换器。

## 2. 新电脑安装：推荐流程

先完整解压，不在压缩包内运行。以下命令在解压后的`portable`目录执行。

### Windows

有Python 3.9或更高版本时：

```powershell
py -3 install.py --verify-only
py -3 install.py --dry-run
py -3 install.py
```

若电脑使用`python`命令而没有`py`启动器，将`py -3`换成`python`。安装器仅用标准库，不会执行pip、联网下载或修改CAD和系统环境变量。

### Linux或macOS

```bash
python3 install.py --verify-only
python3 install.py --dry-run
python3 install.py
```

默认安装到目标电脑当前用户的`~/.agents/skills/chemical-plant-cad-design`。这是本次官方文档列示的用户级发现位置；具体宿主若采用其他目录，使用下方明确目标选项。官方文档说明见[Build skills](https://learn.chatgpt.com/docs/build-skills)。

安装输出`installed`表示文件已复制并逐字节核对；不等于实际绘图工具和工程方案已验证。`unchanged`表示内容完全相同，无须重复安装。

## 3. 旧环境或自定义目录

### 采用CODEX_HOME或旧式.codex目录

```bash
python install.py --profile codex --dry-run
python install.py --profile codex
```

该模式采用当前环境的`CODEX_HOME/skills`；未设置时使用当前用户的`~/.codex/skills`。这是为已有运行环境提供的兼容选项，不会额外修改配置。

### 明确安装位置

```bash
python install.py --target "要安装到的skills父目录" --dry-run
python install.py --target "要安装到的skills父目录"
```

`--target`指父目录，程序会自动追加`chemical-plant-cad-design`，不要把同名skill目录再重复写一层。

### 放在某个代码项目里

在该项目目录执行安装脚本的实际路径，并传入：

```bash
python /解压位置/portable/install.py --target .agents/skills
```

路径仅是命令占位示意，替换成实际位置。安装器相对于自身定位包文件，不要求工作目录固定。

不要同时在用户级、项目级和旧式目录重复安装同名技能；官方说明同名技能不会自动合并。若列表出现两个同名项，核对并保留本项目需要的一处。

## 4. 没有Python时手动安装

完整复制`skills/chemical-plant-cad-design/`，包括`SKILL.md`、`agents/`和`references/`，到宿主实际读取的skills父目录。不能只复制`SKILL.md`或把所有规范散放到skills根目录。

手动安装不会自动执行校验，至少核对相对目录完整，并在有Python时运行发行包的`--verify-only`。规范独立阅读不需要执行安装。

## 5. 使用方法

在支持`$skill-name`的Codex入口中，例如：

```text
使用 $chemical-plant-cad-design，按课程设计阶段整理厂区总图的设计输入，
先根据已知厂界画底图，缺少的危险性和设备条件集中列出，不编造安全距离。
```

```text
使用 $chemical-plant-cad-design，核查这份P&ID与设备表的位号、数量、
管线及跨图连接，先出问题清单，保留原图。
```

```text
使用 $chemical-plant-cad-design，按03号规范设置CAD图层和字高，
说明米模型到纸面毫米的比例换算，并给出实际检查步骤。
```

也可直接描述化工设计或制图任务，由宿主匹配技能。若安装后没有出现，重新打开或重启宿主后检查；不同产品的选择界面可能不同，不能假定所有聊天产品使用相同按钮。

## 6. 在其他AI工具中使用

标准`SKILL.md`及参考文件可作为支持此类目录结构的工具的输入，但发现目录和调用方式由各工具决定，本包不宣称已测试所有宿主。

不支持skills的工具也可以使用`规范/`：把相关章节提供给它，要求区分项目约定、课程资料和待核验标准，并引用章节。不要声称上传规范后AI已经获得CAD软件控制权限。

## 7. 迁移后必须重新确认

|项目|目标电脑需要做的事|
|---|---|
|skill发现|确认实际列表出现，能读相对参考|
|原始资料|需要复核时再提供，不要求原作者盘符存在|
|标准适用|按当前项目和日期核验；历史核验日期不自动更新|
|字体、图块、模板|从合法来源配置并试出图；本包只提供规则|
|绘图与渲染|检查本机实际工具，验证最小图及保存文件|
|DWG版本|确认接收方要求，不能以DXF/STEP替代而不说明|
|坐标与单位|重新做已知长度、比例、北向及标高检查|

详细步骤见[14号规范](规范/14_工具能力与迁移.md)和[迁移验收记录](迁移验收记录.md)。

## 8. 重复安装、更新与移除

安装器不覆盖不同内容的现有目录。更新时先在宿主外备份旧skill，比较自己改过的内容，再将新版本安装到明确的目标；不得为绕过冲突盲目删除旧目录。

如果出现中途写入失败，安装器会报告新目录位置并保留现场，不自动递归删除用户路径；检查该目录后再处理。卸载时通过宿主支持的管理方式，或确认准确skill目录后自行移走，只处理这个skill，不动其他技能和规范。

校验清单用于发现丢失、意外修改或传输损坏，不是发行者数字签名，不能证明来源可信。更改发行包后需要由维护者重新校验和更新manifest；普通使用请保持发行包不变，把项目改动写到项目工作目录。

## 9. 维护约定

发行包内`skills/chemical-plant-cad-design/references/`作为参考规范维护源，`规范/`是其同版独立阅读副本。两处应由发布过程同步，不能各改一套。

与早期根目录14份原始规范相比，便携版保留设计要求和来源标识，移除了开发机路径与已安装环境的假定，并新增能力与迁移章节。原根目录文件可继续作为历史版本，后续跨电脑分发以本`portable`目录为准。
