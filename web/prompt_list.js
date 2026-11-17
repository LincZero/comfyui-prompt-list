import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "PromptList.ShowText",
    async beforeRegisterNodeDef(nodeType, nodeData, app) { // 节点注册事件
        // 只对 PromptList_Show 节点生效
        if (nodeData.name !== "PromptList Show") return;
        console.log('debug init prompt_list Show 事件888', nodeData.name)

        // 在节点创建时，添加一个只读的多行文本框作为显示区域
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated?.apply(this, arguments);

            // 添加一个多行文本控件，用于显示内容
            const w = ComfyWidgets["STRING"](this, "display_text", ["STRING", { multiline: true }], app).widget;
            w.inputEl.readOnly = true;          // 只读
            w.inputEl.style.opacity = 0.6;     // 稍微透明，表明是展示用
            w.inputEl.style.fontFamily = "monospace"; // 等宽字体，适合显示 JSON

            return r;
        };

        // 当节点执行完成后，用 ui 中的数据更新这个文本框
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            // message.text 就是 Python 端返回的 ui.text 列表
            if (message?.text && Array.isArray(message.text)) {
                const displayWidget = this.widgets?.find(w => w.name === "display_text");
                if (displayWidget) {
                    displayWidget.value = message.text.join("\n");
                    // 触发画布重绘，让文字立即显示出来
                    app.graph.setDirtyCanvas(true, true);
                }
            }
        };
    },
});

app.registerExtension({
    name: "PromptList.CreateDynamicInputs",
    async nodeCreated(node) {
        // 只对 PromptList_Create 节点生效
        if (node.comfyClass !== "PromptList Create") return;
        console.log('debug init prompt_list create 事件', nodeData.name)

        // 找到 inputcount 这个 widget
        const inputCountWidget = node.widgets.find(w => w.name === "inputcount");
        if (!inputCountWidget) return;

        // 添加“Update Inputs”按钮
        const updateButton = node.addWidget("button", "Update Inputs", null, () => {
            // 点击按钮时，重新计算节点的大小并重新绘制
            // ComfyUI 会在下次执行时，根据新的 inputcount 重新调用 INPUT_TYPES
            node.setSize([node.size[0], node.computeSize()[1]]);
            app.graph.setDirtyCanvas(true);
        });

        // 将按钮放在 inputcount 下面
        updateButton.serialize = false; // 按钮状态不需要保存
    },
});
