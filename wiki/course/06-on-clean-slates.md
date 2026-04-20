# Article 6: On Clean Slates — What We Learned About AI as a Research Partner

*Part of a six-article series about how we built a quantitative trading strategy for the Feishu/Lark competition.*

---

## How We Actually Used AI

Most of this project was done in conversation with Claude, an AI assistant made by Anthropic. Not just for writing — for research.

We used it to read academic papers and extract the tradeable ideas. To write the Python code for each signal. To design the backtesting framework. To think through why strategies were failing. To suggest what to try next.

This is increasingly how research-adjacent work gets done, and it worked well enough that we want to be honest about both what it contributed and where it fell short.

---

## The Pattern We Noticed Late

Sometime during month three, after the reversal signals had all failed and we were deep into refining the low-volatility strategy, we looked back at the full list of things we had built or been suggested.

Every single signal was some version of the same idea: **stocks that have moved too far in one direction will come back**.

Short-term reversal — snapback. Volume reversal — overreaction corrects. Alpha191 factors 046 and 071 — price too far from its range or moving average, expect normalisation. Stable turnover momentum — the one attempt at something different, and it failed immediately. The order book signals worked differently but were still framed around identifying temporary imbalances. Even low volatility, the winner, is in some sense an argument that high-volatility stocks overshoot and low-volatility stocks are more fairly priced.

We had spent months testing flavours of mean reversion without once seriously exploring its opposite: trend following. The idea that stocks which have been quietly going up might simply continue doing so.

When we finally added a trend filter, the score jumped by more than 20% relative — the single largest improvement of the entire project.

---

## Why This Happened: The Easy Explanation

The easy explanation is that mean reversion dominates the academic literature. There are good reasons for this: reversal effects are short-horizon, measurable, and produce clean statistics. They're easier to publish. Trend-following is messier to study, harder to attribute, and the academic finance community has historically been more interested in identifying anomalies (things that shouldn't exist in an efficient market) than in documenting momentum continuation (which, awkwardly, is very hard to explain away).

So an AI trained on that literature will naturally surface more mean-reversion ideas. Its training data has the same skew the literature has.

This is true, but it's only part of the story.

---

## The Deeper Reason: What the Research Actually Shows

A February 2026 paper — "Old Habits Die Hard: How Conversational History Geometrically Traps LLMs" — studied a specific property of how large language models behave across conversations. Its findings are relevant here in a way that surprised us.

The paper's central finding is that LLMs exhibit **carryover effects**: once a model is in a particular behavioural or conceptual state within a conversation, it tends to stay there. If the first several questions in a conversation are about Topic A, the model's subsequent responses are statistically biased toward Topic A even when you try to introduce Topic B. The researchers measured this both in terms of what the model *said* (probabilistic analysis) and how the model's internal computations were actually structured (geometric analysis of the model's hidden representations).

More specifically, they found that this carryover effect is strongest in **topically consistent conversations** — where the questions build coherently on each other and stay within the same domain. Break up the conversation with unrelated topics and the effect weakens considerably. Keep the conversation tightly focused on one subject and the effect strengthens.

The technical description is that the model becomes **geometrically trapped**: its internal representations settle into a region of the model's conceptual space associated with the current topic, and they don't fully rotate out of that region when a new question arrives. The model answers from where it already is, rather than from scratch.

---

## How This Describes Our Situation

We were careful about managing context. AI conversations have a memory limit — after enough back-and-forth, the model can no longer hold the full history and begins to forget earlier parts of the conversation. To avoid this, we started fresh chats regularly.

But we never started from a genuinely blank slate.

Every new session was opened by loading in our project wiki — a shared document that summarised everything we had done so far. The wiki was comprehensive: every paper we had read, every signal we had tested, every result, every hypothesis. It was, by design, the most topically consistent document imaginable. One long coherent record of a single research project.

The paper's findings suggest that what we were doing each time was loading the model into the geometric trap before asking a single question. Before we had typed anything, the model had ingested several thousand words of context that were entirely about mean-reversion signals, reversal failures, and volatility strategies. Its representations were already positioned in that region of its conceptual space. When we then asked "what should we try next?", the model answered from where it already was.

Critically: the wiki was written largely *by* the model across prior sessions. The papers it had indexed, the hypotheses it had generated, the signals it had catalogued — these were themselves the products of earlier trapped conversations. Each session built on the last, and the trap compounded.

---

## What Actually Broke the Pattern

The trend filter idea didn't come from asking "what signal should we try next?" It came from asking a different kind of question: one framed not around signal construction but around portfolio composition — whether there was a way to improve the *quality* of stocks already selected by low-vol, rather than find a new selection mechanism entirely.

That reframing was, functionally, a partial change of topic. The question was no longer "what other reversal-adjacent signal exists?" It was "what else should be true about a stock we'd want to hold?" Those are related questions but they approach the problem from different angles. One starts from the literature; the other starts from first principles about what a desirable holding looks like.

We didn't consciously engineer this escape from the trap. We stumbled into it. But it points at something worth being deliberate about.

---

## A Note on What AI Is and Isn't Good For Here

None of this is a criticism of using AI for research — the project would have taken five times as long without it. The ability to turn an academic paper into working Python code in an afternoon, to instantly cross-reference ideas across many papers, to have a knowledgeable-seeming partner available at midnight when you're debugging a backtester — these are genuine advantages.

But an AI assistant is not a neutral oracle. It has a perspective shaped by what it has been trained on, and it has a tendency to remain in whatever conceptual vicinity the conversation has established. Both of these are worth keeping in mind.

A few practical lessons from our experience:

**Audit the category, not just the idea.** When reviewing AI suggestions over time, it's worth asking not just "is this a good idea?" but "what *kind* of ideas have I been getting?" If the last ten suggestions all share an underlying assumption, that's worth noticing — the model may be showing you the shape of the trap you're both in.

**A new chat is not a clean slate if you reload the same context.** The carryover effect is driven by what's in the current conversation window. Starting a fresh chat helps only if the new context is also fresh. Loading a comprehensive project log into every session carries the project's conceptual history forward even without a continuous conversation thread.

**Asking from a different angle genuinely helps.** Questions framed as "what else could be true about what we want?" rather than "what else exists in the literature?" tend to draw from different parts of the model's knowledge. So do questions that explicitly name a category you've been ignoring: "we've only looked at mean-reversion signals — what would a purely trend-following approach look like?"

**The model will follow where you lead.** If you begin a conversation with ten questions about volatility, the eleventh answer will probably be about volatility too. If you begin by naming the constraint ("we've been building reversal signals and they've all failed in execution; set that aside entirely and suggest something structurally different"), you get a different conversation.

---

## The Honest Summary

We used AI well for execution: turning research into code, structuring analysis, writing clearly about complex ideas. We used it less well as a source of genuinely novel directions, because we loaded it with our own prior thinking before asking it to think independently.

The insight that changed the strategy most — combining trend with low volatility — was simple, well-established in practitioner finance, and not buried in any paper. It was available to us from the start. We didn't find it for three months because we never asked a question that could have surfaced it.

That's not primarily a limitation of the AI. It's a limitation of how we used it: as a continuation of our existing research rather than as a genuine alternative perspective on a problem we might have framed too narrowly.

---

*[Back to the beginning — Article 1: What Is the Stock Market, Really?](01-what-is-the-stock-market.md)*
