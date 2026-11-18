# TIDE P1–P4 定义、功能与验收

本文件说明 TIDE 统一研究场景中各对象的范围、输入输出和验收结果。对象定义沿用[项目任务书](TIDE_Research_Task_Plan.md)和[最小研究场景](TIDE_Minimal_Research_Scenario/)。任务和进度见[C 组语义互操作任务清单](TIDE_C_Group_Semantic_Task_List.md)，复跑步骤见[实施与验收说明](TIDE_C_Group_Implementation_and_Acceptance.md)。

## 一次研究协作如何使用 P1–P4

| 对象 | 定义和功能 | 消费者拿到或提交什么 |
| --- | --- | --- |
| **P1 研究资源包** | 可发现、可经授权取得并复用的合成研究数据 | 获批后经 Connector 取得指定版本的文件，按清单核对哈希 |
| **P2 受限评测服务** | 在提供方内部数据上运行固定评测，支持提交、查状态和领取结果 | 获得作业 ID 和获准的结果，P2 原始记录留在提供方 |
| **P3 处理方案** | 描述本次评测的白名单参数及版本引用 | 研究团队提交一份 JSON，由 P2 验证并使用 |
| **P4 评测结果与复用记录** | 某次成功作业的汇总指标和来源记录 | 获批的研究或复查团队按作业 ID 领取结果并核对来源 |

场景有两条关联流程。第一条是**发现 P1 → 申请权限 → Connector 传输 → 核对文件**。第二条是**提交 P3 → P2 在提供方运行 → 获批领取 P4**。P3、P4 可以引用 P1 版本。P1 在评测里究竟是计算输入还是来源引用，由 A、C 组确认。

## P1 研究资源包

- **定义与范围**　沿用场景包已有的合成工业过程时序数据定义。启动包的 `p1-process.csv` 有 2,400 行，配套字典说明时间戳、控制输入、流量、当前温度和下一时刻温度标签。产品定义还包含研究说明。目录描述用于发现、了解条款与定位版本，实际交付的文件范围由 A、C 确认。
- **功能与结果**　来源项目发布经准入的资源描述。研究团队在具备资格、项目成员关系及当前有效的 `READ_DATA` 授权后，通过 Connector 取得该版本的文件。标题、条款、获取方式和版本可以从准许展示的目录字段读出。
- **验收**　保留目录条目、原生传输记录、收到的文件及接收端 SHA-256。描述、产品版本、规则版本与实际交付物对应，接收端哈希和清单一致。场景包元数据的 `checksum` 校验 CSV 字节。若交付整包，清单应分别写明整包与 CSV 的校验对象和哈希。对应 TC01、TC04。

[P1 描述](TIDE_Minimal_Research_Scenario/metadata/p1-valid.jsonld) · [数据字典](TIDE_Minimal_Research_Scenario/data/dictionary.csv) · [数据清单](TIDE_Minimal_Research_Scenario/data/data-manifest.json) · [使用说明](TIDE_Minimal_Research_Scenario/data/TERMS.md)

## P2 受限评测服务

- **定义与范围**　P2 面向消费者交付的是固定评测能力。启动包提供服务说明和一份独立生成的 2,400 行合成 CSV，CSV 供提供方内部使用。服务说明定义 P3 输入、P4 输出和固定 ARX 基线。ARX 基线按约定使用时序特征预测下一时刻温度。
- **功能与结果**　具备 `SUBMIT_RECIPE` 授权的研究团队提交 P3。服务校验请求、返回 `job_id`，并按作业提供排队、运行和终态。提交、执行前和结果领取分别检查当前权限。成功作业生成 P4。输入不合格、执行失败或无法计算有效指标时，返回相应错误或失败状态。
- **验收**　保留合法请求、真实作业 ID、执行日志、服务版本和结果。覆盖非法输入拒绝、授权检查和输出范围。消费者出口只提供约定状态和获准结果。服务说明的 SHA-256 与内部 CSV 的 SHA-256 分别核对。对应 TC06。
- **场景包状态**　服务说明标记为 `NOT_IMPLEMENTED`，OpenAPI 给出的是业务接口设计。实际运行证据以部署后的执行记录为准。

[P2 描述](TIDE_Minimal_Research_Scenario/metadata/p2-valid.jsonld) · [服务说明](TIDE_Minimal_Research_Scenario/api/p2-service-description.json) · [OpenAPI](TIDE_Minimal_Research_Scenario/api/openapi.json)

