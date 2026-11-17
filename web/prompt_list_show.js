import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "PromptList.ShowText",
    async beforeRegisterNodeDef(nodeType, nodeData, app) { // 节点注册事件
        // 只对 PromptList_Show 节点生效
        if (nodeData.name !== "PromptList Show") return;
        // console.log('debug init prompt_list_show 事件', nodeData.name)

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
