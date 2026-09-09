# Dramaturg（戏剧顾问）— Agentic Cinema 黑客松参赛计划

> **核心定位**：读一段剧本，用 Parallel Search 实时检索每个真实世界引用（地点 / 历史事件 / 公众人物 / 职业 / 技术 / 法律），逐条核验事实、保留冲突、给出带引用的"准确性档案"，标记时代错误、法律伦理风险，并建议修正。
>
> **不是**趋势研究，不是剧本生成器，不是分镜/视频流水线；它回答的是：**编剧写下的每个真实世界细节，经得起公开网络的检验吗？**
>
> 比赛：[Agentic Cinema: The Blockbuster Hackathon](https://agentic-cinema.devpost.com/)  
> 赛道：**Parallel**（[Parallel Resources](https://agentic-cinema.devpost.com/details/parallel-resources)）  
> 官方截止：2026-09-09 14:00 PDT，即 UTC+8 的 **2026-09-10 05:00**  
> 调研快照：2026-09-09，Parallel 赛道已公开竞品 3 个（见第 2 节）

---

## 0. 当前结论

1. **截止时间就是今晚。** 官方截止 UTC+8 9月10日清晨 5:00。这不是"规划一个多周项目"，而是一个**当夜冲刺、天亮前提交**的作战计划。所有范围以"今晚能端到端跑通并录出 3 分钟演示"为唯一标准。
2. **Parallel 赛道现有竞品全部集中在"检索网络 → 创意生成"**（趋势研究、剧本医生、想法→视频流水线）。**没有任何项目做"事实验证"。** 这是最大的空白，也是 Parallel 自身产品叙事（fresh、traceable、verifiable）最契合的角度。
3. **产品概念：Dramaturg。** "戏剧顾问"是影视行业里真实存在的岗位——专门做事实考证、历史准确性、连续性检查。我们把这个角色做成一个 Gemini agent，用 Parallel Search 作为它的"眼睛"，逐条核验剧本里的真实世界引用。
4. **差异化护城河（相对三个已知竞品）：**
   - Genesis OS 做"情报局为 Studio Head 提供战略决策"——我们做"为编剧和剧组提供逐条事实核验"；
   - CineIntel 做"趋势研究 + 剧本医生（改写）"——我们做"事实核查（不改写，只标注 + 引用）"；
   - Agentic Story Studio 做"想法 → 视频"全流水线——我们只做前置的"准确性关卡"，更窄、更深、更可演示。
5. **官方评分四项等权**（Technological Implementation / Design / Potential Impact / Quality of Idea）。Dramaturg 在 **Quality of Idea**（非显而易见的验证角度）和 **Potential Impact**（解决真实的前期制作考证成本）上天然占优；**Technological Implementation** 靠确定性核验链路 + 溯源 + 冲突保留来拿分；**Design** 靠"逐条 claim 卡片 + 证据 + 来源链接"的清晰界面。
6. **MVP 只做一条可复现链路**：粘贴剧本 → Gemini 抽取可验证 claim → Parallel 逐条检索 → Gemini 核验打标 → 输出准确性档案。不堆功能。

---

## 1. 官方需求与评分

### 1.1 参赛硬性要求（来自 Official Rules）

- **必须**用 Gemini + Google Cloud Agent Builder 构建 agent 或多 agent 网络；
- **必须**集成一个 Partner 的产品/MCP——本赛道为 **Parallel**，且**必须在运行时实际调用 Parallel Search API**（README 里写不算）；
- 解决娱乐/媒体价值链的真实瓶颈，目标用户为 **filmmakers / screenwriters / studio crews / fans** 之一；
- **AI 限制**：只能用 Google Cloud 的 AI 工具（Gemini 等），**禁止**其他厂商的 AI 模型/agent 框架/AI API（OpenAI、Anthropic 等）。LangChain 等"agent 框架"有被判定违规的风险，**本项目不使用**，改用 `google-genai` 原生 function calling；
- 平台：web / Android / iOS 至少其一（本项目为 **web**）；
- 比赛期间新建项目，须为原创；
- **提交物**：托管项目 URL + 文本描述 + 公开开源代码仓库（含开源 license，README 顶部 About 可见）+ ≤3 分钟演示视频（YouTube/Vimeo 公开，英文或英文字幕）；
- 代码仓库须**在运行时实际调用** Google Cloud 与 Partner 服务（imported and actually called），接受的 Google Cloud 包：`google-adk` / `google-genai` / `google-generativeai` / `google-cloud-aiplatform`；Parallel 接受 `parallel-web` SDK 等。

### 1.2 官方评分（Stage Two，四项等权）

| 评分项 | 权重 | Dramaturg 的应对 |
|---|---:|---|
| Technological Implementation | 25% | 确定性核验链路；每条 claim 带 Parallel 检索结果 + 来源 URL + 摘录；冲突保留而非抹平；结构化中间数据可复现 |
| Design | 25% | 逐条 claim 卡片（状态徽章 + 证据摘录 + 源链接 + 修正建议）+ 总览记分卡；不是技术 demo，是一个连贯的"剧本审稿"产品体验 |
| Potential Impact | 25% | 前期制作考证是真实成本中心；服务编剧 + 剧组（美术/场记/道具）；演示能展示"省掉几小时人工查资料" |
| Quality of Idea | 25% | 非显而易见：竞品都在生成，我们在验证；用 Parallel 的"可溯源"特性做它最擅长的事 |

> 平局打破顺序：按上述四项依次比较。Dramaturg 在 Quality of Idea 和 Potential Impact 上领先，正是平局时的胜负手。

---

## 2. Parallel 赛道竞争格局

### 2.1 已知竞品（截至 2026-09-09）

| 项目 | 已展示能力 | 与 Dramaturg 的重叠 | Dramaturg 守住的差异 |
|---|---|---|---|
| [Genesis OS — Signal Intelligence](https://github.com/MoreSalamander/01-genesis-parallel) | 为虚构 Convergence Studios 做"情报局"：agent 规划任务 → Parallel 检索证据 → 验证 claim（保留冲突）→ 构建溯源知识图谱 → 向人类 Studio Head 提供证据 backed 建议 | **中**：都做"验证 + 保留冲突 + 溯源" | Genesis 面向 Studio Head 的**战略决策**；Dramaturg 面向**编剧/剧组的逐条事实核验**，输入是剧本、输出是可操作的修正建议，不是战略情报 |
| [CineIntel Engine](https://github.com/AtchayamG/cineintel-engine) | 实时网络 grounding + 影视趋势研究 + 自动剧本医生；TrendAnalyst / GroundedWriter / CastingIntel 三 agent | **中高**：都"Parallel 检索 + Gemini 综合" | CineIntel 做**趋势研究 + 改写剧本**；Dramaturg **不改写**，只做事实核查与标注，职责更窄更深，且逐条可溯源 |
| [Agentic Story Studio](https://github.com/Senseiglobal/agentic-story-studio) | 复杂想法 → Parallel 检索证据 → 证据账本 → 故事大纲 → 分镜 → Imagen/Veo 生成视频 | **低**：都"Parallel 检索 + 证据" | Story Studio 是**全流水线到视频**；Dramaturg 只做前置**准确性关卡**，不碰生成 |

### 2.2 共同模式与空白

- **共同模式**：三个项目都是"检索网络 → 喂给 Gemini → 产出创意内容（趋势/剧本/视频）"。Parallel 在它们手里是"创意灵感来源"。
- **空白**：没有人把 Parallel 用作**事实裁判**——用它的 fresh + traceable 特性去**证伪**剧本里的细节，而不是去**生成**新内容。这正是 Parallel 产品叙事里"verifiable"一词的落点。
- **风险点**：Genesis OS 已经做了"验证 + 保留冲突 + 溯源"，这是和 Dramaturg 最像的地方。Dramaturg 必须在**输入（剧本）+ 输出（逐条修正建议）+ 用户（编剧/剧组）**上与 Genesis 的"战略情报"拉开距离，并在演示里强调"我读的是剧本场景，输出的是每个错误怎么改"。

---

## 3. 产品定位与差异化

### 3.1 一句话

**Dramaturg 是一个 AI 戏剧顾问：它读你的剧本，用实时网络检索核验每个真实世界细节，告诉你哪里写错了、依据是什么、怎么改——而你始终是最终拍板的人。**

### 3.2 目标用户与解决的瓶颈

- **主用户：编剧（screenwriters）**。痛点：写一个历史剧/职业剧/科技题材，每个真实细节（某年某事件、某地某规矩、某职业某流程、某技术某参数）都要查半天，查错了到拍摄期才被发现，返工成本极高。
- **次用户：剧组（studio crews）**——美术指导（年代考证）、场记（连续性）、道具（器材年代）。痛点：拿到剧本后要逐条核实可拍摄性。
- **不服务**：粉丝向、纯创意生成、后期制作。聚焦前期"考证关卡"。

### 3.3 与竞品的差异化矩阵

| 维度 | Genesis OS | CineIntel | Agentic Story Studio | **Dramaturg** |
|---|---|---|---|---|
| 输入 | 战略问题 | 主题/趋势 | 复杂想法 | **剧本场景** |
| Parallel 用途 | 检索证据做战略情报 | 检索趋势做创作 | 检索证据做故事 | **检索证据做事实裁判** |
| 输出 | 战略建议 | 趋势报告/改写剧本 | 视频 | **逐条事实核验 + 修正建议** |
| 改写原文？ | 否 | 是 | 是（生成） | **否（只标注）** |
| 保留冲突？ | 是 | 部分 | 否 | **是** |
| 用户 | Studio Head | 编剧 | 创作者 | **编剧 + 剧组** |

### 3.4 为什么是 Parallel 赛道的最佳契合

Parallel 官方文档把自家 Search API 定位为"accurate, fresh, **traceable** information from the open web"，强调"verifiable"。Dramaturg 把这个词从营销话术变成产品功能：**每个核验结论都挂着一个可点击的来源 URL**。这是 Parallel 最想被这样用的场景，也是评审（Parallel 的人）最容易买单的叙事。

---

## 4. 技术架构

### 4.1 总体链路

```
剧本场景（粘贴 / 上传 .txt / .fountain）
        │
        ▼
[1] Claim Extraction（Gemini，长上下文）
   抽取"可验证 claim"：地点 / 历史事件+日期 / 公众人物 / 职业流程 / 技术参数 / 法律法规 / 年代文化细节
   每条 claim：{ id, text, category, verifiable_question, search_keywords }
        │
        ▼
[2] Parallel Search（parallel-web SDK，运行时实际调用）
   对每条 claim：objective = verifiable_question，search_queries = search_keywords
   返回：{ url, title, excerpts[] } per result
        │
        ▼
[3] Verification（Gemini，function calling 编排）
   对每条 claim × 检索摘录，判定状态：
     VERIFIED / UNVERIFIED / INACCURATE / CONFLICTED
   附：supporting excerpts + source URLs + 一句话依据 + 修正建议
   冲突时：保留双方证据，不抹平
        │
        ▼
[4] Dossier 输出
   - 逐条 claim 卡片（状态徽章 + 证据摘录 + 源链接 + 修正建议）
   - 总览记分卡（X 条核验 / Y 条准确 / Z 条有误 / W 条冲突 / N 条无法核实）
   - 人类编剧始终是最终拍板者（每条可"接受/忽略/再查"）
```

### 4.2 技术栈（最小可发布）

| 层 | 选型 | 理由 |
|---|---|---|
| LLM | Gemini（`google-genai` SDK，function calling） | 官方接受包；原生 function calling 编排 agent loop，不引入 LangChain 等可能违规的 agent 框架 |
| 检索 | Parallel Search API（`parallel-web` Python SDK） | 赛道硬性要求；运行时实际调用，代码里可见 `from parallel import Parallel` |
| Agent 编排 | `google-genai` function calling（Parallel search 作为 tool 函数） | 最快可发布；如时间富余可升级到 `google-adk` |
| 后端 | Python + FastAPI | 轻量、易部署 Cloud Run |
| 前端 | 单页 HTML/JS（参考 DemandRadar 的 vanilla 模式）或 Streamlit | 优先 Streamlit 求速度；若要更可控的 UI 用 HTML/JS |
| 部署 | Google Cloud Run | 满足"托管项目 URL"；资源页推荐 Cloud Run Quickstart |
| 密钥 | Secret Manager 或环境变量 | Parallel API key + Gemini 凭据 |

### 4.3 关键合规点（务必满足，否则 Stage One 直接淘汰）

- 代码里**实际 import 并调用** `google-genai`（Gemini）和 `parallel`（Parallel SDK），不是只在 README 提；
- **只用** Gemini 作为 AI，**不**用 OpenAI/Anthropic/其他 agent 框架；
- 仓库**公开 + 开源 license**（MIT/Apache），license 文件在仓库根、About 区可见；
- 演示视频 ≤3 分钟、英文或英文字幕、YouTube/Vimeo 公开；
- 托管 URL 可访问（Cloud Run）。

### 4.4 升级路径（时间富余才做）

- 用 `google-adk` 重写 agent loop，部署到 Agent Engine（更贴资源页推荐，但 setup 更重）；
- 多 agent：抽取 agent / 检索 agent / 核验 agent 分工；
- 用 Parallel 的 `web_fetch`（Extract）对关键来源做深读；
- 上传 .fountain / .pdf 剧本（Document Processing）。

---

## 5. MVP 范围（今晚必做）

### 5.1 必做（P0）

1. **粘贴剧本场景** → 文本框输入（先不做文件上传）。
2. **Claim 抽取**：Gemini 输出结构化 JSON 列表（每条含 category / verifiable_question / search_keywords）。
3. **Parallel 检索**：对每条 claim 调 `parallel.search()`，拿到 url + excerpts。
4. **核验打标**：Gemini 判定 VERIFIED/UNVERIFIED/INACCURATE/CONFLICTED + 依据 + 源链接 + 修正建议；冲突保留双方。
5. **Dossier UI**：逐条卡片 + 总览记分卡。
6. **确定性演示数据**：一段故意埋了 4 个事实错误的剧本场景（错年份 / 错地点细节 / 时代错误的技术 / 误述的法律），跑一遍能稳定抓出这 4 个错并带来源。
7. **部署到 Cloud Run**，拿到公开 URL。
8. **录 3 分钟演示视频**（英文或英文字幕）。
9. **README + 开源 license + 文本描述**。

### 5.2 不做（P1/P2，留到时间富余）

- 文件上传、.fountain 解析、PDF；
- 多 agent 分工、ADK/Agent Engine；
- "再查"交互、用户标注反馈；
- 多场景批量、整本剧本；
- 历史会话保存。

### 5.3 演示剧本场景（确定性 demo 的核心）

准备一段约 300 字的剧本场景，题材选**1989 年柏林墙倒塌**当夜的故事，故意埋入：
1. **错年份**：把柏林墙倒塌写成 1987 年（实际 1989-11-09）；
2. **错地点细节**：写"勃兰登堡门位于东柏林西侧"（实际位于柏林墙边界、东西柏林交界，表述需精确）；
3. **时代错误的技术**：让角色用 GSM 手机发短信（GSM 短信商用是 1992 年后，1989 年不可能）；
4. **误述的法律/程序**：写"东德公民凭签证可自由穿越查理检查站"（实际需特定许可，1989 年 11 月 9 日晚是因 Schabowski 失误才开放）。

跑通后，Dramaturg 应稳定抓出这 4 个错，每条带 Parallel 来源 URL。这是 3 分钟视频的杀手锏镜头。

---

## 6. 实施步骤与时间表（当夜冲刺，UTC+8）

> 截止 UTC+8 9月10日 05:00。以下为约 10 小时冲刺，按小时桶分配。若起步更晚则压缩 P0 的 polish。

| 时段 | 任务 | 产出 |
|---|---|---|
| T+0~1h | 环境与凭据：GCP 项目、Cloud Run、Parallel API key、Gemini API；本地 `pip install google-genai parallel-web fastapi uvicorn`；跑通 Parallel 一次 search、Gemini 一次 function call | 两个最小调用脚本各跑通 |
| T+1~3h | Claim 抽取 + Parallel 检索 + 核验打标的后端逻辑（纯 Python 函数，先不接 UI） | 命令行能输入场景文本、输出 JSON dossier |
| T+3~5h | FastAPI 端点 + 最小前端（Streamlit 或 HTML/JS）：粘贴 → 流式/同步展示逐条卡片 | 本地 http 端到端跑通 |
| T+5~6h | 写确定性演示剧本场景（1989 柏林墙，4 个错），调试到稳定抓出 | demo 场景稳定输出 |
| T+6~7h | 部署 Cloud Run，拿到公开 URL，线上跑通 demo | 托管 URL 可用 |
| T+7~8h | 录 3 分钟演示视频（英文或加英文字幕），上传 YouTube/Vimeo | 视频公开链接 |
| T+8~9h | README（含运行说明、架构图、Parallel+Gemini 运行时调用说明）、LICENSE、Devpost 文本描述 | 仓库提交就绪 |
| T+9~10h | 自检合规清单（见第 7 节），提交 Devpost，缓冲 | 提交完成 |

---

## 7. 提交清单与合规自检

### 7.1 提交物

- [ ] 托管项目 URL（Cloud Run，公开可访问）
- [ ] 公开代码仓库（GitHub/GitLab/Bitbucket），含：
  - [ ] 开源 license 文件（MIT 或 Apache-2.0），仓库根 + About 区可见
  - [ ] 代码里 `import genai`（google-genai）并实际调用 Gemini
  - [ ] 代码里 `from parallel import Parallel` 并实际调用 `client.search(...)`
  - [ ] README：功能、技术栈、运行步骤、Parallel+Gemini 运行时调用说明
- [ ] ≤3 分钟演示视频，YouTube/Vimeo 公开，英文或英文字幕
- [ ] Devpost 文本描述：功能摘要、技术、数据来源、发现与学习

### 7.2 合规自检（Stage One pass/fail）

- [ ] 用了 Gemini + Google Cloud（google-genai）
- [ ] 运行时实际调用 Parallel Search API（代码可见，非 README 提及）
- [ ] 只用 Google Cloud AI，无 OpenAI/Anthropic/其他 agent 框架
- [ ] web 平台可运行
- [ ] 比赛期间新建、原创
- [ ] 视频无第三方广告/商标/侵权内容
- [ ] 仓库公开 + 开源 license

---

## 8. 风险与降级

| 风险 | 概率 | 降级方案 |
|---|---|---|
| Parallel API 限额/延迟 | 中 | 用 `mode: "fast"`；demo 场景的 claim 数控制在 6~8 条；本地缓存检索结果用于演示回放 |
| Gemini function calling 不稳定输出 JSON | 中 | 用 Gemini 的 JSON schema / structured output；加正则兜底解析；极端情况退化为"抽取用一次调用、核验用一次调用"两段式 |
| Cloud Run 部署卡住 | 中 | 降级到本地 `python3 -m http.server` + ngrok / Render / 任何公开 URL；只要 URL 可访问即可，规则不限定平台（仅 Replit 赛道要求 replit 域名） |
| 演示场景抓不出错 | 低 | 预先手动验证每个埋错都能被 Parallel 检索到反证；准备备用场景 |
| 时间不够 | 高 | 砍前端 polish，用 Streamlit 默认 UI；砍多 claim，只演示 4 条；保证"输入→核验→带源输出"链路完整可录 |
| 被判定用了违规 agent 框架 | 低 | 全程只用 google-genai 原生 function calling，不碰 LangChain |

---

## 9. 一句话电梯演讲（写进 Devpost 描述开头）

> Dramaturg is an AI dramaturg for screenwriters. Paste a scene; it reads every real-world detail—locations, historical events, public figures, professions, technology, laws—and checks each against the live web with Parallel Search. It tells you what's wrong, shows the source, and suggests the fix, while you stay the final authority. Where every other agent generates, this one verifies.