## P3 处理方案

- **定义与范围**　研究团队提交的白名单 JSON 参数。每份请求带 `recipe_id`、项目和版本引用，由 P2 的固定管线解释。以下值是启动包 Schema 的现有约束。
- **功能与结果**　合法 P3 被接受后，调用方收到作业 ID，可以查询对应作业。P2 将实际采用的请求与该作业关联，P4 用 `recipe_id` 和 `recipe_sha256` 引用它。额外字段、超限参数或不兼容版本应明确拒绝，或按已确认的映射规则处理适用的单位或版本转换。
- **验收**　用合法请求触发实际作业，并用未知 `script` 字段、超限窗口或把 `target_temp` 放入特征的反例验证服务入口。记录导致拒绝的规则。对应 TC05、TC06。

| 字段 | 启动包允许的内容 |
| --- | --- |
| `feature_fields` | `control_input`、`flow_rate`、`temperature` 三个字段，各出现一次 |
| `target_field` | `target_temp`，仅作标签 |
| `missing_strategy` | `forward_fill` 或 `train_mean` |
| `smoothing_window` | `1`、`3` 或 `5` |
| `lag` | `1`、`2` 或 `3` |
| `train_fraction` | 固定 `0.7`，按时间划分训练和测试 |
| `p1_version`、`p2_version`、`schema_version` | 启动包均固定为 `1.0.0`。产品升级后的兼容和启用版本由 A、C 确认 |

[P3 规则](TIDE_Minimal_Research_Scenario/schemas/recipe.schema.json) · [合法请求](TIDE_Minimal_Research_Scenario/examples/recipe-valid.json) · [错误请求](TIDE_Minimal_Research_Scenario/examples/recipe-invalid.json)

## P4 评测结果与复用记录

- **定义与范围**　一次成功作业生成一份 P4。`job_id` 标识具体作业，启动规则用同一个 `resource_id` 标识 P4 结果资源。P4 包含 `mae`（平均绝对误差）、`n_train`、`n_test`、`valid_ratio`，以及项目、协议、请求、数据、算法版本和时间等追溯信息。对消费者只返回汇总指标与约定来源字段，逐条记录、逐条预测和逐条标签留在提供方边界内。
- **功能与结果**　有当前有效 `READ_RESULT` 授权的研究或复查团队按作业领取结果。复查者用自己的权限核对数据版本及哈希、Recipe 标识及哈希、`benchmark_version` 和 `agreement_id`。P4 的 P2 数据哈希对应内部 CSV，P2 产品描述中的 `checksum` 对应服务说明，两者核对不同对象。
- **验收**　使用一次真实成功作业生成符合 Schema 的 P4，并用包含 `records` 的反例验证输出规则。固定输入、算法、环境及规则复跑两次，保留不同作业 ID 和执行记录。样本数一致，MAE 差在约定容差内，两份结果均可追溯。验收看实际计算、输出范围和可复查性，任务书没有设定模型分数提升门槛。对应 TC06、TC08。
- **场景包状态**　`result-valid-fixture.json` 中的分数、样本数和作业 ID 是格式示例。正式验收使用实际作业生成的值。

[P4 规则](TIDE_Minimal_Research_Scenario/schemas/result.schema.json) · [格式示例](TIDE_Minimal_Research_Scenario/examples/result-valid-fixture.json) · [越界输出反例](TIDE_Minimal_Research_Scenario/examples/result-invalid-leak.json)

## 联调前需要确认的口径

| 事项 | 确认后应留下的记录 |
| --- | --- |
| P1 的交付与发布 | A、C 确认交付 CSV 或整包、版本、哈希对象和目录白名单。权利、使用条款和展示范围由资源负责人确认 |
| P2 的实际计算输入 | A 组目前拟用 P2 内部数据训练和测试，P1 仅作来源引用。A、C 共同固定实际输入、切分、跨边界标签处理、预处理和 `valid_ratio` 的分母 |
| P3/P4 的版本与来源 | A、C 明确启用的产品及规则版本、`recipe_sha256` 的计算口径，以及服务版本与 `benchmark_version` 的关系。启动包的 P3/P4 描述引用的是示例文件，运行作业用实际请求和输出的标识追溯 |

[跨组待议 C1–C15](../../跨组待议.md)
