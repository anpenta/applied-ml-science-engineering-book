# Causal Effects

Imagine that a model predicts which sections of a greenhouse are likely to produce a low yield. Could we use these predictions to decide which sections to inspect first? What about which sections to water more than others?

To answer these questions, we need to understand how to distinguish predictions from causal effects, how to avoid comparisons that can mislead us, and how to estimate causal effects reliably.

## Distinguish predictions from causal effects

A prediction of low yield can help us identify greenhouse sections to prioritize for inspection, but it does not tell us whether giving those sections extra water would improve their yield. The latter is a causal question. In fact, whether prioritizing inspections based on predictions improves yield is also a causal question, which we will return to later. For now, let us focus only on the action of providing extra water to some sections.

In causal inference, the action whose effect we study is called the **treatment**, and the quantity that the treatment affects is called the **outcome**. In this chapter, we use **action** to describe the treatment under study and always specify the alternative we compare it with.

The example below illustrates the difference between predicting an outcome and estimating the effect of an action.

> **Worked example: Deciding whether to give extra water**
>
> Suppose a model predicts that a greenhouse section is likely to produce a low yield under the usual routine. The greenhouse staff considers giving that section extra water. For illustration, assume that the section in question would yield 3 kilograms under the usual routine and 1 kilogram with extra water. The section is already at risk of a low yield under the usual routine, but extra water would actually lower it further.
>
> Here, the action under study is extra watering, the alternative is the usual routine, and the outcome is yield in kilograms at harvest. Let $Y(1)$ be the yield with extra water and $Y(0)$ the yield under the usual routine. These are the section's **potential outcomes**. The **causal effect** of extra water for the section is $Y(1) - Y(0) = 1 - 3 = -2$ kilograms in this example.
>
> Note that we have assumed knowledge of both potential outcomes to make the example checkable. In a real growing period, we observe only the outcome under the action the staff actually takes. The outcome that would have occurred under the alternative is the **counterfactual outcome**. If the staff gives extra water, they observe $Y(1)$, while $Y(0)$ remains unobserved.
>
> Under the stated assumptions, the section would yield more under the usual routine than with extra water. Choosing extra water requires evidence that extra water would improve yield, and the model's prediction does not provide this information.

As the example above shows, the prediction can identify a section at risk, but it does not determine whether extra water would help. Claims that an action improves an outcome require evidence about its effect relative to an alternative.

## Avoid misleading comparisons

Once we have identified the causal effect we want to estimate, we might compare outcomes between sections that historically received different actions in an attempt to estimate it. However, the greenhouse staff might have chosen those historical actions based on information that also affects the outcome. Without accounting for these differences, the comparison can mix the effect of the action with existing differences between the sections, leading to a biased estimate of the causal effect.

Consider the continuation of the greenhouse example below for an illustration.

> **Worked example: Comparing watered and unwatered sections**
>
> Continuing the greenhouse example, assume that the greenhouse staff gives extra water to two sunny sections and leaves two shaded sections on the usual routine. The staff chooses the sunny sections because they think that those sections need more water due to greater sunlight exposure. For illustration, assume that the yields under both options are as follows.
>
> | Sections | Staff decision | Yield per section with extra water | Yield per section under the usual routine |
> | --- | --- | ---: | ---: |
> | Two sunny sections | Extra water | **8 kilograms** | 10 kilograms |
> | Two shaded sections | Usual routine | 1 kilogram | **3 kilograms** |
>
> The bold values are the yields the staff would observe. The watered sections yield 5 kilograms more per section than the others. The staff incorrectly concludes that extra water increases yield by 5 kilograms. However, they assigned extra water only to sunny sections, so the comparison mixes the effect of watering with the effect of sunlight. The observed difference is an **association** between extra watering and yield, **confounded** by sunlight. It does not represent the causal effect of extra water.
>
> We can check the actual causal effect using the assumed potential outcomes in the table. Sunny sections would yield 10 kilograms under the usual routine and 8 with extra water. Shaded sections would yield 3 kilograms under the usual routine and 1 with extra water. Extra water therefore reduces yield by 2 kilograms in both groups. Sunlight is a **confounder** here because it affects both where the staff waters and how much the sections yield.

