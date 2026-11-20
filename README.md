# Prompt List

English | [简体中文](./README.zh.md)

A ComfyUI custom node pack for handling a **prompt list**. Under the hood it is a plain Python `list[str]`, and it travels through the graph as *one value*: build it once, edit it in place, read single items out of it by index, and flatten it back into one prompt line at the end.

## What a list is good for

The length of the list and the meaning of the indices are determined by you. Here are the two common usage scenarios that the author frequently employs:

**Slots.** Give each index a job, and let every stage of the workflow fill in or swap only the slots it cares about:

| Index | Slot |
| --- | --- |
| 0 | character / head |
| 1 | outfit |
| 2 | expression |
| 3 | action |
| 4 | camera |
| 5 | scene |

You can customize them as you wish, for example by making more detailed divisions: shirts, jackets, pants, socks, shoes (similar to the Kisekae plugin, but with stronger and more flexible customization capabilities. You don't have to pay attention to those categories that you don't use)

A character is described once, then "change the outfit" or "change the camera" becomes an extra stage that edits one or two slots — nothing gets re-typed, and any stage can be muted to see its effect. The [demo workflow](./examples/prompt-list-demo.json) is built this way.

**A prompt bank.** The index is just "which variant I want": type a set of prompts once, keep them on the canvas, and let `Get Item` hand one of them to the text encoder.

## Two kinds of "list" in ComfyUI

ComfyUI already has list execution, where an input list makes downstream nodes run once per item. This pack does something else entirely, and mixing the two up is the usual source of confusion:

| | ComfyUI list execution | `STRING_PYLIST` (this pack) |
| --- | --- | --- |
| What travels on the wire | one item per run | the whole array, one value |
| Downstream nodes run | once per item | once |
| Socket type | the item type (`STRING`, `IMAGE`, …) | `STRING_PYLIST` |
| Good for | generating N variants of one graph | composing one prompt out of slots, or keeping a prompt bank |

`STRING_PYLIST` is a socket type defined by this pack, so it only connects to nodes from this pack. The value inside is a plain `list[str]`.

## Installation

