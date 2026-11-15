# Editorial plan for a more cohesive book

The book can read as a developing argument while keeping each chapter usable on its own. A reader going in order should see how one technical decision raises the next question. A reader arriving from the contents should have enough context to follow the chapter or worked example.

## What the initial read suggests

| Location | What to verify |
| --- | --- |
| Introduction | The opening explains where the author's positions came from and why science and engineering decisions interact. The next paragraph moves to chapter format. Check whether the introduction gives readers a reason to follow the chapters in sequence before it explains how they are organized. |
| Chapter 1, first worked example | The 10-inspection limit appears in the operational table. Check whether its role in choosing between the models is clear before the reader reaches the classification results. The two comparisons can stay technically intact while the decision guiding them becomes clear earlier. |
| Chapter 1, section handoffs | Model B puts eight likely failures on the inspection list. The next section asks whether that beats the current policy, and the third asks whether the gain justifies the cost. The numbers already carry through. Check whether the generic section openings make those steps feel like fresh starts. |
| Chapter 2, irrigation comparison | The final example identifies the sunlight-by-watering observations missing from the historical records and uses that gap to motivate a new experiment. Keep that connection and test whether putting the specific gap earlier gives the reader a clearer reason to follow the experiment. |
| Conclusion | The text moves from writing the book, to checking whether an approach's assumptions hold in a new setting, to disagreement and independent judgment. Check whether the reader can trace that final invitation back to the introduction's emphasis on linked scientific and engineering decisions. |

These are preliminary observations from the main manuscript. The reader's report gives us hypotheses to test across all 12 chapters.

## 1. Trace the argument through the book

Read the introduction, all 12 chapters, and the conclusion in order. Write one sentence per chapter answering what judgment the chapter helps the reader make. At each chapter boundary, record which question carries forward, which question the next chapter adds, and whether the relationship is apparent in the manuscript.

Test a few natural connections first. Chapter 1 treats failure prevention as an assumption when translating inspection results into business outcomes. Chapter 2 asks what evidence supports the effect of an action. Chapter 5 returns to that problem when it tests whether a calling rule improves clinic outcomes. Chapter 8 asks whether results survive a change to one component, while Chapters 9–11 address reliability, feasibility, and change after deployment. Chapter 12 brings the focus back to how teams examine and revisit decisions. Verify each connection against the text before proposing a reference or a change.

Give each paragraph of the introduction and conclusion a job. Check whether each paragraph follows from the one before it and whether the conclusion returns to a question the introduction gives readers reason to care about. Test a paragraph move or a short connection before proposing broader changes.

## 2. Read each section and worked example in sequence

At each section boundary, ask what the reader just learned and what remains undecided. At each worked example, record the decision, the constraint or evidence that matters, what the team learns, and how the result changes the decision. Where an example continues, check that the reader can tell what still holds, what changed, and why the team is taking the next step. Mark a new hypothetical scenario clearly when it reuses a setting with different assumptions.

After the sequential read, enter selected chapters and sections from the contents. Check whether the opening gives a reader who skipped earlier material enough local context. Pay particular attention to tables. Before reading one, a reader should be able to say what is being compared and why. After reading it, they should be able to say what the evidence implies and which assumptions that inference depends on.

Use Chapter 1 as the pilot. When the proposed revamp is available, compare it with the manuscript at each point of confusion. Record the specific reading problem it solves and test the smallest equivalent change. Use Chapter 2 as a second pilot for examples that share a setting and a question across sections.

## 3. Propose the smallest edits the findings justify

For each material finding, record the chapter and section, the reader's likely question, the evidence in the text, and the smallest proposed edit. Prefer moving an existing sentence forward, naming the result that carries over, or replacing a generic transition with the question the team now needs to answer. For example, test whether recalling that Model B finds eight likely failures gives the reader a clearer reason to ask what the current policy achieves. Suggest a cross-reference only when it helps the reader recover a specific earlier idea.

Bring back a short findings list and before-and-after excerpts for the introduction, conclusion, and the Chapter 1 and 2 pilots. Prioritize moments where a reader loses the decision or misses why it matters. Preserve the author's positions, examples, figures, assumptions, terminology, and wording wherever the prose is doing its job. Flag any finding that would require a substantive change for a separate editorial decision.

## 4. Verify the proposed remedy before expanding it

Read the pilot excerpts in order and again from their section headings. Ask a fresh reader, if available, to explain the decision before each worked example, what changed since the previous example, and why the next question follows. Compare their answers with the original excerpts. Check the rendered reading order if the audit points to a break around a table or page boundary. Use the pilot findings to propose chapter-by-chapter edits for review.

## Chapter 2 pilot informed by reader feedback

Keep the existing progression from prediction to historical evidence to an experiment and then return to the inspection question from the opening. The greenhouse setting can carry the reader through these steps as one investigation. Make the change in evidence explicit at each step.

| Passage | Change to test | What the manuscript already provides |
| --- | --- | --- |
| Deciding whether to give extra water | Keep the low-yield prediction and the staff's consideration of extra water up front. Establish the two possible outcomes for that same section and why the team needs to compare them before revealing 3 kg and 1 kg. Test moving the existing potential-outcomes explanation ahead of the figures. | The prediction and decision already precede the numbers, and the text explains the counterfactual. Treat the two yields as hypothetical potential outcomes. The example needs neither a completed intervention nor a new explanation for crop damage. |
| Comparing watered and unwatered sections | Set up sunlight as both a basis for the staff's choice and a factor in yield before the table. State before the table that bold values are observed under the historical policy and the other values are hypothetical alternatives. Test writing the observed difference as $8 - 3 = 5$ kg alongside the within-sunlight differences of $-2$ kg. Introduce association and confounding as the reader sees why the two comparisons differ. | The table and following paragraphs already identify both roles of sunlight and explain what bold means. Move or condense that material. Let the historical example focus on how watering was assigned and introduce random assignment in the experiment. |
| Designing an irrigation comparison | Carry forward which sections received which action and the resulting gap in the records. Then explain that chance decides which of the 24 sections receives each watering routine and that the two groups can differ in a particular assignment. Test a short connection between the earlier effect for one section and the estimated average effect from the difference in group means. | The example already states the missing comparisons, calculates $4.5 - 6.5 = -2$ kg per section, and discusses uncertainty and individual effects. Preserve those qualifications. The repeated numerical result comes from a different comparison in a new hypothetical growing period. |
| Returning to inspections | Replace the abrupt return with a sentence that carries over the causal question from irrigation. Here the action is adopting a model-assisted inspection workflow, and timely detection and yield are distinct outcomes. If the unit of assignment needs explanation, test a short conditional rationale tied to a shared workflow or inspection capacity within each greenhouse. | The current ending already distinguishes timely detection from yield and attributes the estimated effect to the workflow change. Preserve that scope, including the use of the current workflow as the comparison. |

If readers still stumble over matching and weighting, test a short explanation of how each helps construct a comparison and retain the warning about missing comparisons and unmeasured confounding. A causal diagram, a terminology summary table, and formal average-effect notation can stay optional. Revisit them only if the shorter pilot leaves a specific point unclear.

Check the pilot by asking three questions after each relevant passage. What decision is the team facing? What can it infer from the information it has? What evidence would it need next? A reader should be able to distinguish the hypothetical individual effects, the misleading historical association, and the experimentally estimated average effect.
