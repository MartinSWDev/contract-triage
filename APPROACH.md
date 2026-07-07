# How I'd approach this for real

The prototype here is really just a proof that the mechanism works: a
playbook-driven assistant can triage these contracts, clear the boilerplate on
its own, and hand a lawyer only the parts that actually need a decision, without
inventing anything. It runs on synthetic contracts and a playbook I wrote
myself.

Doing it properly is a different job, and most of it isn't the code. The
pipeline is the easy part. The real work is understanding what the team does all
day, grounding the playbook in their actual decisions, and building something
they'll trust and keep using once I've left. Here's roughly how I'd go about it.

## What I built, and how to run it

Before the plan, here's what's actually in the repo. The working demo:

- A **playbook** (`playbook/playbook.yaml`) of the team's standard positions and
  pre-approved redlines for NDAs and order forms, plus the escalation rules that
  decide what a human has to see.
- Nine **synthetic contracts** (`samples/`, Word and PDF). Some are clean, some
  have deviations the playbook covers, and a couple have deviations it
  deliberately doesn't, to check the tool is honest about its limits.
- The **assistant** (`src/`). It reads a contract, triages it, diffs it against
  the template and playbook, checks every quote it's about to use against the
  real document, and produces a **redlined Word file with tracked changes and
  margin comments**, a triage summary, the flagged deviations, and a draft reply
  to the counterparty.
- An **evaluation** (`eval/REPORT.md`) that scores all nine against
  hand-written answers. On the current run it gets the type and the escalation
  call right on all nine, catches every deviation, invents advice on none of the
  uncovered ones, and puts zero unverified quotes into a redline. The report is
  deliberately sceptical about what those numbers do and don't mean.
- A **desktop app** (`app/`) that wraps all of it: point it at a folder, run the
  contracts, read each result, and generate the scorecard.

To run it:

- **Command line:** `pip install -r requirements.txt`, then
  `python src/run_all.py` to process every sample and `python eval/evaluate.py`
  to score them. Full steps in the [README](README.md).
- **Desktop app:** `cd app/src-tauri && cargo tauri dev`. Prerequisites and
  steps in [app/README.md](app/README.md).

And the plan itself, one line each:

- Sit with the team first and find the repetitive, low-risk work worth
  automating.
- Rebuild the playbook from their real past decisions, not my guesses.
- Add RAG over those decisions for precedent, and keep the positions in the
  editable playbook rather than in model weights.
- Keep a quick human pass on every contract, and feed those accept/edit/overrule
  actions back into the playbook.
- Roll out in shadow mode first, watch recall hardest, and keep the failures
  visible.

The rest of this document is that plan in full.

## Start with the team

I'd hold off writing any code initially. First I'd sit with the legal team and
watch them review contracts. The prototype assumes NDAs and order forms are the
repetitive 80%, but that's a guess. The team knows which contract types clog the
queue and which clauses they end up rewriting again and again, so I'd get them to
rank that for me.

The more important conversation is about accuracy. For each clause, where are
they happy for a machine to propose an edit, where should it propose but never
decide, and where should it not go anywhere near? That line is theirs to draw,
not mine. It's also what earns their trust later, because the tool is only ever
doing what they told it to.

By the end of this I'd want a shortlist of the contract-type-and-clause
combinations worth automating first (high volume, low risk) and a shared sense of
where the danger is.

## Use their old decisions as the data

The team has already made these calls thousands of times. Every past contract,
the draft that came in, the redline they sent back, the signed version, the email
chain, is a worked example of "they asked for X, we did Y." That's the data.

I'd pull an anonymised set and use it to rebuild the playbook from what the team
actually does rather than from my assumptions. What position did they really take
on a liability cap? What did they give up when pushed? What got kicked upstairs?
This also tends to surface disagreements, different lawyers doing different
things, positions that have drifted over the years, which is worth sorting out
anyway. And it gives me a proper evaluation set built from real cases instead of
ones I made up.

## Playbook, RAG, and maybe fine-tuning later

There are a few ways to get the team's knowledge into the system and they aren't
interchangeable. Keeping them apart is the point.

The playbook holds the actual positions, and it stays as plain, readable rules a
lawyer can open and edit. That's deliberate. If the tool takes a wrong position I
want fixing it to be a one-line change someone non-technical can make, not a
retraining job.

RAG over the old decisions is where I'd get the most value first. When the
assistant hits a clause it can pull up the closest past examples and show the
lawyer the last handful of times they saw, say, an uncapped liability clause and
what they did each time. It backs the playbook rule with real precedent, and it's
honest about it, the human still decides.

Fine-tuning I'd leave for later, if at all. It's expensive, it's a black box, and
it bakes the team's positions into model weights where nobody can see or edit
them, which is the opposite of what a legal team wants. A good playbook plus
retrieval beats it at this volume. Feeding new decisions back in, which is the
other half of the idea, is really the feedback loop below.

## Keep a human in the loop, and let that loop improve it

Every contract still gets looked at by a person. The difference is they're
reviewing a marked-up draft instead of a blank one, so it's quick. For each
flagged clause they accept the suggestion, tweak it, or overrule it.

That review is where the value is, and it doubles as the training signal. An
accept confirms a rule is working. An edit means the wording needs tuning. An
overrule ("no, escalate this one") usually means an escalation rule is off. And
when someone resolves something the tool flagged as not covered, that's a
candidate for a new rule. A regular review, weekly at first and then less often,
turns all of that into playbook edits.

This is exactly how you'd catch the kind of mistake the prototype's own
evaluation threw up. The assistant under-escalated a clause because one of the
escalation rules was worded ambiguously. In a live system that shows up as a
lawyer overruling the suggestion, which flags the rule for a quick fix. So the
tool gets better the more it's used, and every improvement is a readable edit to
a file the team owns rather than a mystery retrain.

Alongside that I'd run a slow trust ratchet. Everything starts under full human
review. Rules that consistently get accepted without changes can move to a
lighter touch. Sending anything automatically stays off the table.

## Roll it out slowly and measure the honest things

I'd start in shadow mode: the tool runs on real contracts next to the humans
without changing anyone's workflow, and I just measure how often it agrees with
them. That's the real evaluation. Then lawyers start working from the redline and
I track how often they accept each rule's suggestion. Then the rules with a good
track record can get lighter review.

The number I care about most is recall, whether it ever misses a deviation,
because a miss is more dangerous than a bad suggestion. A lawyer glancing at a
"looks clean" verdict can wave it through. So the tool never says "done," it
always shows what it cleared and why, and recall stays the headline metric.
Hallucinated advice has to stay at zero. After that it's accept rate per rule,
queue turnaround, and time saved. Failures stay visible.

Sensitive contracts would run on a self-hosted or VPC model rather than a cloud
API. The prototype already isolates the whole model layer to a single file, so
that's a small change. Training data stays anonymised and on our own
infrastructure.

For handover, the playbook is owned by the team as a plain file, the evaluation
harness doubles as the regression test after any change, and real failures get
added to the test set over time so coverage grows on its own.

## What I'd be worried about

A missed deviation is worse than a wrong suggestion, for the rubber-stamp reason
above. So the tool has to stay visibly unfinished, and recall is the number I'd
watch hardest.

RAG can pull up a clause that looks similar but is legally different, so
precedent is only ever shown to the human as context, never acted on by itself.

The old decisions won't be consistent. Mining them will expose disagreements and
drift, and someone actually has to resolve those. That's real work, but it needs
doing regardless of the tool.

And I'd keep the legal positions out of the model weights and in the playbook
where they can be seen and changed. If a position is wrong, fixing it should be a
one-line edit, not an engineering project.
