# Prompt List

> [!NOTE]
> 该项目是使用 [cookiecutter](https://github.com/Comfy-Org/cookiecutter-comfy-extension) 模板创建的。它可以帮助你开始编写自定义节点，而无需担心 Python 环境配置。

> 如果你的环境 python 与 ComfyUI 的版本不一致
> (可执行 `python` `import sys; print(sys.executable)` 命令验证是否一致)，
> 可以:
> 
> - 将后续的 python 命令修改为 `../../../python_embeded/python.exe`，`pip ...` 命令替换为 `../../../python_embeded/python.exe -m pip ...`
> - 或 `$env:Path = "../../../python_embeded;" + $env:Path` 添加到临时环境变量中，pip 替换为 `python -m pip ...`。
> - 或设置你 IDE 相关的设置 (如 VSCode 的 `.vscode/launch.json`)。

## 开发

要安装开发依赖和 pre-commit（将运行 ruff hook），请执行：

```bash
cd prompt-list
pip install -e .[dev]
pre-commit install
```

上面的 `-e` 标志将产生一种“实时”安装，也就是说，你对节点扩展所做的任何更改都会在你下次运行 ComfyUI 时自动生效。

## 发布到 Github

安装 Github Desktop，或按照这些[说明](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)配置 ssh。

1. 创建一个与目录名匹配的 Github 仓库。
2. 将文件推送到 Git
```bash
git add .
git commit -m "project scaffolding"
git push
``` 

## 编写自定义节点

一个示例自定义节点位于 [node.py](src/prompt_list/nodes.py)。要了解更多信息，请阅读[文档](https://docs.comfy.org/essentials/custom_node_overview)。

## 测试

此仓库在 `tests/` 目录中包含用 Pytest 编写的单元测试。建议对你的自定义节点进行单元测试。

- [build-pipeline.yml](.github/workflows/build-pipeline.yml) 将在任何打开的 PR 上运行 pytest 和 linter
- [validate.yml](.github/workflows/validate.yml) 将运行 [node-diff](https://github.com/Comfy-Org/node-diff) 以检查破坏性更改

## 发布到 Registry

如果你希望将此自定义节点分享给社区中的其他人，可以将其发布到 registry。我们已经在 `pyproject.toml` 的 `tool.comfy` 下自动填充了一些字段，但请再次检查它们是否正确。

你需要在 https://registry.comfy.org 上创建一个账户，并创建一个 API 密钥令牌。

- [ ] 前往 [registry](https://registry.comfy.org)。登录并创建一个发布者 ID（即你 registry 个人资料中 `@` 符号之后的所有内容）。
- [ ] 将发布者 ID 添加到 pyproject.toml 文件中。
- [ ] 在 Registry 上创建一个 API 密钥，用于从 Github 发布。[说明](https://docs.comfy.org/registry/publishing#create-an-api-key-for-publishing)。
- [ ] 将其添加到你的 Github Repository Secrets 中，名称为 `REGISTRY_ACCESS_TOKEN`。

每次 git push 时都会运行一个 Github action。你也可以手动运行该 Github action。完整说明见[此处](https://docs.comfy.org/registry/publishing)。如果你有任何问题，请加入我们的 [discord](https://discord.com/invite/comfyorg)！
