# Causal Effects

In the equipment-inspection example, we assumed that inspecting a machine would prevent its failure. But a prediction of failure does not establish what an inspection will achieve. To examine this distinction, imagine that a model predicts which sections of a greenhouse are likely to produce a low yield. Could we use these predictions to decide which sections to inspect? What about which sections to water more?

To answer these questions, we need to understand how to distinguish predictions from causal effects, avoid misleading comparisons, and estimate causal effects.

## Distinguish predictions from causal effects

A prediction of low yield can help us identify greenhouse sections to prioritize for inspection, but it does not tell us whether giving those sections extra water would improve their yield. The latter is a causal question. In fact, whether prioritizing inspections based on predictions improves yield is also a causal question, which we will return to later. For now, let us focus on the action of providing extra water.

**Causal inference** concerns learning about causal effects from data. The action whose effect we study is called the **treatment**, and the quantity it may change is the **outcome**. In this chapter, we use **action** to describe the treatment under study and always specify the alternative we compare it with.

The example below illustrates the difference between predicting an outcome and estimating the effect of an action.

> **Worked example: Deciding whether to give extra water**
>
> Suppose a model predicts that a greenhouse section is likely to produce a low yield under the usual routine. The greenhouse staff considers giving that section extra water, hoping to improve its yield. The prediction identifies a section at risk, but it does not establish that a lack of water is the problem or that additional water would help.
>
> To assess the proposed action, we want to compare the yield of the same section under two alternatives: extra water and the usual routine. Let $Y(1)$ be the yield with extra water and $Y(0)$ the yield under the usual routine. These are the section's **potential outcomes**, measured in kilograms at harvest. The **causal effect** of extra water for the section is their difference, $Y(1) - Y(0)$.
>
> For illustration, assume that the section would yield 3 kilograms under the usual routine and 1 kilogram with extra water. The causal effect is therefore $1 - 3 = -2$ kilograms. Under these assumptions, the model correctly identifies a section at risk of low yield, yet the proposed action would lower its yield further.
>
> Note that we have assumed knowledge of both potential outcomes to make the example checkable. In a real growing period, we observe only the outcome under the action the staff actually takes. The outcome that would have occurred under the alternative is the **counterfactual outcome**. If the staff gives extra water, it observes $Y(1)$, while $Y(0)$ remains unobserved.
>
> Under the stated assumptions, the section would yield more under the usual routine than with extra water. Choosing extra water requires evidence that extra water would improve yield, and the model's prediction does not provide this information.

As the example above shows, the prediction can identify a section at risk, but it does not determine whether extra water would help. Claims that an action improves an outcome require evidence about its effect relative to an alternative.

## Avoid misleading comparisons

Once we have identified the causal effect we want to estimate, we might compare outcomes between sections that historically received different actions in an attempt to estimate it. However, the greenhouse staff might have chosen those historical actions based on information that also affects the outcome. Without accounting for these differences, the comparison can mix the effect of the action with existing differences between the sections, leading to a biased estimate of the causal effect.

Consider the continuation of the greenhouse example below for an illustration.

> **Worked example: Comparing watered and unwatered sections**
>
> To investigate whether extra water helps, the greenhouse staff looks at past watering decisions and yields. The greenhouse has sunny and shaded sections, and sunlight affects yield. Suppose the staff expected sunny sections to need more water, so it gave extra water to two sunny sections and left two shaded sections on the usual routine.
>
> The table below supplies hypothetical yields under both options so that we can check whether the historical comparison recovers the causal effect. As in the first example, the staff could observe only one potential outcome for each section.
>
> | Sections | Staff decision | Yield per section with extra water | Yield per section under the usual routine |
> | --- | --- | ---: | ---: |
> | Two sunny sections | Extra water | **8 kilograms** | 10 kilograms |
> | Two shaded sections | Usual routine | 1 kilogram | **3 kilograms** |
>
> The bold values are the yields the staff would observe; the other values are unobserved counterfactual outcomes. Comparing the observed values gives $8 - 3 = 5$ kilograms more per section in the extra-water group. This is an **association** between extra watering and higher yield.
>
> It would be a mistake to conclude that extra water caused that increase. The watered sections also received more sunlight, which affects yield independently of the watering decision. Sunlight is a **confounder** here because it affects both where the staff waters and how much the sections yield. The observed comparison mixes these effects instead of isolating the effect of extra water.
>
> We can check the causal effect using the assumed potential outcomes in the table. For sunny sections it is $8 - 10 = -2$ kilograms, and for shaded sections it is $1 - 3 = -2$ kilograms. Extra water therefore reduces yield by 2 kilograms in both groups, despite the positive observed difference of 5 kilograms.

As the example above shows, an observed difference between groups can point in the opposite direction from the causal effect. Before using historical records to determine the effect of an action, check whether they support a credible comparison between groups that received different actions.

## Estimate causal effects

The historical comparison fails because sunlight influences both the watering decision and yield. We still cannot observe both potential outcomes for the same section in the same growing period, so we need a way to compare groups without selecting the watering action on that basis. **Randomized experiments**, including A/B tests, assign actions by chance to create such a comparison.

