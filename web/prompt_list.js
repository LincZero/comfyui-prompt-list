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


// ------------ 按 inputcount 增删文本输入框（CreateFromStrings 单行 / 多行） ------------

// [warning] PromptList_CreateFromStrings 节点的动态输入比较复杂，部分 vibe coding 的代码我也没弄懂

// 单行 / 多行两个版本共用同一套逻辑，只有文本框的 multiline 不同；
// 输入框默认内容 {{item}} = 保留原值（不接上游列表时它就是空字符串）
const CREATE_NODES = {
    "PromptList CreateFromStrings": { multiline: false, default: "{{item}}" },
    "PromptList CreateFromStringsMulti": { multiline: true, default: "{{item}}" },
};
const COUNT_WIDGET = "inputcount";
const TEXT_PREFIX = "text_";
const UPDATE_BUTTON = "Update Inputs";
const MAX_TEXT_INPUTS = 100;  // 与 Python 端 inputcount 的 max 保持一致

const textInputName = (index) => `${TEXT_PREFIX}${index}`;

// 输入框下标从 0 开始（text_0、text_1…），和 GetItem / SetItem 的 index 对应；不是输入框时返回 -1
const textInputIndex = (name) => {
    if (typeof name !== "string" || !name.startsWith(TEXT_PREFIX)) return -1;
    const suffix = name.slice(TEXT_PREFIX.length);
    return /^\d+$/.test(suffix) ? Number(suffix) : -1;
};

const getTextWidget = (node, index) =>
    node.widgets?.find((w) => w.name === textInputName(index));

const clampCount = (value) => {
    const count = Math.round(Number(value)) || 1;
    return Math.min(MAX_TEXT_INPUTS, Math.max(1, count));
};

function ensureTextInput(node, index, config) {
    const name = textInputName(index);
    let changed = false;
    if (!getTextWidget(node, index)) {
        const options = { multiline: config.multiline, default: config.default };
        const { widget } = ComfyWidgets["STRING"](node, name, ["STRING", options], app);
        widget.tooltip = `第 ${index + 1} 项提示词内容（index ${index}）`;
        changed = true;
    }
    // 加载工作流时端口已经按保存的内容建好了，这里只补上和文本框的关联
    const input = node.inputs?.find((slot) => slot.name === name);
    if (input) {
        input.widget = { name };
        return changed;
    }
    // 和 INPUT_TYPES 里声明的 text_0/text_1 一样，同时有输入端口和文本框
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

// 让 text_0..text_{count-1} 和 inputcount 一一对应；savedValue 用于恢复加载工作流时保存的内容。
function syncTextInputs(node, count, config, savedValue) {
    const limit = clampCount(count);
    const highest = Math.max(
        -1,
        ...(node.widgets ?? []).map((widget) => textInputIndex(widget.name)),
        ...(node.inputs ?? []).map((input) => textInputIndex(input.name)),
    );
    let changed = false;

    for (let index = highest; index >= limit; index--) {
        removeTextInput(node, index);
        changed = true;
    }
    for (let index = 0; index < limit; index++) {
        changed = ensureTextInput(node, index, config) || changed;
    }

    if (savedValue) {
        for (let index = 0; index < limit; index++) {
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
        const config = CREATE_NODES[nodeData.name];
        if (!config) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const node = this;
            const r = onNodeCreated?.apply(node, arguments);

            const countWidget = node.widgets?.find((w) => w.name === COUNT_WIDGET);
            if (!countWidget) return r;

            const updateButton = node.addWidget("button", UPDATE_BUTTON, null, () => {
                syncTextInputs(node, countWidget.value, config);
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
                if (!canvas) syncTextInputs(node, value, config);
                return result;
            };

            return r;
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (serialisedNode) {
            const r = onConfigure?.apply(this, arguments);

            // widget 值按顺序保存、跳过不序列化的（按钮），所以先算出 text_0 前面有几个可保存的 widget
            const before = this.widgets.slice(0, this.widgets.indexOf(getTextWidget(this, 0)));
            const offset = before.filter((widget) => widget.serialize !== false).length;

            const named = serialisedNode?.widgets_values_named;
            const positional = serialisedNode?.widgets_values;
            const savedValue = (index) =>
                named?.[textInputName(index)] ??
                (Array.isArray(positional) ? positional[offset + index] : undefined);

            const count = this.widgets?.find((w) => w.name === COUNT_WIDGET)?.value;
            syncTextInputs(this, count, config, savedValue);

            return r;
        };
    },
});
