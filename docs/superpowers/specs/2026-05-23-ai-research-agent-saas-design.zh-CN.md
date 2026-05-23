# AI Research Agent Platform 设计说明（中文版）

## 1. 项目定位

`ai-research-agent-saas` 不再定义为一个简单的“自动生成研究报告”的 Web SaaS，而是升级为一个 `监督式多 Agent 研究平台`。

它面向的不是普通聊天式 AI 产品，而是以下两类需求：

- 需要把公司研究、竞品研究、市场扫描流程自动化的中小企业
- 需要可验证、可追溯、可扩展的 Agent 研究系统的 AI 初创团队

这个项目在 GitHub 和 Upwork 上的核心卖点应该是：

`我能构建一个带监督、带批判审查、带证据链追踪的多 Agent 研究系统，而不是一个套壳聊天机器人。`

## 2. 设计目标

这个项目需要同时满足三个目标：

- 作为产品展示，它要看起来像一个可交付的成品
- 作为工程展示，它要体现多 Agent 编排、状态管理、容错与可观测性
- 作为 Agent 展示，它要证明系统不是单次模型调用，而是带结构化控制和证据验证的研究工作流

## 3. 升级后的产品定义

该系统的工作方式不是：

- 用户提问
- 系统搜索
- 系统生成一篇报告

而是：

1. 用户提交研究任务
2. `supervisor` 定义当前研究轮次目标
3. `planner` 将大问题拆成多个可执行 briefs
4. 多个 `researcher` 并行研究不同 briefs
5. `critic` 审查每个 brief 的研究结果是否证据充分
6. `supervisor` 决定结束、返工、补查或进入下一轮
7. `synthesizer` 仅基于通过审查的发现生成最终报告

这意味着系统本质上是一个 `supervised, schema-driven, evidence-grounded multi-agent platform`。

## 4. 非目标范围

为了避免范围失控，第一阶段明确不做以下内容：

- 多租户与账号体系
- 支付、计费、订阅
- 团队协作与评论系统
- 自主浏览器代理无限探索
- 登录保护网站的数据抓取
- 多模型动态路由平台
- 实时通知系统
- 长期用户记忆系统
- 生成 PPT、PDF 等完整交付物
- 图数据库接入

## 5. 目标用户

### 主要用户

- 需要自动完成公司调研、市场扫描、竞品研究的企业用户
- 需要展示 Agent 能力、评估 Agent 研究流程、验证架构可行性的 AI 初创团队

### 次要用户

- 在 Upwork 上寻找定制 Agent 系统、研究自动化工具、RAG/Research 产品的客户

## 6. 用户价值

这个系统需要回答的不是“能不能生成一篇报告”，而是：

- 能不能把一个复杂研究任务拆成多个可执行子问题
- 能不能并行研究并保留中间过程
- 能不能对研究结论做证据级验证
- 能不能清晰展示为什么得出这个结论

最终价值在于：把高价值研究工作从“黑盒摘要”升级成“可监督、可追溯、可解释的 Agent 研究流程”。

## 7. 升级后的 MVP 定义

升级后的 MVP 不再是轻量型线性工作流，而是一个 `高阶但可落地的监督式多 Agent MVP`。

### MVP 必须包含

- Web 控制台，可提交研究任务、查看过程、查看报告
- `supervisor` 驱动的多轮研究机制
- `planner` 生成 briefs
- `researcher` 池并行执行 brief
- `critic` 对 brief 结果进行审查
- 证据级持久化，包括 finding、claim、source fragment
- 最终报告仅消费已通过审查的发现
- 任务追踪界面，能看到轮次、brief、证据和 verdict
- token、成本、重试、失败信息等执行元数据

### MVP 不包含

- 用户登录
- 支付
- 外部消息通知
- 私有数据连接器
- 图数据库
- 高级权限系统
- 复杂前端协作功能

## 8. 产品体验

### 8.1 提交任务

用户输入：

- 研究主题或公司名称
- 可选上下文
- 报告类型
- 可选限制条件，例如时间范围、关注维度、预算上限

系统创建一个 `research task`，进入研究编排流程。

### 8.2 追踪执行过程

