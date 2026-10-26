# Free hosting research — for 1–7 hours/day, long term (checked 2026-10-26)

## Honest headline
**No free provider guarantees 6–7 hours/day, every day, forever, for a 24 GB-class
model at $0.** Anyone promising that is selling a trial, a credit that runs out,
or a quota workaround. The realistic free plan below gets you to ~4–5 hours/day
on average, with Colab as an unreliable extra on some days. 6–7 hours/day is
possible on good weeks, not guaranteed.

## What the model needs
Q4_K_M = 16.8 GB weights, ~18.6 GB total at 8k context. So a host must offer
either one ≥24 GB GPU, or two 16 GB GPUs with tensor-split, or a single 16 GB
GPU with partial CPU offload (slower).

## Comparison (all $0, legitimate single-account use)

| Provider | GPU you can actually get free | Recurring free amount | Hours/day math | Long-term? | Verdict for this model |
|---|---|---|---|---|---|
| **Kaggle Notebooks — RECOMMENDED, primary** | P100 16 GB, or **T4 x2 (2×16 GB)** | ~30 GPU hours/week, resets weekly, session ~12 h | 30 ÷ 7 = **~4.3 h/day** | Yes — recurring weekly quota, not a trial, as long as the account stays in good standing (phone verification required) | **Best fit.** T4 x2 + tensor-split is the only recurring free path that holds exact Q4_K_M fully on GPU. Quota is shown in your own Kaggle account settings — trust that number over any blog. |
| Google Colab (free) | T4 ~15 GB usable, type not guaranteed | No published number, dynamic, idle timeouts, ~12 h max session | Unpredictable — can be 0 on a bad day (quota exhaustion observed for ~18 h in Oct 2026) | Yes, but unreliable | Backup only. Single T4 needs partial offload (NGL≈50). Never plan a deadline around it. |
| Modal (Starter) | L4 24 GB, A10G 24 GB | $30/month credit, recurring monthly | L4 at ~$0.80/h = 37.5 h/month = **~1.25 h/day**; A10G at ~$1.10/h = 27 h/month = **~0.9 h/day** | Yes, monthly credit, but small | Useful **supplement**, not a replacement. Add it after Kaggle quota runs out, for ~1 extra hour/day. Serverless, so you pay only for active seconds — do not idle. |
| Lightning AI (free) | T4 / L4 class Studios, 4 h restarts | **One-time** starter grant (reported ~30 credits in Sep 2026, expiring after 12 months), **not a monthly refill anymore** | One-time only | No — it runs out | Do NOT plan long-term use on it. Older articles claiming "15 credits/month forever" are outdated. |
| Hugging Face Spaces ZeroGPU | RTX PRO 6000 (shared, 48 GB half-GPU) | 5 minutes/day free | 0.08 h/day | Yes, but useless for this | Demo only. Cannot host a 6-hour chat session. |
| Paperspace Gradient (free) | Quadro M4000 8 GB | No stated expiry, but 8 GB only | — | — | Cannot fit Q4_K_M (or even IQ2_M comfortably). Exclude. |
| SageMaker Studio Lab | T4 16 GB | Was 4 h/session, ~8 h/day | — | **Closed to new users** | Exclude. |
| Google Cloud / AWS / Azure trials ($300 etc.) | Any GPU, if you pay the difference | One-time, ~90 days | — | No — trial ends | Exclude for "onek somoy" (long time) use. |
| Oracle Always Free | No GPU (CPU only) | Forever, but CPU | — | — | CPU inference for a 27B model is far too slow for chat. Exclude. |

## The combined, legitimate plan (no quota evasion)
1. **Kaggle first, every week:** use its ~30 h for the main 4+ h/day.
2. **Modal second:** spend its $30/month L4 credit for ~1 h/day extra.
   Combined: ~30×4.33 + 37.5 ≈ 167 h/month ≈ **5.5 h/day average**.
3. **Colab third, opportunistically:** on days Colab actually gives a GPU,
   you may reach 6–7 h that day. On days it does not, you do not.
4. **Never** create extra Kaggle/Colab accounts to multiply quotas — providers
   treat that as abuse, and one banned account loses everything.

## Why "uptime bhalo" needs redefining here
None of these is a 24/7 server. "Good uptime" here means: **when you open it
for your 1–2 hour session, it starts reliably and stays up for that session.**
Kaggle's 12-hour session cap and weekly quota fit that definition; a
"server" that is always on but throttled, queued, or banned does not.

## What still needs your manual run
The model cannot be hosted by Muse alone — Kaggle/Colab/Modal all need YOUR
login, phone verification, and a Run click on your phone. The repo already
contains the Kaggle notebook, the gateway, and now a Settings UI (provider
preset, quant, context, temperature, top-p, max tokens, system prompt, direct
mode, and a quota planner). After you run the notebook, paste the tunnel URL
into Settings and press Reconnect. Until that run happens, "hosted" is a plan,
not a fact.