The example below continues the greenhouse scenario and shows how the greenhouse team could obtain the comparison missing from their historical records.

> **Worked example: Designing an irrigation comparison**
>
> In the previous example, staff gave extra water only to sunny sections. The old records therefore contain no sunny sections on the usual routine and no shaded sections with extra water. Comparing sections with similar sunlight would require observations the greenhouse staff does not have, so the team plans a new experiment.
>
> Assume that in a new growing period the staff has 24 sections. They randomly assign 12 to receive extra water and 12 to stay on the usual routine: chance determines which sections receive each action, rather than staff preferences or sunlight exposure. Assume also that watering one section does not affect another section's yield and that each watering option is applied consistently.
>
> At harvest, the staff compares average yields between the two groups. Random assignment balances observed and unobserved characteristics in expectation over repeated assignments, although the groups in this experiment may still differ by chance.
>
> Suppose the experiment produces the following results. These numbers are constructed for illustration.
>
> | Assigned action | Number of sections | Total yield | Average yield per section |
> | --- | ---: | ---: | ---: |
> | Extra water | 12 | 54 kilograms | 4.5 kilograms |
> | Usual routine | 12 | 78 kilograms | 6.5 kilograms |
>
> The quantity we want to estimate is the average of the individual causal effects across these 24 sections. If $Y_i(1)$ and $Y_i(0)$ are the potential outcomes for section $i$, this average is:
>
> $$
> \mathrm{ATE}=\frac{1}{24}\sum_{i=1}^{24}\bigl(Y_i(1)-Y_i(0)\bigr).
> $$
>
> We cannot calculate it directly because we do not observe both outcomes for any section. Instead, random assignment allows us to estimate it using the difference between the two groups' observed average yields:
>
> $$
> \widehat{\mathrm{ATE}}=\overline{Y}_{\text{extra water}}-\overline{Y}_{\text{usual routine}}=4.5-6.5=-2.
> $$
>
> Here, each $\overline{Y}$ is an observed group average, and the hat distinguishes the estimate from the true average effect. Under the stated assumptions, this estimator equals the average causal effect in expectation over random assignments. The result from this experiment suggests that extra water lowers yield by 2 kilograms per section on average, but it remains uncertain because a different assignment could produce a different estimate. It does not reveal the effect for each individual section, and extending the result to other sections or growing periods requires further justification.
>
> If random assignment is infeasible, observational causal inference methods, such as matching or weighting, could help compare sections in existing records. Matching compares sections with similar measured characteristics; weighting changes how much each observation contributes to make the groups more comparable. These methods require assumptions, including that relevant confounders have been measured and accounted for, that comparable sections received both watering options, and that each watering option was applied consistently.

As the example above shows, random assignment provides a way to estimate an average causal effect without observing both potential outcomes for each section. When A/B testing is infeasible, observational causal inference methods can help estimate effects, but their conclusions depend on assumptions about the historical data. For example, observational causal inference methods cannot rule out unmeasured confounding or supply comparisons absent from the records.

So far, we have asked whether changing the watering routine improves yield. The same reasoning applies to the inspection decision raised at the start of the chapter: using the model's ranking changes how staff allocate inspections, and that change also needs evaluation.

For example, suppose each greenhouse has its own staff implementing the inspection workflow. An A/B test could randomly assign whole greenhouses to use either the current workflow or one that prioritizes inspections using the model's predictions. Assigning whole greenhouses avoids asking the same staff to follow competing workflows within one greenhouse. The team could then compare the number of problems identified in time to act over the same period and with the same inspection capacity.

This comparison estimates the causal effect of introducing the model-assisted workflow on timely problem detection. It does not isolate the contribution of the predictions from accompanying changes in staff behavior or inspection timing. To determine whether the workflow also improves yield, the team would need to compare yield under the two workflows. Better predictions, earlier detection, and improved yield are distinct results that require appropriate evidence.

This illustrates a broader point: even when predictions are used only to inform human decisions, such as prioritizing inspections, we cannot assume that changing those decisions automatically improves the desired outcome. Determining whether this is the case requires evaluating the causal effect of that change.

## Further reading

- **Distinguish predictions from causal effects.** Kleinberg and colleagues explain why some decisions need only predictions while others need estimates of causal effects. [Jon Kleinberg and colleagues, *Prediction Policy Problems*](https://www.aeaweb.org/articles?id=10.1257/aer.p20151023)
- **Avoid misleading comparisons.** Chapter 1 defines causal effects using potential outcomes and explains how they differ from observed associations. [Miguel Hernán and James Robins, *Causal Inference: What If*, Chapter 1](https://miguelhernan.org/whatifbook)
- **Estimate causal effects.** Chapters 2 and 3 explain what random assignment provides and what assumptions a comparison based on observational data requires. [Miguel Hernán and James Robins, *Causal Inference: What If*, Chapters 2–3](https://miguelhernan.org/whatifbook)
