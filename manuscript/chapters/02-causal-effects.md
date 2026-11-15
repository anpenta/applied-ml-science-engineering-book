# Causal Effects

Suppose greenhouse staff want to improve yield and have a model that flags sections likely to produce a low yield. The staff could inspect the flagged sections or give them extra water. What would they need to know to decide whether either action would help?

In the equipment example in Chapter 1, we assumed that inspecting a machine that would otherwise fail prevented its failure. Here we ask what evidence would support an assumption like that. To answer the greenhouse questions, we need to understand how to distinguish predictions from causal effects, avoid misleading comparisons, and estimate causal effects.

## Distinguish predictions from causal effects

A prediction of low yield can help us identify greenhouse sections to prioritize for inspection, but it does not tell us whether giving those sections extra water would improve their yield. To answer the watering question, we need to compare what would happen under the two watering routines. In fact, whether prioritizing inspections based on predictions improves yield is also a causal question, which we will return to later. For now, let us focus on the action of providing extra water.

In causal inference, the action whose effect we study is called the **treatment**, and the quantity it may change is the **outcome**. In this chapter, we use **action** to describe the treatment under study and always specify the alternative we compare it with.

The example below illustrates the difference between predicting an outcome and estimating the effect of an action.

> **Worked example: Deciding whether to give extra water**
>
> Suppose a model predicts that a greenhouse section is likely to produce a low yield under the usual routine. The greenhouse staff considers giving that section extra water. To decide whether extra water would help, the staff would need to compare the yield under each routine for that same section.
>
> Here, the action under study is extra watering, the alternative is the usual routine, and the outcome is yield in kilograms at harvest. Let $Y(1)$ be the yield with extra water and $Y(0)$ the yield under the usual routine. These are the section's **potential outcomes**. The **causal effect** of extra water for the section is $Y(1) - Y(0)$. For illustration, suppose that the section would yield 3 kilograms under the usual routine and 1 kilogram with extra water. In that case, the causal effect is $1 - 3 = -2$ kilograms.
>
> Note that we have assumed knowledge of both potential outcomes to make the example checkable. In a real growing period, we observe only the outcome under the action the staff actually takes. The outcome that would have occurred under the alternative is the **counterfactual outcome**. If the staff gives extra water, it observes $Y(1)$, while $Y(0)$ remains unobserved.
>
> Under the stated assumptions, the section would yield more under the usual routine than with extra water. Choosing extra water requires evidence that extra water would improve yield, and the model's prediction does not provide this information.

As the example above shows, the prediction can identify a section at risk, but it does not determine whether extra water would help. Claims that an action improves an outcome require evidence about its effect relative to an alternative.

## Avoid misleading comparisons

Once we have identified the causal effect we want to estimate, we might compare outcomes between sections that historically received different actions in an attempt to estimate it. However, the greenhouse staff might have chosen those historical actions based on information that also affects the outcome. Without accounting for these differences, the comparison can mix the effect of the action with existing differences between the sections, leading to a biased estimate of the causal effect.

> **Worked example: Comparing watered and unwatered sections**
>
> Suppose the greenhouse staff looks back at a period when it used sunlight to decide where to give extra water. The staff watered two sunny sections more and kept two shaded sections on the usual routine. The sunny sections also tend to yield more under either watering routine, which makes it harder to tell what extra water did.
>
> The bold values below are the yields the staff would observe under that policy. The other values are hypothetical yields under the routine each group did not receive.
>
> | Sections | Staff decision | Yield per section with extra water | Yield per section under the usual routine |
> | --- | --- | ---: | ---: |
> | Two sunny sections | Extra water | **8 kilograms** | 10 kilograms |
> | Two shaded sections | Usual routine | 1 kilogram | **3 kilograms** |
>
> The observed difference is $8 - 3 = 5$ kilograms per section in favor of the sections that received extra water. The staff concludes that extra water increases yield by 5 kilograms. However, it assigned extra water only to sunny sections, so the comparison mixes the effect of watering with the effect of sunlight. The observed difference is an **association** between extra watering and yield, **confounded** by sunlight. It does not represent the causal effect of extra water.
>
> We can check the actual causal effect using the assumed potential outcomes in the table. For sunny sections, the effect is $8 - 10 = -2$ kilograms per section. For shaded sections, it is $1 - 3 = -2$ kilograms per section. Sunlight is a **confounder** here because it affects both where the staff waters and how much the sections yield.

