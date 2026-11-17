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


// ------------ PromptList Create：按 inputcount 增删文本输入框 ------------

// [warning] PromptList_Create 节点的动态输入比较复杂，部分 vibe coding 的代码我也没弄懂

const CREATE_NODE = "PromptList Create";
const COUNT_WIDGET = "inputcount";
const TEXT_PREFIX = "text_";
const UPDATE_BUTTON = "Update Inputs";
const MAX_TEXT_INPUTS = 100;  // 与 Python 端 inputcount 的 max 保持一致

const textInputName = (index) => `${TEXT_PREFIX}${index}`;

const textInputIndex = (name) => {
    if (typeof name !== "string" || !name.startsWith(TEXT_PREFIX)) return 0;
    const index = Number(name.slice(TEXT_PREFIX.length));
    return Number.isInteger(index) && index > 0 ? index : 0;
};

const getTextWidget = (node, index) =>
    node.widgets?.find((w) => w.name === textInputName(index));

const clampCount = (value) => {
    const count = Math.round(Number(value)) || 1;
    return Math.min(MAX_TEXT_INPUTS, Math.max(1, count));
};

function ensureTextInput(node, index) {
    const name = textInputName(index);
    let changed = false;
    if (!getTextWidget(node, index)) {
        const { widget } = ComfyWidgets["STRING"](node, name, ["STRING", { multiline: true, default: "" }], app);
        widget.tooltip = `第 ${index} 项提示词内容`;
        changed = true;
    }
    // 加载工作流时端口已经按保存的内容建好了，这里只补上和文本框的关联
    const input = node.inputs?.find((slot) => slot.name === name);
    if (input) {
        input.widget = { name };
        return changed;
    }
    // 和 INPUT_TYPES 里声明的 text_1/text_2 一样，同时有输入端口和文本框
    node.addInput(name, "STRING", { widget: { name } });
    return true;
}

function removeTextInput(node, index) {
    const name = textInputName(index);
    const widget = getTextWidget(node, index);
    if (widget) node.removeWidget(widget);
    for (let slot = (node.inputs?.length ?? 0) - 1; slot >= 0; slot--) {
        if (node.inputs[slot].name === name) node.removeInput(slot);
    }
}

// 让 text_1..text_count 和 inputcount 一一对应；savedValue 用于恢复加载工作流时保存的内容。
function syncTextInputs(node, count, savedValue) {
    const limit = clampCount(count);
    const highest = Math.max(
        0,
        ...(node.widgets ?? []).map((widget) => textInputIndex(widget.name)),
        ...(node.inputs ?? []).map((input) => textInputIndex(input.name)),
    );
    let changed = false;

    for (let index = highest; index > limit; index--) {
        removeTextInput(node, index);
        changed = true;
    }
    for (let index = 1; index <= limit; index++) {
        changed = ensureTextInput(node, index) || changed;
    }

    if (savedValue) {
        for (let index = 1; index <= limit; index++) {
            const widget = getTextWidget(node, index);
            const value = savedValue(index);
            if (widget && typeof value === "string" && widget.value !== value) widget.value = value;
        }
    }

    const countWidget = node.widgets?.find((w) => w.name === COUNT_WIDGET);
    if (countWidget && countWidget.value !== limit) {
        countWidget.value = limit;
        changed = true;
    }

    // 只有输入框增减时才改变节点高度，避免覆盖用户手动拖出来的尺寸
    if (changed) node.setSize([node.size[0], node.computeSize()[1]]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "PromptList.CreateDynamicInputs",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        // 只对 PromptList Create 节点生效
        if (nodeData.name !== CREATE_NODE) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const node = this;
            const r = onNodeCreated?.apply(node, arguments);

            const countWidget = node.widgets?.find((w) => w.name === COUNT_WIDGET);
            if (!countWidget) return r;

            const updateButton = node.addWidget("button", UPDATE_BUTTON, null, () => {
                syncTextInputs(node, countWidget.value);
            });
            updateButton.serialize = false;          // 不写进工作流
            updateButton.options.serialize = false;  // 不写进 API 格式

            // 按钮紧贴在 inputcount 下面；之后新增的 text_N 会排在按钮之后
            const widgets = node.widgets;
            widgets.splice(widgets.indexOf(updateButton), 1);
            widgets.splice(widgets.indexOf(countWidget) + 1, 0, updateButton);

            // API 格式的工作流不走 onConfigure，改 inputcount 只会触发回调，这里补上同步
            const countChanged = countWidget.callback;
            countWidget.callback = function (value, canvas) {
                const result = countChanged?.apply(this, arguments);
                if (!canvas) syncTextInputs(node, value);
                return result;
            };

            return r;
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (serialisedNode) {
            const r = onConfigure?.apply(this, arguments);

            // widget 值按顺序保存：inputcount 是第 0 个，text_N 是第 N 个
            const named = serialisedNode?.widgets_values_named;
            const positional = serialisedNode?.widgets_values;
            const savedValue = (index) =>
                named?.[textInputName(index)] ?? (Array.isArray(positional) ? positional[index] : undefined);

            const count = this.widgets?.find((w) => w.name === COUNT_WIDGET)?.value;
            syncTextInputs(this, count, savedValue);

            return r;
        };
    },
});