用户可以在任务详情页看到：

- 当前任务状态
- 当前轮次
- 每轮包含的 briefs
- 每个 brief 的负责人角色和状态
- 当前是否进入 critic 审查
- 是否需要返工或补查
- token 与成本使用情况

### 8.3 查看证据与结论

用户可以查看：

- 某个 finding 来源于哪些网页片段
- 哪些结论被 critic 接受
- 哪些结论被 critic 拒绝
- 哪些问题仍存在证据缺口

### 8.4 查看最终报告

最终报告只展示：

- 被接受的结论
- 对应引用来源
- 风险提示
- 未知项和待进一步确认的问题

## 9. 核心架构

系统建议拆成 8 个核心模块。

### 9.1 Web Console

职责：

- 提供任务创建、任务详情、round/brief 看板、证据浏览器、最终报告视图
- 用产品化界面展示 Agent 执行过程

建议实现：

- `FastAPI`
- `Jinja2`
- `HTMX`

这样能快速做出可演示产品，同时不引入过重前端工程成本。

### 9.2 API Layer

职责：

- 创建任务
- 查询任务状态
- 查询 round 与 brief
- 查询证据链
- 查询最终报告

建议接口：

- `POST /api/tasks`
- `GET /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/rounds`
- `GET /api/tasks/{task_id}/evidence`
- `GET /api/tasks/{task_id}/report`

### 9.3 Orchestrator

职责：

- 驱动整个多 Agent 状态机
- 管理轮次推进
- 调度 supervisor、planner、researcher、critic、synthesizer
- 控制最大轮次、并行数、返工次数

这一层是整个系统的核心，不应写成“顺手拼起来的 if-else 脚本”，而应明确建模为工作流状态机。

### 9.4 Agent Runtime

职责：

- 定义各类 agent 的统一输入输出 schema
- 管理 agent 调用上下文
- 执行结构化输出校验

### 9.5 Tooling Layer

职责：

- 给 researcher 提供发现和抽取工具
- 给 critic 提供验证和覆盖率检查工具
- 给 supervisor 和 planner 提供控制与依赖分析工具

### 9.6 Research Memory

职责：

- 维护任务级、brief 级、来源级的共享记忆
- 避免重复研究
- 支持多轮研究的上下文继承

### 9.7 Evidence Graph Persistence

职责：

- 存储 finding、claim、source fragment、gap 之间的关系
- 支持结论到证据的追溯

### 9.8 Worker Runtime

职责：

- 异步执行研究任务
- 支持并行 brief
- 支持失败重试

建议实现：

- `Redis`
- `Celery` 或 `Dramatiq`

## 10. Agent 拓扑

该系统采用 `监督者型多 Agent` 架构。

### 10.1 Supervisor

职责：

- 定义当前轮次研究目标
- 审批 planner 的拆分结果
- 基于 critic 的审查结果做出继续、返工、扩展或结束决策

它不直接研究事实，而是负责控制系统方向。

### 10.2 Planner

职责：

- 将大问题拆成多个可执行 briefs
- 为每个 brief 指定研究目标、搜索方向、证据目标和优先级

它的重点不是输出自然语言计划，而是输出结构化的 brief 集合。

### 10.3 Researcher

职责：

- 围绕单个 brief 进行搜索、抽取和整理
- 产出“带证据的发现”

它不能直接决定最终结论，也不能绕过 critic。

### 10.4 Critic

职责：

- 审查 researcher 的发现是否有足够证据支撑
- 检查来源是否过旧、单一、冲突或信息不足
- 给出 `accept / revise / expand` verdict

它是整个系统可信度的关键角色。

### 10.5 Synthesizer

职责：

- 只基于被接受的 findings 生成最终报告
- 不得补充未验证的事实
- 对风险和未知项做明确标记

## 11. Agent 输入输出 Schema

所有 agent 必须采用结构化输入输出，避免自由文本协作失控。

### 11.1 Supervisor 输出

- `round_goal`
- `selected_briefs`
- `decision`
- `decision_reason`
- `next_action`

### 11.2 Planner 输出