As the example above shows, an observed difference between groups can point in the opposite direction from the causal effect. Before using historical records to determine the effect of an action, check whether they support a credible comparison between groups that received different actions.

## Estimate causal effects

We cannot observe both potential outcomes for the same section in the same growing period. Therefore, to estimate an average causal effect across sections, we need groups whose outcomes can be credibly compared. **Causal inference** concerns learning about causal effects from data. **Randomized experiments**, including A/B tests, and **observational methods** are two approaches for estimating causal effects.

> **Worked example: Designing an irrigation comparison**
>
> The historical records show sunny sections with extra water and shaded sections on the usual routine. To estimate the effect of watering, the staff needs a comparison that separates the watering decision from sunlight.
>
> Assume that in a new growing period the staff has 24 sections. They use chance to assign 12 sections to receive extra water and 12 to stay on the usual routine. The assignment no longer depends on sunlight or staff preferences, although the groups may still differ by chance. At harvest, the staff uses the difference in average yields between the two groups to estimate the average causal effect across sections.
>
> Suppose the experiment produces the following results. These numbers are constructed for illustration.
>
> | Assigned action | Number of sections | Total yield | Average yield per section |
> | --- | ---: | ---: | ---: |
> | Extra water | 12 | 54 kilograms | 4.5 kilograms |
> | Usual routine | 12 | 78 kilograms | 6.5 kilograms |
>
> The estimated average causal effect is $4.5 - 6.5 = -2$ kilograms per section. The estimate suggests that extra water lowers average yield. Unlike the historical comparison, this comparison uses randomly assigned groups rather than groups selected by sunlight. It still has sampling uncertainty, which the staff should assess before changing the watering routine. It also does not reveal the effect for each individual section.
>
> If random assignment is infeasible, observational causal inference methods, such as matching or weighting, could help compare sections in existing records. These methods require some assumptions, including that the comparison accounts for confounding factors, that comparable sections received both watering options, and that each watering option was applied consistently across sections.

As the example above shows, random assignment provides a way to estimate an average causal effect without observing both potential outcomes for each section. When A/B testing is infeasible, observational causal inference methods can help estimate effects, but their conclusions depend on assumptions about the historical data. For example, observational causal inference methods cannot rule out unmeasured confounding or supply comparisons absent from the records.

The same reasoning applies to the inspection question from the opening. Using the model's ranking changes which sections the staff inspects first. To find out whether that helps, we need to compare outcomes under the two inspection workflows. For example, an A/B test could randomly assign greenhouses to use either the current inspection workflow or one that prioritizes inspections using the model's predictions, then compare how many problems the staff identify in time to act. This comparison estimates the causal effect of the workflow change on timely problem detection. To determine whether the change also improves yield, the team would need to compare yield under the two workflows.

This illustrates a broader point: even when predictions are used only to inform human decisions, such as prioritizing inspections, we cannot assume that changing those decisions automatically improves the desired outcome. Determining whether this is the case requires evaluating the causal effect of that change.

## Further reading

- **Distinguish predictions from causal effects.** Kleinberg and colleagues explain why some decisions need only predictions while others need estimates of causal effects. [Jon Kleinberg and colleagues, *Prediction Policy Problems*](https://www.aeaweb.org/articles?id=10.1257/aer.p20151023)
- **Avoid misleading comparisons.** Chapter 1 defines causal effects using potential outcomes and explains how they differ from observed associations. [Miguel Hernán and James Robins, *Causal Inference: What If*, Chapter 1](https://miguelhernan.org/whatifbook)
- **Estimate causal effects.** Chapters 2 and 3 explain what random assignment provides and what assumptions a comparison based on observational data requires. [Miguel Hernán and James Robins, *Causal Inference: What If*, Chapters 2–3](https://miguelhernan.org/whatifbook)