As the example above shows, an observed difference between groups can point in the opposite direction from the causal effect. Before using historical records to determine the effect of an action, check whether they support a credible comparison between groups that received different actions.

## Estimate causal effects

We cannot observe both potential outcomes for the same section in the same growing period. Therefore, to estimate an average causal effect across sections, we need groups whose outcomes can be credibly compared. **Causal inference** concerns learning about causal effects from data. **Randomized experiments**, including A/B tests, and **observational causal inference methods** are two approaches for estimating causal effects.

The example below continues the greenhouse scenario and shows how the greenhouse team could obtain the comparison missing from their historical records.

> **Worked example: Designing an irrigation comparison**
>
> Continuing the greenhouse example, imagine that the old records contain no sunny sections on the usual routine and no shaded sections with extra water. Therefore, comparing sections with similar sunlight would require observations the greenhouse staff does not have.
>
> Now assume that in a new growing period the staff has 24 sections in the greenhouse. They randomly assign 12 to receive extra water and 12 to stay on the usual routine. Since assignment is determined by chance rather than by sunlight or other characteristics that affect yield, extra water is not systematically given to sections that would already have higher yields under the usual routine. Therefore, the difference in average yields between the two groups provides an estimate of the **average causal effect** of extra water.
>
> Suppose the experiment produces the following results. Note that these numbers are constructed for illustration purposes.
>
> | Assigned action | Number of sections | Total yield | Average yield per section |
> | --- | ---: | ---: | ---: |
> | Extra water | 12 | 54 kilograms | 4.5 kilograms |
> | Usual routine | 12 | 78 kilograms | 6.5 kilograms |
>
> The estimated average causal effect is $4.5 - 6.5 = -2$ kilograms per section. The estimate suggests that extra water actually lowers average yield. Unlike the historical comparison in the previous example, this comparison uses randomly assigned groups rather than groups selected by sunlight and therefore provides an unbiased estimate of the true average causal effect.
>
> Note that the two groups may still differ by chance, so the estimated effect above is uncertain. Although there are statistical methods to quantify this uncertainty, we omit them in this example for simplicity. Furthermore, this comparison does not reveal the causal effect for each individual section. For that, we would need to observe its yield both with extra water and under the usual routine in the same growing period, which is not possible.
>
> As a side note, if random assignment were infeasible, observational causal inference methods could help compare sections using existing records. However, these methods would require some assumptions, including that the comparison accounts for confounding factors, that the records include comparable sections under each watering option, and that each watering option was applied consistently across sections.

As the example above shows, random assignment provides a way to estimate an average causal effect without observing both potential outcomes for each section. When A/B testing is infeasible, observational causal inference methods can help estimate effects, but their conclusions depend on assumptions about the historical data. For example, observational causal inference methods cannot rule out unmeasured confounding or supply comparisons that are absent from the historical records.

As promised earlier in the chapter, we now return to the question of which sections to inspect first. Notice that using the model’s ranking to prioritize inspections would change the greenhouse’s inspection workflow. To estimate the causal effect of this change on yield, we could randomly assign greenhouses to follow either the current workflow or one that uses the model’s ranking to decide which sections to inspect first. The difference in average yield per greenhouse between the two groups would estimate the causal effect of the workflow change on yield. The downside is that this experiment would require access to several comparable greenhouses.

The above illustrates a broader point: even when predictions are used only to inform human decisions, such as prioritizing inspections, we cannot assume that changing those decisions automatically improves the desired outcome. Determining whether this is the case requires evaluating the causal effect of that change.

## Further reading

- **Distinguish predictions from causal effects.** Kleinberg and colleagues explain why some decisions need only predictions while others need estimates of causal effects. [Jon Kleinberg and colleagues, *Prediction Policy Problems*](https://www.aeaweb.org/articles?id=10.1257/aer.p20151023)
- **Avoid misleading comparisons.** Chapter 1 defines causal effects using potential outcomes and explains how they differ from observed associations. [Miguel Hernán and James Robins, *Causal Inference: What If*, Chapter 1](https://miguelhernan.org/whatifbook)
- **Estimate causal effects.** Chapters 2 and 3 explain what random assignment provides and what assumptions a comparison based on observational data requires. [Miguel Hernán and James Robins, *Causal Inference: What If*, Chapters 2–3](https://miguelhernan.org/whatifbook)
