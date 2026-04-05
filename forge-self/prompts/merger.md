# 增量合并 (Merger)

当用户想要更新已有替身时，使用此流程进行增量合并。

## 触发条件

- 用户明确说"更新替身"
- 用户提供了新的素材
- 用户经历了重大变化想要反映到替身中

## 合并原则

1. **新数据不自动覆盖旧数据**：新信息作为候选项，需要与旧数据对比后决定
2. **标注时间戳**：每次合并记录时间，方便追踪变化轨迹
3. **保留历史版本**：合并前先用 `version_manager.py` 存档

## 合并流程

### Step 1: 加载现有人格底座
```
读取 standins/{name}/persona.md
解析五层结构
```

### Step 2: 分析新数据
```
如果是对话：提取新的观点、态度变化
如果是素材：走 self_analyzer.md 流程
输出：新数据提取结果
```

### Step 3: 差异对比
```
逐层对比新旧数据：

【无变化】：保持原样
【新增】：标记为 [新增-待确认]
【冲突】：
  - 如果新数据与L5纠正层一致 → 保留新数据
  - 如果新数据与L0硬性覆写冲突 → 需要用户确认
  - 其他冲突 → 列出供用户选择
【参数变化】：如果决策偏好参数变动超过2分 → 标记为显著变化，需确认
```

### Step 4: 用户确认
```
向用户展示所有变化：

你的替身有以下更新：

【确认更新】
- [已自动应用的无争议更新]

【需要你确认的】
- 之前你的风险偏好是 4/10，但最近的表现更像 7/10。
  你觉得是你变了，还是那只是特定情况下的表现？

【新发现】
- [全新的特征，之前没有采集到]
  要加进去吗？
```

### Step 5: 应用合并 + 生成 diff

```python
from tools.version_manager import archive_before_update, generate_diff, save_changelog_entry

# 存档当前版本
archive_before_update(name, persona_type)

# 将用户确认的更新写入 persona.json
# old_data = 更新前的数据，new_data = 更新后的数据
# ...

# 生成字段级 diff 并写入 changelog
changes = generate_diff(old_data, new_data)
if changes:
    save_changelog_entry(
        name=name,
        persona_type=persona_type,
        changes=changes,
        reason="增量合并：" + source_description,  # 如"新增微信聊天记录"
        user_words="",
    )

# 更新 meta.last_updated 和 meta.version
```

向用户展示变更摘要：
```
合并完成。

本次更新了 {N} 个字段：
- L3.risk_appetite.score: 4 → 6（来源：新导入的微信记录）
- L2.signature_phrases: 新增"就这样"
- ...

变更已记录到 history/changelog.json，可随时查看或按字段回滚。
```