1. Install [ComfyUI](https://docs.comfy.org/get_started).
2. Recommended: install [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager) and search for this extension there.
3. Manual alternative — clone the repository into `ComfyUI/custom_nodes`:

   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/LincZero/comfyui-prompt-list.git
   ```

4. Restart ComfyUI.

All nodes are registered under the **Prompt List** category.

## What you can do with it

| Goal | Node |
| --- | --- |
| Create a list | one of the five create nodes — see below |
| Read one item | `PromptList GetItem` |
| Read the whole list | `PromptList Show` (JSON preview) |
| Edit many items at once | a create node with `prompt_list` connected (template syntax) |
| Edit a single item | `PromptList SetItem` |
| Flatten back into one string | `PromptList JoinToString` — or the `joined_text` output the create nodes already have |

## Nodes

### Create From Upstream (Auto) — `PromptList CreateFromUpstream`

Collects whatever strings are wired into it into one list. Each connected input becomes one item, in port order.

- Ports grow and shrink the usual way: connect the last one and another appears, disconnect it and it goes away (1–100).
- Values are stripped of surrounding whitespace.
- A connected but empty input is kept as an empty item, not skipped.
- Connect the single `prompt_list` input and these same strings become templates for that list instead — see *Editing with templates* below.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | Optional single socket. Connected = the strings below are templates for that list |
| `text0`, `text1`, … | `STRING` | Multiline, auto-growing ports, 1–100 |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | One item per connected port |
| `joined_text` | `STRING` | Those items joined with a fixed `,` (no space), ready for a text encoder |

For stacking several lists in one go, see `Create From Lists (Chain)` below.

### Create From Lists (Chain) — `PromptList CreateFromLists`

Lays several lists on top of each other as a pipeline: the first list (or the `prompt_list` you wire in) sets the items, and every following list is one layer of templates applied in port order. This is the "parallel → series" node — keep each layer in its own parallel branch, then stack them here with a single node.

- Ports grow and shrink like the auto-grow node above (1–100).
- One layer = one list: position *n* of the layer edits item *n* of the result, so `{{item}}` keeps that value and plain text overwrites it.
- A layer shorter than the result leaves the remaining items alone; a longer one appends its extra non-empty items.
- A port carrying an empty list changes nothing.
- Outputs are the same two as the other create nodes: the list itself, and its `,`-joined text.

With `["111", "222"]` and `["{{item}}", "333"]` wired in, the result is `["111", "333"]`: the first list builds, the second keeps item 0 and replaces item 1.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | Optional single socket. Connected = start from this list instead of the first input |
| `list0`, `list1`, … | `STRING_PYLIST` | Auto-growing ports, 1–100. Port order is also the layer order |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | The result after all layers |
| `joined_text` | `STRING` | That list joined with a fixed `,` (no space), ready for a text encoder |

### Create From Strings — `PromptList CreateFromStrings`

One single-line box per item. With nothing connected it creates a list; with `prompt_list` connected the same boxes act as templates that edit that list item by item.

The number of boxes comes from the `inputcount` widget (1–100, default 2). Change it, then click **Update Inputs** on the node to rebuild the ports; loading a workflow rebuilds them automatically.

Every box defaults to `{{item}}`, which means "leave this item alone". Each box can also be driven by an upstream `STRING` instead of being typed into.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `inputcount` | `INT` | 1–100, default 2. How many boxes |
| `text_0` … `text_N-1` | `STRING` | One box per item, default `{{item}}` |
| `prompt_list` | `STRING_PYLIST` | Optional. Connected = edit that list, empty = create |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | The new or edited list |
| `joined_text` | `STRING` | That list joined with a fixed `,` (no space), ready for a text encoder |

Both outputs come from the same list, so `joined_text` is exactly `",".join(prompt_list)` — an empty slot therefore shows up as a doubled comma.

### Create From Strings (Multi) — `PromptList CreateFromStringsMulti`

Same node with multiline boxes and the same two outputs, for slots whose content is a paragraph rather than a phrase.

### Create From String — `PromptList CreateFromString`

Splits one multiline text box into items, one per line.

- Blank lines are kept as empty items, so line *n* always maps to item *n*.
- Each line is stripped.
- An empty text box creates an empty list.
- With `prompt_list` connected, each line is a template — so one text box can edit many items at once.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `text` | `STRING` | Multiline, default empty. One item per line |
| `prompt_list` | `STRING_PYLIST` | Optional. Connected = edit that list, empty = create |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | The new or edited list |
| `joined_text` | `STRING` | That list joined with a fixed `,` (no space), ready for a text encoder |

### Show — `PromptList Show`

An output node that renders the list as indented JSON in a read-only box on the node, and passes the list through unchanged so it can sit anywhere in the chain. Non-ASCII text is shown as-is.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | Required |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | The same list, unchanged |

### Get Item — `PromptList GetItem`

Reads one item. The index is 0-based. An index outside `0 … length-1` stops the run with an error that reports both the index and the list length; it never clamps or wraps.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | Required |
| `index` | `INT` | 0–9999, default 0. Can be driven by an upstream `INT` |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `string` | `STRING` | The selected item |

### Set Item — `PromptList SetItem`

Replaces one item and outputs the edited list. The index must already exist: this node replaces, it never appends.

It is the single-slot tool — "same list, but the camera is different now" — as opposed to a create node, which edits many slots from one row of boxes.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | Required |
| `index` | `INT` | 0–9999, default 0. Must be within the list |
| `new_value` | `STRING` | Multiline replacement text |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | A copy with one item replaced |

### Join To String — `PromptList JoinToString`

Flattens the list into one string, in list order, with a separator (default `", "`). Items are joined exactly as stored — including empty ones, which leave a doubled separator behind.

Every create node already returns a `joined_text` output that joins with a fixed `,`, so this node is only needed when you want another separator, or when the list was edited after it was created.

**Inputs**

| Name | Type | Notes |
| --- | --- | --- |
| `prompt_list` | `STRING_PYLIST` | Required |
| `separator` | `STRING` | Single-line, default `", "` |

**Output**

| Name | Type | Notes |
| --- | --- | --- |
| `joined_text` | `STRING` | All items in one string |

## Editing with templates

All five create nodes share one rule set. Only where the inputs come from differs — text boxes (`Create From Strings` and its `(Multi)` twin), the lines of one text box (`Create From String`), the connected strings (`Create From Upstream`), or each connected list applied as one layer (`Create From Lists`) — and merging works exactly the same. Without an upstream list every input simply becomes an item; with an upstream list each input is a template for the item at the same index:

```text
result = list(prompt_list)                 # empty when nothing is connected
for index, template in enumerate(boxes):
    if index < len(result):
        # {{item}} → the item's current text; no {{item}} at all → overwrite the item
        result[index] = template.replace("{{item}}", result[index])
    else:
        # a box beyond the list length appends a new item, unless it is empty
        extra = template.replace("{{item}}", "")
        if extra.strip():
            result.append(extra)
# items the boxes do not reach are left untouched
```

So the whole "追加 / 替换 / 清空" vocabulary is just what you write in the input:

| You want | Type this | Effect |
| --- | --- | --- |
| keep the slot | `{{item}}` | untouched (this is the default value) |
| append | `{{item}}, best quality` | text added after the item |
| prepend | `masterpiece, {{item}}` | text added before the item |
| replace | `silver hair` | item overwritten |
| clear | *(empty box)* | item becomes an empty string |
| leave the rest alone | write fewer inputs | untouched items keep their value |

Text inputs — boxes, lines and connected strings — are stripped before merging, so spaces at their edges are dropped; put the spacing after the placeholder if you need it. Items that arrive through `Create From Lists` are used verbatim. An input may contain `{{item}}` more than once; every occurrence is replaced.

Some concrete results:

| Upstream list | Inputs | Result |
| --- | --- | --- |
| `["one", "two", "three"]` | `{{item}}` in every box | unchanged |
| `["one", "two"]` | `{{item}}, masterpiece`, `best quality, {{item}}` | `["one, masterpiece", "best quality, two"]` |
| `["one", "two"]` | `red`, *(empty)* | `["red", ""]` |
| `["one", "two", "three"]` | `A` | `["A", "two", "three"]` |
| `["one"]` | `a`, `b`, *(empty)* | `["a", "b"]` |
| none | `{{item}}`, `{{item}}` | `["", ""]` |
| none | `cat`, `dog` | `["cat", "dog"]` |

## Walkthrough: a character in slots

This is the "wardrobe" chain from the demo workflow. Six slots, five stages, each stage one node.

### Stage 0 — skeleton of comments

A `Create From Strings (Multi)` with six boxes. Every box is just a comment naming what the slot is for:

```text
box 0  一个小技巧是，你可以在初始节点之前放一个纯注释节点来解释每一项。
       反正后面会被覆盖掉。
box 1  注释-服装
box 2  注释-表情
box 3  注释-动作（我们这里假设初始不写动作，后面有需要了再补充）
box 4  注释-镜头
box 5  注释-场景
```

Nothing here survives — and that is the point. The canvas now documents its own layout: anyone reading the graph can see that index 3 is the action slot, even though it is empty.

### Stage 1 — base settings

Another `Create From Strings (Multi)`, six plain boxes, `prompt_list` fed from stage 0. Plain text overwrites, so the whole skeleton is replaced in one go:

```text
box 0  这是角色的头
box 1  角色的服装
box 2  角色的表情
box 3  (empty)          ← the action slot is deliberately left empty
box 4  镜头
box 5  场景
```

```text
list → ["这是角色的头", "角色的服装", "角色的表情", "", "镜头", "场景"]
```

### Stage 2 — new outfit, new camera

Now only the slots that change get a box, and the list has six items while the node has five boxes:

```text
keep       box 0  {{item}}
append     box 1  {{item}}, 服装的基础上新增一些小细节, 或新增墨镜和帽子啥的
overwrite  box 2  把原来的表情删掉更换成表情2
keep       box 3  {{item}}                    ← the action slot stays empty
overwrite  box 4  镜头B
keep       no box for slot 5                 ← 场景 survives untouched
```

```text
list → ["这是角色的头",
        "角色的服装, 服装的基础上新增一些小细节, 或新增墨镜和帽子啥的",
        "把原来的表情删掉更换成表情2",
        "",
        "镜头B",
        "场景"]
```

Two different ways of saying "don't touch this" — `{{item}}` for a slot you kept a box for, and simply not writing the box at all — and they matter here: five boxes, six items.

### Stage 3 — one slot, without a row of boxes

`Set Item`, index `4`, value `再更换为镜头C`. The camera slot changes; nothing else is touched.

```text
list → ["这是角色的头",
        "角色的服装, 服装的基础上新增一些小细节, 或新增墨镜和帽子啥的",
        "把原来的表情删掉更换成表情2",
        "",
        "再更换为镜头C",
        "场景"]
```

### Stage 4 — flatten

`Join To String` with the default `", "` separator:

```text
这是角色的头, 角色的服装, 服装的基础上新增一些小细节, 或新增墨镜和帽子啥的, 把原来的表情删掉更换成表情2, , 再更换为镜头C, 场景
```

Which is ready for a text encoder. Note the `, ,` in the middle: the action slot is empty, and `Join To String` joins items exactly as they are without skipping empties.

The join comes last on purpose — `Set Item` outputs a list too, and a create node's own `joined_text` only reflects that node's output, not later edits.

### What this buys you

- **One stage per idea.** "Base character", "new outfit", "different camera" are separate nodes, so each can be muted, bypassed or duplicated without re-typing anything.
- **Only the changing slots get written.** `{{item}}` and a missing box both mean "leave it", so a stage is as small as it needs to be.
- **Bulk and single both available.** A create node with `prompt_list` edits many slots from one row of boxes; `Set Item` edits exactly one.
- **The list is inspectable.** Drop a `PromptList Show` anywhere to see the JSON, and put a core `Preview Any` on the joined text.

## The demo workflow

[`examples/prompt-list-demo.json`](./examples/prompt-list-demo.json) is one canvas covering everything above. Drag the file onto the ComfyUI canvas, or use *Workflow → Open*.

It is laid out in four framed areas, top to bottom:

| Area | Shows | What you should see |
| --- | --- | --- |
| Node basics | `Create From String` with `1`–`5` one per line, then `Show`, `Get Item`, `Set Item`, `Join To String` | `Show` renders `["1","2","3","4","5"]`; `Get Item` index 1 gives `2`; `Set Item` index 1 → `22222` gives `["1","22222","3","4","5"]`; `Join To String` (fed from the create node) gives `1, 2, 3, 4, 5` |
| Create nodes | four ways of creating a list | `Create From Strings` with `666 / 555 / 666` → `["666","555","666"]`; the `(Multi)` node next to it holds two empty multiline boxes (its output is not wired); `Create From Upstream` fed by two `Primitive String` nodes (`aaa`, `bbb`) → `["aaa","bbb"]` |
| Slots / wardrobe | the walkthrough above | the lists shown in the walkthrough |
| KJNodes comparison | a development note; it uses `Join String Multi` from [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes) | — (needs KJNodes installed; delete this area if you don't have it) |

Everything except the last area runs on core ComfyUI plus this pack.

## Related nodes

- **`Join String Multi`** (KJNodes) collects several `STRING` inputs into one string. It solves the input side; this pack's `Join To String` solves the value side — the list it joins may have been edited by any number of nodes in between. Its implementation was a useful reference while building this one.
- **`Preview Any`** and **`Primitive String`** (core) are handy companions: the former to look at a single output, the latter to feed strings into `Create From Upstream`.
- Development idea reference: KJNodes (Join String Multi), ComfyUI-List-Utils, Kisekae

## Limits and notes

- Up to 100 boxes or inputs per node, and an index up to 9999. Those limits belong to the widgets; `Show`, `Get Item`, `Set Item` and `Join To String` handle lists of any length.
- Only strings live inside the list.
- There is no "delete item" node yet — shorten a list by rebuilding it, or empty the slot you no longer need and accept the doubled separator.
- An empty item joins as an empty slot, so a list like `["a", "", "b"]` becomes `a, , b` from `Join To String`, or `a,,b` from a create node's `joined_text`.
- The list is one value, so it does not trigger per-item execution. To run a graph N times, drive an index from a counter or use ComfyUI's own list nodes.
- Node descriptions and tooltips inside the pack are currently written in Chinese only.