- `brief_id`
- `question`
- `search_queries`
- `evidence_targets`
- `priority`
- `dependencies`

### 11.3 Researcher 输出

- `brief_id`
- `findings`
- `citations`
- `open_questions`
- `confidence`
- `raw_notes`

要求：

- 每条 finding 必须关联 source id 或 fragment id

### 11.4 Critic 输出

- `verdict`
- `accepted_findings`
- `rejected_findings`
- `gaps`
- `requested_followups`
- `quality_score`

其中 `verdict` 只允许：

- `accept`
- `revise`
- `expand`

### 11.5 Synthesizer 输出

- `section_outputs`
- `key_takeaways`
- `risk_flags`
- `citation_index`

## 12. 任务状态机

系统必须显式建模任务状态，而不是依赖隐式控制流。

### 12.1 任务级状态

- `queued`
- `running`
- `waiting_for_retry`
- `completed`
- `completed_with_warnings`
- `failed`

### 12.2 轮次级状态

- `round_created`
- `planning`
- `researching`
- `critic_review`
- `supervisor_decision`
- `round_closed`

### 12.3 Brief 级状态

- `pending`
- `in_progress`
- `submitted`
- `accepted`
- `revise_requested`
- `expand_requested`
- `failed`

## 13. 轮次控制规则

为了让系统高阶但可控，第一版必须限制复杂度。

建议约束：

- 最多 `3` 轮 supervisor 循环
- 每轮最多 `5` 个 briefs
- 每个 brief 最多 `2` 次 revise
- 超出预算、超出轮次或证据覆盖率长期不足时，允许任务以 `completed_with_warnings` 结束

这样既能展示高阶 Agent 编排，又不会变成不可维护的自治系统。

## 14. Research Memory 设计

### 14.1 Task Memory

保存：

- 原始任务目标
- 模板类型
- 轮次摘要
- 全局限制条件
- 预算信息

### 14.2 Brief Memory

保存：

- brief 定义
- 当前状态
- 已接受发现
- 被拒绝发现
- gaps
- 待补查问题

### 14.3 Source Memory

保存：

- 来源 URL
- 标题
- 发布时间
- 域名
- 抽取片段
- 抓取状态
- 可信度标签

## 15. 证据图模型

这是项目升级后的关键设计，不应只保存普通日志。

系统需要把“结论”和“证据”存成关系结构。

### 15.1 关键节点

- `task`
- `round`
- `brief`
- `finding`
- `claim`
- `source`
- `source_fragment`
- `gap`

### 15.2 关键关系

- `task -> round`
- `round -> brief`
- `brief -> finding`
- `finding -> source_fragment`
- `claim -> source_fragment`
- `critic -> gap`
- `gap -> followup_brief`

### 15.3 设计价值

这层设计的好处：

- critic 可以判断某条 finding 是否只有单一来源支撑
- supervisor 可以知道哪些 brief 仍然缺证据
- synthesizer 可以只消费通过审核的 finding
- UI 可以展示“这条结论来自哪些证据片段”

第一版不需要上图数据库，建议先用 `Postgres` 的关系模型实现。

## 16. 数据模型建议

初始版本建议至少包含以下表：

- `research_tasks`
- `research_rounds`
- `research_briefs`
- `research_steps`
- `research_sources`
- `research_source_fragments`
- `research_findings`
- `research_claims`
- `research_gaps`
- `research_reports`
- `finding_sources`
- `brief_dependencies`

## 17. 工具链设计

高阶 Agent 项目的关键之一，是让工具负责事实收集和校验，让模型负责判断和组织。

### 17.1 Discovery Tools

给 researcher 使用：

- `web_search`
- `news_search`
- `domain_search`
- `query_expander`

职责：

- 发现候选来源
- 扩展查询词
- 形成研究入口

### 17.2 Extraction Tools

给 researcher 使用：

- `page_fetch`
- `readability_extract`
- `metadata_extract`
- `content_chunker`
- `citation_anchor_builder`

职责：

- 拉取内容
- 清洗内容
- 切分证据片段
- 构建引用锚点

### 17.3 Validation Tools

给 critic 使用：

