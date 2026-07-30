
# Copilot multi-agent model selection - audit result

Audited 30 July 2026 against GitHub and VS Code primary documentation.
Scope as briefed: VS Code custom agents, usage-based billing, providers limited
to OpenAI, Anthropic, Google, and MAI-Code-1-Flash.

## TL;DR

- **The architecture is broken by a documented rule, not by a pricing error.**
  VS Code: *"The requested model cannot exceed the cost tier of the main model.
  If you request a more expensive model, the subagent falls back to the main
  model."* The recommended stack puts the **cheapest** model in the main session
  and pricier ones in the subagents, so under this rule **both subagents
  silently run on GPT-5 mini**. The cost model is fiction in the user's favour
  on price and against them on quality.
- **Every rate was transcribed correctly.** All 14 claimed input/output pairs
  match GitHub's table exactly, including the Sonnet 5 promo date. Spend no
  more worry there.
- **The real failure is omission.** **GPT-5.6 Luna ($1.00/$6.00, GA)** was never
  considered and beats Claude Sonnet 5 on both dimensions for the planner role,
  with no promotional cliff. **Gemini 3.6 Flash ($1.50/$7.50, GA)** was likewise
  missed and is the GA answer to preview-risk on Gemini 3 Flash.
- **The model ID format in the recommendation is wrong.** IDs are picker
  **display names**, e.g. `Claude Haiku 4.5 (copilot)`, not the inferred
  `claude-sonnet-4.5` kebab pattern. An unresolvable name falls back **silently**
  to the parent model, which is exactly the failure you flagged.
- **C3's cost logic is backwards.** Within a 3-attempt cap, GPT-5.4 nano failing
  *all three* times costs $0.105, still less than MAI-Code-1-Flash succeeding
  once at $0.1275. The cheap coder cannot lose on token cost alone inside one
  cycle. The argument against it is capability and latency, not spend.
- **C6 rests on one forum post.** A single user, no corroboration, no official
  response, unresolved. Keep the conclusion, discard the evidence: use the
  vendor's own admission of sub-50% adversarial reasoning instead.
- **Sonnet 5's promo expires in 32 days** (31 Aug 2026) and GitHub does not
  document the post-promo rate. Any Sonnet-5-based plan needs a decision before
  then.
- **A 10% discount exists for auto model selection**, which pinning models
  presumably forfeits. Not addressed anywhere in the original analysis.

## Verdict table (C1-C11)

