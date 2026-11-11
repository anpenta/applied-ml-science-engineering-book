# Technical Judgment in Teams

Consider a technical team developing a model to help music teachers decide which passages their students should rehearse. A scientist evaluates the model, an engineer reviews its implementation, and a teacher examines its recommendations. What might each of them notice that the others overlook?

To make sound decisions as a team, we need to understand how our work affects the rest of the system, challenge assumptions that could have important consequences, and document the reasoning behind our decisions so others can revisit them.

## Understand the whole system

Scientific and engineering decisions often depend on assumptions made by people with different expertise. Understanding how the different parts of a system work together helps us recognize when to involve others and how our decisions may affect their work.

The example below shows how bringing different perspectives together can reveal a problem that separate reviews might miss.

> **Worked example: Reviewing what a rehearsal tool measures**
>
> A technical team develops a tool that helps music teachers identify which passages their students should rehearse. The model identifies notes in a recording of a student's performance, and the system compares their timing with a reference recording to identify potential mistakes.
>
> Three people review the tool from different perspectives.
>
> | Reviewer | Question raised |
> | --- | --- |
> | Scientist | Does the evaluation measure how accurately the model identifies the notes and their timing? |
> | Engineer | Does the system correctly align the student's recording with the reference before comparing them? |
> | Teacher | What happens when a student intentionally slows down during a passage? |
>
> The teacher's question reveals an important assumption: that differences from the reference timing always indicate mistakes. However, some musical passages are intended to slow down or speed up. The tool could therefore identify a mistake even when the model's predictions and the system's calculations are correct.
>
> The team decides to limit the first version to exercises intended to follow a fixed tempo. The teacher identifies suitable exercises, the scientist evaluates the model on those exercises, and the engineer ensures that the tool does not provide timing recommendations for unsupported passages.
>
> The team also documents this limitation so that future versions can consider how to evaluate passages with intentional tempo changes.

As the example above shows, each specialist can evaluate their part of a system correctly while overlooking a problem that affects the system as a whole. Shared understanding helps us identify such problems and bring together the expertise needed to address them.

## Question important decisions

When questioning a decision, we should identify the underlying assumption, examine the evidence supporting it, and consider the consequences if it is wrong. How much effort we spend reviewing the decision should depend on its potential consequences and how easily it can be reversed.

The example below shows how questioning a proposed design can reveal important information that would otherwise be lost.    

> **Worked example: Questioning what the tool should show**
>
> Continuing the rehearsal-tool example, the technical team wants to compare patterns of early and late notes across recordings. To do this, they divide each timing offset by the largest absolute offset in the recording.
>
> Consider two recordings of the same three-note passage. Positive offsets mean that a note was played late.
>
> | Recording | Timing offsets (milliseconds) | Largest absolute offset (milliseconds) | Normalized offsets |
> | --- | --- | ---: | --- |
> | A | 10, 20, 10 | 20 | 0.5, 1, 0.5 |
> | B | 100, 200, 100 | 200 | 0.5, 1, 0.5 |
>
> Both recordings have the same normalized offsets, even though the timing errors in recording B are ten times larger.
>
> A reviewer questions whether showing only the normalized offsets would hide useful information. The team asks a music teacher, who explains that the size of the timing errors also matters when deciding what students should rehearse.
>
> The team therefore decides to show both the normalized offsets and the largest absolute offset. This allows teachers to see both the pattern and the size of the timing errors.
>
> The review helps the team avoid hiding information that matters to the people using the tool.

As the example above shows, questioning a decision can reveal problems that might otherwise go unnoticed. By checking the concern with a teacher, the team can determine whether the decision matters in practice.

We should focus our reviews on decisions that could significantly affect the results or how people use them. Minor choices, such as naming preferences, usually require less attention than decisions that could remove important information.

## Document the reasoning

We should document important decisions so that others can understand and reconsider them later. A short record should explain what was decided, why the decision was made, and what might justify changing it.

The example below shows how documenting the reasoning behind a decision helps a new team member evaluate a proposed change.

> **Worked example: Revisiting the report design**
>
> Continuing the rehearsal-tool example, assume that the technical team documents why it decided to show both normalized offsets and the largest absolute offset.
>
> | Part of the record | What the team writes |
> | --- | --- |
> | Context | Teachers use the report to decide which passages students should rehearse. |
> | Decision | Show both normalized offsets and the largest absolute offset. |
> | Evidence | Recordings A and B have identical normalized offsets, although B's timing errors are ten times larger. A teacher confirmed that both measures are useful. |
> | Alternative considered | Show only normalized offsets, which would hide the size of timing errors. |
> | Limitation | The largest absolute offset reflects only the largest timing error, not the overall performance. |
> | Reason to revisit | Teachers report that the largest absolute offset is not a useful summary of timing errors. |
>
> Later, a new team member suggests removing the largest absolute offset to simplify the report. After reading the record, they understand why it was included and decide not to remove it without checking with teachers.
>
> However, the record also highlights a limitation. A single unusually late note could make the largest absolute offset misleading. The new team member proposes showing the average absolute offset instead.
>
> The team can now compare the two approaches with teachers and decide which better supports their needs. If the team decides to eventually change the report, they update the record to explain the new decision.

As the example above shows, documenting the reasoning behind a decision helps others understand it and evaluate possible improvements without having to start from scratch.

## Further reading

- **Understand the whole system.** The paper explains how dependencies and interactions across a machine learning system can undermine assumptions made about individual components. [David Sculley and colleagues, *Hidden Technical Debt in Machine Learning Systems*](https://research.google/pubs/hidden-technical-debt-in-machine-learning-systems/)
- **Question important decisions.** The guide covers reviewing design and user-facing behavior, including when to examine a demonstration and how to separate substantive concerns from style preferences. [Google, *What to look for in a code review*](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- **Document the reasoning.** The article explains how short decision records preserve context and consequences so future team members can reconsider a choice. [Michael Nygard, *Documenting Architecture Decisions*](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