- `claim_deduper`
- `cross_source_checker`
- `recency_checker`
- `consistency_checker`
- `evidence_coverage_checker`

职责：

- 去重
- 多来源核验
- 新鲜度检查
- 冲突识别
- 证据覆盖率判断

### 17.4 Planning and Control Tools

给 supervisor 和 planner 使用：

- `brief_dependency_builder`
- `round_budget_tracker`
- `coverage_scorer`
- `followup_generator`

职责：

- 分析依赖
- 控制预算
- 判断覆盖率
- 生成下一轮补充 brief

## 18. 错误处理与容错

这个系统必须能处理中途失败，而不是一旦某步失败就整单崩溃。

规则建议：

- 搜索失败先自动重试
- 单个来源抓取失败仅影响该来源
- schema 校验失败时重试一次模型输出
- 某个 brief 失败时允许 supervisor 决定是否补建 follow-up brief
- 当局部完成但证据不充分时，允许进入 `completed_with_warnings`

## 19. 可观测性

为了突出工程能力，系统必须显式记录并展示以下信息：

- 每轮开始与结束时间
- 每个 brief 的状态变化
- 每次 agent 调用的输入输出摘要
- 重试次数
- 来源抓取成功率
- 每条 finding 的证据链
- token 使用量
- 预估成本

后续可扩展：

- OpenTelemetry trace
- Prometheus 指标
- 外部结构化日志平台

## 20. 安全与基础防护

第一版即使没有用户体系，也要有基本防护：

- 输入校验与清洗
- 对抓取协议做限制
- 网络超时与重试策略
- LLM 结构化输出校验
- 避免在日志中泄露敏感信息
- 对外部内容进行长度与格式约束，避免 prompt 污染扩大影响

## 21. 测试策略

这个项目的测试重点不只是 API 通不通，而是多 Agent 编排是否稳定。

至少覆盖：

- task 状态流转
- round 状态推进
- brief 生命周期
- supervisor 决策分支
- critic verdict 行为
- finding 到 source fragment 的关联关系
- 最终报告只消费 accepted findings
- 工具失败时的容错和重试

测试层次建议：

- 单元测试：schema、状态机、适配器、验证逻辑
- 集成测试：mock provider 下跑通一整轮或多轮任务

## 22. 前端展示重点

为了让项目一眼看起来有技术门槛，前端建议至少突出 4 个视图：

### 22.1 Task Overview

展示任务目标、状态、预算、轮次概览。

### 22.2 Round / Brief Board

展示每轮有哪些 briefs、谁在执行、是否被 critic 接受。

### 22.3 Evidence Explorer

展示某条 finding 对应哪些 source fragments，形成证据链浏览体验。

### 22.4 Final Report

展示最终报告及其引用来源、风险项和未决问题。

## 23. README 与仓库包装

这个仓库不应包装成：

- “AI 自动研究工具”

而应包装成：

- `Agentic Research Platform for Evidence-Grounded Company Intelligence`

README 应强调：

- 为什么单轮 LLM 调用不够
- 为什么需要 supervisor + critic
- 系统如何通过 evidence graph 提升可信度
- 研究流程如何可追溯
- 这个平台如何扩展成客户定制项目

## 24. 成功标准

升级后的 MVP 成功标准如下：

- 用户可以从浏览器提交研究任务并看到多轮研究过程
- 系统可以生成 briefs 并并行执行研究
- critic 能对 findings 做接受、返工或扩展判断
- findings 与 source fragments 可以双向追溯
- 最终报告只使用通过审查的研究结论
- UI 能展示这个系统不是黑盒，而是一个有监督、有证据、有审查的 Agent 平台

## 25. 第一轮实施优先级

建议实施顺序如下：

1. 项目脚手架与本地开发环境
2. 核心数据模型与状态机
3. task / round / brief 持久化
4. orchestrator 与 worker 运行框架
5. agent schema 与基础 runtime
6. discovery / extraction 工具最小集
7. critic 验证逻辑最小集
8. final report 生成
9. Web 控制台四个核心视图
10. 基础集成测试

这个顺序的目的，是尽早跑通一个“真的有多 Agent 形态”的端到端 demo，而不是先堆外围功能。