| # | Claim | Verdict | Note |
|:--|:--|:--|:--|
| C1 | Output costs 5-8x input across the roster | **CONFIRMED** | Holds exactly across your accessible set: Anthropic uniformly 5.0x, OpenAI 6.0-8.0x, Google 5.0-8.0x, MAI 6.0x. The only two exceptions on the whole roster are Grok 4.5 (3.0x) and Kimi K2.7 (4.2x), which are the two models you cannot use. [source](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) |
| C2 | Coder dominates total spend | **CONFIRMED** | ~65% of cycle cost on the briefed assumptions, and caching *raises* it to ~68% rather than shifting it. See Q4. |
| C3 | Cheapest model is the wrong coder because 3 attempts cost more than 1 success | **PARTLY WRONG** | Conclusion defensible, arithmetic is not. Nano at 3 attempts = $0.105 < MAI at 1 attempt = $0.1275. Break-even is 3.6 attempts, above the cap. Cost never punishes the cheap coder inside one cycle. |
| C4 | Planner is cheap, so economising there is false economy | **PARTLY WRONG** | The absolute figure is right ($0.09/cycle for Sonnet 5, matching the claimed $0.07-0.10). "Almost regardless of which good model" is not: the spread across sensible planners is $0.01 to $0.10, a 10x range. Break-even derived in Q4. |
| C5 | MAI trained against the production Copilot harness | **CONFIRMED (vendor claim)** | Microsoft states it was *"trained directly with GitHub Copilot harnesses used in production"*, claims +16 points on SWE-Bench Pro vs Haiku 4.5 (51.2% vs 35.2%) and *"up to 60% fewer tokens"*. Marketing, as you flagged, but the token-efficiency claim is the strongest economic argument for MAI and nobody made it. [source](https://microsoft.ai/news/introducingmai-code-1-flash/) |
| C6 | MAI unusable as planner: runaway Plan-mode loops | **PARTLY WRONG** | Directionally fine, evidentially thin. Exactly one user (riceze, 6 Jul 2026), zero corroborating replies, no official response, unresolved. Weight it as an anecdote. The vendor's own admission that *"Einstellung traps remained below 50% accuracy"* is better support for the same conclusion. [source](https://github.com/orgs/community/discussions/197306) |
| C7 | Sonnet 5 $2/$10 is promotional, expires 31 Aug 2026 | **CONFIRMED** | Verbatim in GitHub's table: "Promo pricing through 8/31/26". Cache-write is $2.50. **The post-promo rate is not documented anywhere I could find.** All other Anthropic Sonnet models sit at $3.00/$15.00, but treating that as the landing spot is inference, not documentation. Labelled UNVERIFIED. |
| C8 | Gemini 3 Flash and 3.1 Pro are public preview | **CONFIRMED** | Both listed Public preview on the supported-models and pricing pages. Note Gemini 3.5 Flash and 3.6 Flash are **GA**, which is the missed alternative. |
| C9 | `model` pins the model; omitting inherits the picker | **PARTLY WRONG** | The inherit half is exact: *"If not specified, the currently selected model in model picker is used."* "Pins" is too strong. Three documented paths override it: the cost-tier cap, silent fallback on an unresolvable name, and [issue #291883](https://github.com/microsoft/vscode/issues/291883), where the field was reported simply not respected. |
| C10 | VS Code accepts `model` as an array; CLI does not | **CONFIRMED** | VS Code: *"When you specify an array, the system tries each model in order until an available one is found."* CLI rejects arrays ([issue #2133](https://github.com/github/copilot-cli/issues/2133)). **But it is an availability chain only** - see the Q3 caveat, it does not rescue you from the cost-tier cap. |
| C11 | `tools:` can strip edit tools from main and planner | **CONFIRMED** | Documented property, list of tool/tool-set names. Two better instruments went unmentioned: `agents` (restrict which subagents an agent may call, `[]` to forbid all) and `disable-model-invocation` (stop an agent being invoked as a subagent at all). [source](https://code.visualstudio.com/docs/agent-customization/custom-agents) |

`target: vscode` **CONFIRMED** - allowed values `vscode` and `github-copilot`,
defaults to both if unset. Custom agent prompts cap at 30,000 characters.

## Q1 - Rates, as verified

Every claimed rate is correct. Reproduced with the cached and cache-write
columns the original omitted (per 1M tokens).

| Model | Provider | Status | In | Cached in | Cache write | Out | Out/in |
|:--|:--|:--|--:|--:|--:|--:|--:|
| GPT-5.4 nano | OpenAI | GA | 0.20 | 0.02 | - | 1.25 | 6.25x |
| GPT-5 mini | OpenAI | GA | 0.25 | 0.025 | - | 2.00 | 8.0x |
| GPT-5.4 mini | OpenAI | GA | 0.75 | 0.075 | - | 4.50 | 6.0x |
| **GPT-5.6 Luna** | OpenAI | GA | **1.00** | 0.10 | - | **6.00** | 6.0x |
| GPT-5.3-Codex | OpenAI | GA | 1.75 | 0.175 | - | 14.00 | 8.0x |
| GPT-5.4 | OpenAI | GA | 2.50 | 0.25 | - | 15.00 | 6.0x |
| MAI-Code-1-Flash | Microsoft | GA | 0.75 | 0.075 | - | 4.50 | 6.0x |
| Claude Haiku 4.5 | Anthropic | GA | 1.00 | 0.10 | 1.25 | 5.00 | 5.0x |
| Claude Sonnet 5 | Anthropic | GA | 2.00 | 0.20 | 2.50 | 10.00 | 5.0x |
| Claude Sonnet 4.6 | Anthropic | GA | 3.00 | 0.30 | 3.75 | 15.00 | 5.0x |
| Claude Opus 5 | Anthropic | GA | 5.00 | 0.50 | 6.25 | 25.00 | 5.0x |
| Gemini 2.5 Pro | Google | GA | 1.25 | 0.125 | - | 10.00 | 8.0x |
| Gemini 3 Flash | Google | **Preview** | 0.50 | 0.05 | - | 3.00 | 6.0x |
| **Gemini 3.6 Flash** | Google | GA | **1.50** | 0.15 | - | **7.50** | 5.0x |
| Gemini 3.5 Flash | Google | GA | 1.50 | 0.15 | - | 9.00 | 6.0x |
| Gemini 3.1 Pro | Google | **Preview** | 2.00 | 0.20 | - | 12.00 | 6.0x |

Long-context tiers exist for GPT-5.4/5.5/5.6 (>272K) and Gemini 3.1 Pro (>200K)
at roughly double input. Irrelevant for greenfield prototypes; relevant if a
session's accumulated context crosses the threshold.

### Does the Anthropic cache-write rate distort the comparison?

No, but it is worth knowing. Cache write is a uniform **1.25x input** across
every Anthropic model; OpenAI and Google show no cache-write line at all.
Writing costs a 0.25x premium and each subsequent read saves 0.9x, so the
break-even is **0.28 reads** - the first re-read already pays for the write.
In an agentic loop that reuses a prefix 3+ times it is negligible. The real
asymmetry is structural: Anthropic charges to build the cache and its
competitors here appear not to.

### Models never considered that should have been

| Model | Rate | Why it matters |
|:--|:--|:--|
| **GPT-5.6 Luna** | $1.00/$6.00 GA | Cheaper than Sonnet 5 on **both** dimensions, GA, no promo cliff. The single most consequential omission. |
| **Gemini 3.6 Flash** | $1.50/$7.50 GA | GA alternative to preview-risk Gemini 3 Flash; lowest output/input ratio (5.0x) of any Google model. |
| Gemini 3.5 Flash | $1.50/$9.00 GA | Strictly worse than 3.6 Flash. Listed only so you can rule it out. |
| Claude Sonnet 4.6 | $3.00/$15.00 GA | The non-promotional Anthropic mid-tier, and a plausible landing spot if Sonnet 5 reverts. |
| GPT-5.4 | $2.50/$15.00 GA | Relevant only as a high ceiling for the main session (see Q2). |

## Q2 - Corrected assignment

**The cost-tier cap inverts the design rule.** Because a subagent may not exceed
the main model's tier, the main session must sit at or above the highest tier
any subagent needs. Since the main session is low-volume, this is cheap to do -
but it is the opposite of "put the cheapest model in the orchestrator."

| Role | Primary | Rate | Per-cycle arithmetic |
|:--|:--|:--|:--|
| **Main** | GPT-5.6 Luna | $1.00/$6.00 | 15k in, 2k out: (15 x 1.00 + 2 x 6.00)/1000 = **$0.027** |
| **Planner** | GPT-5.6 Luna | $1.00/$6.00 | 20k in, 5k out: (20 x 1.00 + 5 x 6.00)/1000 = **$0.050** |
| **Coder** | MAI-Code-1-Flash | $0.75/$4.50 | 50k in, 20k out = $0.1275/attempt x 1.4 = **$0.179** |
| | | | **Total ~$0.256/cycle** |

Main and planner share a model deliberately: the planner is the most expensive
thing the main session needs to permit, so setting main to the planner's tier
costs nothing extra and keeps the cap satisfied. MAI sits below both, so it is
legal as a subagent.

**Against the original stack.** As specified it would total $0.276/cycle if it
worked. Under the cap it collapses to everything running on GPT-5 mini at
**$0.096/cycle** - 65% cheaper and not the framework you designed.

**Tiebreakers where cost is within ~20%:**

- **Coder: MAI-Code-1-Flash vs GPT-5.4 mini is a pure capability call** - the
  rates are *identical* at $0.75/$4.50. Tiebreaker is tool-call reliability in
  agentic loops, where MAI's harness training is the only differentiating
  evidence available. Take MAI, but you are paying nothing for the privilege
  of switching if it disappoints.
- **Planner: Luna ($0.050) vs Sonnet 5 ($0.090)** is an 80% gap, not a
  tiebreaker. Luna wins on cost and on promo risk. It loses on the one thing
  that matters most for this role, reasoning quality, which I could not verify
  (see Caveats).
- **Main: Luna ($0.027) vs GPT-5.4 ($0.0675)** is a $0.04/cycle difference to
  buy a **much higher ceiling**, letting you escalate the coder to
  GPT-5.3-Codex ($1.75/$14.00) on a third attempt. Worth it if escalation is
  part of the design; skip it otherwise.

At $0.256/cycle: Copilot Pro (1,500 credits = $15) buys ~58 cycles/month,
Pro+ (7,000 = $70) buys ~273.

## Q3 - Fallback chains

**Structural warning first.** Because of the cap, **a subagent cannot fall back
*upward* without also raising the main model.** Any escalation hop below marked
"+ raise main" requires changing two files, not one. The array syntax does not
help here: it resolves *availability*, and the cost-tier violation resolves to
the main model regardless of what else is in the array.

| Role | Primary | Fallback 1 | Trigger | Fallback 2 | Trigger |
|:--|:--|:--|:--|:--|:--|
| **Main** | GPT-5.6 Luna $1.00/$6.00 | Gemini 3.6 Flash $1.50/$7.50 | Luna absent from picker or org-blocked. Raises the ceiling, so subagents stay legal. | GPT-5.4 $2.50/$15.00 | Both blocked, or you need headroom to escalate the coder. |
| **Planner** | GPT-5.6 Luna $1.00/$6.00 | GPT-5.4 mini $0.75/$4.50 | Luna missing, or credit pressure. 25% cheaper, weaker reasoning. | GPT-5 mini $0.25/$2.00 | Hard budget cap. Expect plan quality to drop sharply. |
| | | *escalation:* Claude Sonnet 5 $2.00/$10.00 **+ raise main** | Plans repeatedly sending the coder to 3 attempts. Re-evaluate after 31 Aug. | | |
| **Coder** | MAI-Code-1-Flash $0.75/$4.50 | GPT-5.4 mini $0.75/$4.50 | MAI burning all 3 attempts routinely, or Plan-mode looping. Identical price, so this is a capability swap, not a cost hop - flagged because you asked for real hops. | GPT-5 mini $0.25/$2.00 | Credit pressure. 3x cheaper input, 2.25x cheaper output. |
| | | *escalation:* GPT-5.3-Codex $1.75/$14.00 **+ raise main to $2.50 tier** | Prototype complexity outgrows flash-class models. Output at $14.00 makes this expensive fast. | | |

Preview-pull trigger: **Gemini 3 Flash and Gemini 3.1 Pro appear nowhere above
by design.** Both are public preview, and you named preview-pull as a trigger
you care about. Gemini 3.6 Flash is the GA substitute at every point.

### Does the array syntax give you this for free?

**Partly, and less than the original implied.** The documented behaviour is
*"tries each model in order until an available one is found"* - genuine
fallback, but keyed on **availability only**. It covers two of your five
triggers:

| Your trigger | Array handles it? |
|:--|:--|
| Model not in picker | **Yes** |
| Blocked by org policy | **Yes**, if policy makes it unavailable rather than erroring |
| Preview pulled | **Yes**, once it stops resolving |
| Promo expired, no longer cost-competitive | **No.** Still available, so the array never advances. |
| Underperforming in the role | **No.** No quality signal exists. |

For the last two, escalation must be manual: edit the `.agent.md`, or keep two
agent files and invoke the other. There is no automatic quality-based routing.

Example of the verified syntax:

```yaml
---
name: coder
description: Implements the plan, writes tests, verifies.
target: vscode
model: ['MAI-Code-1-Flash (copilot)', 'GPT-5.4 mini (copilot)']
tools: ['edit', 'search', 'runCommands', 'runTests']
---
```

## Q4 - Attacking the cost model

**The worked example is arithmetically correct.** All three check out:
MAI $0.0375 + $0.09 = **$0.1275**; GPT-5.3-Codex $0.0875 + $0.28 = **$0.3675**;
Opus 5 $0.25 + $0.50 = **$0.75**.

**The assumptions underneath are where it goes wrong.**

**50k in / 20k out per coder attempt is wrong-shaped for greenfield.** 20k output
is roughly 1,500 lines of code in a single attempt, which does not happen in a
small prototype; a realistic attempt writes 200-400 lines. The figure is only
defensible because **reasoning tokens bill as output**, and on a reasoning model
they can dwarf the code. Meanwhile 50k input is too *high* for attempt 1 against
an empty repo. My estimates:

| | Attempt 1 | Attempts 2-3 |
|:--|:--|:--|
| Input | 15-25k (empty repo, plan only) | 40-60k (accumulated context, test output) |
| Output | 6-10k (code + reasoning) | 4-8k (smaller diffs, more reasoning) |

The practical consequence: **reasoning effort is a bigger cost lever than model
choice for the coder**, and it went unmentioned. Halving reasoning effort can
beat switching model tier.

**1.4 average attempts is plausible, possibly optimistic.** Greenfield has no
existing behaviour to regress, so first-attempt success should beat large-repo
work. 1.3-1.6 is a fair band.

**C1 holds and does not change the ranking** - see the verdict table. The two
roster outliers are both models you cannot access.

**Does caching shift the bottleneck off the coder? No - it concentrates it
there.** With 90% of coder input cached:

| | Uncached | 90% cached |
|:--|--:|--:|
| Coder input | $0.0375 | $0.0071 |
| Coder output | $0.0900 | $0.0900 |
| Coder/attempt | $0.1275 | $0.0971 |
| Output share of coder cost | 71% | **93%** |
| Coder share of cycle | 65% | **68%** |

Caching attacks input, the coder's spend is output, so caching makes the coder
*more* dominant, not less. **C2 survives aggressive caching and is strengthened
by it.**

**C4's break-even, which nobody computed.** Planner spread runs $0.010
(GPT-5.4 nano) to $0.100 (Gemini 3.1 Pro) per cycle - a 10x range but only
$0.09 in absolute terms. What a bad plan costs depends entirely on whether it
means one extra attempt or a full escalation:

| Bad-plan cost | Upgrade nano to Luna (+$0.04) | Upgrade nano to Sonnet 5 (+$0.08) |
|:--|:--|:--|
| One extra coder attempt ($0.18) | breaks even at **22 pts** better plan rate | **44 pts** |
| Full escalation: 3 attempts + re-plan + re-run ($0.65) | breaks even at **6 pts** | **12 pts** |

So C4 is right, but only under the escalation case, and the prior assistant did
not distinguish them. A 6-12 point improvement in plan quality is very
plausible; a 44 point one is not. **Buy a better planner than nano; do not
assume the most expensive planner pays for itself.**

**C3, restated correctly.** The break-even for GPT-5.4 nano against MAI is
$0.1275 / $0.035 = **3.6 attempts**, above your 3-attempt cap. Inside one cycle
the cheap coder *cannot* lose on token cost. Two caveats that rescue the
conclusion: MAI's claimed 60% token efficiency narrows the gap to near parity
(nano at 2.5 attempts = $0.0875, MAI at 1.2 attempts with 8k output = $0.088),
and a coder that exhausts its attempts produces **no working code**, which no
per-token comparison prices.

## Q5 - Copilot mechanics, verified

**Frontmatter fields** ([VS Code reference](https://code.visualstudio.com/docs/agent-customization/custom-agents),
[GitHub reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration)):

| Field | Type | Notes |
|:--|:--|:--|
| `description` | string | **Required.** |
| `name` | string | Defaults to filename. |
| `model` | string **or array** | Array = ordered availability fallback. |
| `tools` | list or comma-separated string | Omit edit tools to make an agent read-only (C11). |
| `target` | `vscode` \| `github-copilot` | Defaults to both. |
| `agents` | list | Which subagents this agent may call. `[]` forbids all. |
| `disable-model-invocation` | boolean | Prevents being invoked as a subagent. |
| `user-invocable` | boolean | Whether it appears in the agents dropdown. |
| `argument-hint`, `handoffs`, `hooks`, `mcp-servers`, `metadata` | | Also documented. |

**Model ID strings - the important correction.** The IDs are **picker display
names**, optionally with a ` (copilot)` vendor suffix and including `(Preview)`
where the model is preview. Verbatim from the docs:

```
Claude Opus 4.5
GPT-5.2
GPT-5 (copilot)
Claude Sonnet 4.5 (copilot)
model: ['Claude Haiku 4.5 (copilot)', 'Gemini 3 Flash (Preview) (copilot)']
```

The inferred `claude-sonnet-4.5` kebab format appears in **no** official
example. One community respondent claimed API-style IDs (`claude-3-opus-20240229`)
are required; that contradicts the documentation, cites long-obsolete model
names, and I would disregard it.

**Verify by credits, not by label.** Two documented traps:

1. An unresolvable model name **silently falls back** to the parent model. No
   error, no warning.
2. The hover tooltip shows the **parent** model even when the subagent's model
   *is* being applied ([discussion #191450](https://github.com/orgs/community/discussions/191450)),
   so the label is not evidence either way.

The reliable check is the per-subagent AI credits readout, cross-referenced
against the arithmetic above. Run one known task and see which rate the charge
matches.

**Subagent model priority** is documented as: explicit `runSubagent` parameter,
then the agent's `model` frontmatter, then the parent model - subject
throughout to the cost-tier cap.

## Caveats and unverified items

Flagged rather than filled, as requested.

- `UNVERIFIED` - **What Claude Sonnet 5 costs after 31 Aug 2026.** Not
  documented on the pricing page, the supported-models page, or the GA
  changelog, which says only that it is "billed at provider list pricing."
  Every other Anthropic Sonnet sits at $3.00/$15.00, but that is my inference.
- `UNVERIFIED` - **The exact semantics of "cost tier."** The docs use the phrase
  without defining it. It may compare per-token rates directly or bucket models
  into discrete tiers. The practical rule is the same either way: never make a
  subagent pricier than the main. Test it before trusting a stack that sits
  close to a boundary.
- `UNVERIFIED` - **GPT-5.6 Luna's reasoning quality.** I recommend it on price,
  GA status, and absence of promo risk. I found no benchmark or capability
  evidence for it in the planner role, and its price implies mid-tier rather
  than frontier. **A/B it against Sonnet 5 before the promo expires**, while
  comparing them is still cheap.
- `UNVERIFIED` - **Whether pinning a model forfeits the 10% auto-selection
  discount.** The discount is documented verbatim for auto selection; the docs
  do not say what happens when you pin. If it is forfeited, every figure here
  is ~10% optimistic relative to running on Auto.
- `UNVERIFIED` - **Whether subagent model pinning currently works at all.**
  [Issue #291883](https://github.com/microsoft/vscode/issues/291883) (Jan 2026,
  now closed) reported the field simply ignored; the closure notes no fix.
  [Issue #292452](https://github.com/microsoft/vscode/issues/292452) (Feb 2026)
  reported the billing bypass and was still open at last check. The cost-tier
  cap reads like the response to it. Treat pinning as working-but-verify.
- `UNVERIFIED` - **MAI's "60% fewer tokens."** Vendor benchmark, unreproduced.
  It is load-bearing for MAI's economics: without it, GPT-5 mini at
  $0.25/$2.00 is the better-value coder.
- Not researched, per your exclusions: BYOK, Copilot CLI/SDK/cloud agent,
  non-Copilot tools, the legacy multiplier scheme, agent prompt content.

## Sources

- [Models and pricing for GitHub Copilot](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
- [Supported AI models in GitHub Copilot](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [Custom agents configuration (GitHub)](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [Subagents in Visual Studio Code](https://code.visualstudio.com/docs/copilot/agents/subagents)
- [Usage-based billing for individuals](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals)
- [About Copilot auto model selection](https://docs.github.com/copilot/concepts/auto-model-selection)
- [Creating custom agents for Copilot cloud agent](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents)
- [Introducing MAI-Code-1-Flash](https://microsoft.ai/news/introducingmai-code-1-flash/)
- [Claude Sonnet 5 GA changelog](https://github.blog/changelog/2026-06-30-claude-sonnet-5-is-generally-available-for-github-copilot/)
- [Community #197306 - MAI-Code-1-Flash GA thread](https://github.com/orgs/community/discussions/197306)
- [Community #191450 - subagent model falls back to parent](https://github.com/orgs/community/discussions/191450)
- [microsoft/vscode#291883 - model field not respected](https://github.com/microsoft/vscode/issues/291883)
- [microsoft/vscode#292452 - subagent billing bypass](https://github.com/microsoft/vscode/issues/292452)
- [github/copilot-cli#2133 - array syntax incompatibility](https://github.com/github/copilot-cli/issues/2133)
