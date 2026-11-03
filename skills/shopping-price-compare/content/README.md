# 淘宝京东拼多多比价 · Agent Skill

> **English** — An agent skill that compares live prices for the same product across Taobao/Tmall, JD.com and Pinduoduo in one request. It returns the final price after coupons, subsidies and group-buy discounts, the conditions that apply, and a purchase link, and tells you which platform is cheapest and by how much. Built for China mainland e-commerce; works with any agent that supports the `SKILL.md` format.
>
> **中文** — 一个智能体技能：一句话同时比较淘宝/天猫、京东、拼多多三个平台的实时价格，给出已算上优惠券、补贴和拼单的到手价、适用条件和购买链接，并告诉你哪家最便宜、便宜多少。面向中国大陆电商，适用于支持 `SKILL.md` 格式的智能体。

## 能做什么

- 按预算推荐：“300 元以内的降噪蓝牙耳机推荐 2 款”
- 具体型号问价：“iPhone 17 256G 哪里买最便宜”
- 三平台比价、找平替、送礼挑选
- 缺条件时只追问一次（预算、用途、平台）

不处理：写文案、查天气、与购物无关的问答、下单后的售后和物流。

## 目录结构

```
shopping-price-compare/
├── SKILL.md              # 技能说明与规则（智能体读取）
├── _meta.json            # 技能元数据
├── scripts/shop_search.py # 取商品数据的脚本，只用 Python 标准库
├── examples/cases.json    # 触发与降级的测试用例
├── assets/icon.png        # 技能图标（512×512 PNG，可选）
├── README.md
└── LICENSE
```

> `assets/icon.png` 仅用于展示。若运行环境不支持二进制资源，删除 `assets/` 目录后技能功能完全不受影响（脚本与文档均为纯文本）。

## 安装

把 `shopping-price-compare/` 整个目录复制到你的智能体的技能目录，例如：

```bash
# Claude Code（个人）
cp -R shopping-price-compare ~/.claude/skills/
```

打包成 zip 上传：

```bash
zip -r shopping-price-compare.zip shopping-price-compare -x '*.DS_Store' '*__MACOSX*' '*/._*'
```

## 运行要求

- Python 3（`python3` 或 `python`），无需安装依赖。
- 能访问 HTTPS 外网。不需要账号、密钥或任何配置。

单独试跑：

```bash
python3 shopping-price-compare/scripts/shop_search.py '{"keywords":["降噪蓝牙耳机"],"budget_max_minor":30000,"limit":3,"original_query":"300以内降噪耳机"}'
```

输出一行 JSON（商品、到手价、购买链接和展示说明）。`SHOP_SEARCH_API_URL` 环境变量可覆盖服务地址。

## 数据去向

脚本只把这次的购物参数（关键词、预算、条件、用户原话）通过 HTTPS 发送给作者运营的购物推荐服务，由服务返回商品、到手价和购买链接。不读取本机其他文件，不需要也不收集账号、密钥或个人信息。返回的购买链接是该服务生成的跳转链接。

服务由作者个人运营，可能限流（短时间内请求过多会返回“请求太频繁”），也可能临时不可用；不可用时技能会改为联网搜索并注明价格仅供参考。

## 说明

- 价格每天变化，结果为查询时刻的数据，以下单页为准。
- 技能不会代你下单、支付或领券。

## 作者

中贸宏图

## 许可

[MIT](LICENSE)。本仓库的技能文件和脚本可自由使用、修改和分发；脚本请求的购物推荐服务由作者运营，不在本许可范围内，使用时遵循上文“数据去向”和限流说明。
