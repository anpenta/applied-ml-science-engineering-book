# Before Machine Learning

Suppose we receive a request to build a machine learning model for a company. How would we know whether building the model is worth the effort?

To make that judgment, we need to understand the operational problem, define what success means, and compare machine learning with alternative approaches.

## Understand the operational problem

A model is useful only in relation to the operational problem it is meant to address. To understand the operational problem, we need to identify the **business objective**, the **decision** to be made, the **action** that follows, and the **constraints** on what can be done.

The example below illustrates these four components and shows how understanding the operational problem can actually change which model we prefer.

> **Worked example: Prioritizing equipment inspections**
>
> A company asks a technical team to build a model that predicts failures in industrial machines. Before building a model, the technical team should understand the operational problem that the company wants to address. We describe the company's operational problem in the table below.
>
> | Operational component | In this example |
> | --- | --- |
> | **Business objective** | Reduce unexpected equipment failures. |
> | **Decision** | Which machines should be inspected first? |
> | **Action** | Inspect the selected machines for signs of deterioration. |
> | **Constraints** | Staff and time permit only 10 inspections per week. |
>
> Assume that the technical team builds two different models. At the start of the week, each model scores the same 1,000 machines on their risk of failure over the next 30 days. Without preventive action, 50 of those machines would fail within that period. Also, the company's staff has 10 available inspection slots that week.
>
> To calculate classification accuracy and precision, the technical team uses a threshold of 0.5 to turn each score into a binary yes/no prediction. To help the company's staff schedule inspections, the technical team ranks the machines by score for each model and selects the 10 highest-scoring machines on each list for the staff to prioritize.
>
> The table below shows the classification results for both models at the 0.5 threshold.
>
> | Actual outcome | Model A: Predicted failure | Model A: Predicted non-failure | Model B: Predicted failure | Model B: Predicted non-failure |
> | --- | ---: | ---: | ---: | ---: |
> | Failure (50 machines) | 10 | 40 | 30 | 20 |
> | Non-failure (950 machines) | 10 | 940 | 80 | 870 |
> | **Total** | **20** | **980** | **110** | **890** |
>
> From the classification results above, we can see that Model A predicts that 20 machines will fail, whereas Model B predicts that 110 will fail. We can use these counts to calculate accuracy and precision at the 0.5 threshold.
>
> The next table compares these metrics with precision among the 10 highest-ranked machines.
>
> | Evaluation result | Model A | Model B |
> | --- | ---: | ---: |
> | **Accuracy at the 0.5 threshold** | **950/1,000 = 95%** | **900/1,000 = 90%** |
> | **Precision at the 0.5 threshold** | **10/20 = 50%** | **30/110 ≈ 27.3%** |
> | Actual failures among the 10 highest-ranked machines | 2 | 8 |
> | **Precision at top 10** | **2/10 = 20%** | **8/10 = 80%** |
>
> **Accuracy at the 0.5 threshold** measures the proportion of correct yes/no classifications. **Precision at the 0.5 threshold** measures the proportion of flagged machines that would fail without preventive action. **Precision at top 10** measures that proportion only among the 10 machines selected for inspection.
>
> At the 0.5 threshold, Model A has higher classification accuracy and higher precision, so it may seem better initially. However, the inspection team has only 10 inspection slots, so each model will be actually used to select its 10 highest-scoring machines for inspection. As the table above shows, Model B puts eight machines that would fail without preventive action on the list, whereas Model A puts only two. Precision at top 10 captures this difference because it evaluates the list the team would actually use, and it is therefore a better way to evaluate and choose a model for this operational problem.

As the example above shows, the operational constraints determine which predictions matter for the decision. With only 10 inspection slots, we should evaluate the machines at the top of the ranking, rather than all classifications at an arbitrary threshold.

## Define success

Let's assume that we already understand the operational problem. That alone is not enough to proceed with building a model. We also need a preliminary way to judge whether building one would be worthwhile.

The **business objective** describes what the company wants to improve. The **business metric** measures progress toward that business objective. The **success criterion** specifies what result on the business metric counts as success. A success criterion can be as simple as improving on the approach that is currently in use. We can always refine the business metric and success criterion as we learn more.

The example below builds on the previous example to illustrate these three concepts and show the importance of having a success criterion.

> **Worked example: Defining success**
>
> Continuing the equipment-inspection example, consider the business objective, business metric, and success criterion for this use case, shown in the table below.
>
> | Concept | In this example |
> | --- | --- |
> | **Business objective** | Reduce unexpected equipment failures. |
> | **Business metric** | Number of unexpected equipment failures over 30 days. |
> | **Success criterion** | Fewer unexpected equipment failures over 30 days than under the current inspection policy, with the same inspection capacity. |
>
> Assume again that 50 machines would fail over the next 30 days without preventive action. Additionally, assume that inspecting any of those machines always prevents its failure. With 10 available inspection slots, the current inspection policy selects 5 of those machines, Model A selects 2, and Model B selects 8.
>
> Under the assumptions above, we can actually calculate the business metric directly from the evaluation metric mentioned in the previous example. We multiply precision at top 10 by 10 to get the number of failures prevented, then subtract that number from 50 to get the number of unexpected failures as shown in the table below.
>
> | | Current inspection policy | Model A | Model B |
> | --- | ---: | ---: | ---: |
> | Failures prevented under the assumption | 5 | 2 | 8 |
> | **Unexpected failures over 30 days** | **45** | **48** | **42** |
>
> This direct relationship between the evaluation metric and the business metric is useful because every improvement in one translates into a known improvement in the other. Under the example’s assumption, maximizing precision at top 10 is equivalent to minimizing unexpected failures.
>
> In this case, we can see that Model B meets the success criterion by reducing unexpected failures from 45 to 42 with the same inspection capacity. Model A leaves 48 unexpected failures, three more than the current inspection policy, and therefore does not meet the success criterion.

As shown in the example above, a success criterion is helpful because it gives us a benchmark that even the best candidate solution has to meet before we consider it.

## Consider alternatives

Imagine that we already understand the operational problem and have a definition of success. Should we start building a machine learning model?

Before building a machine learning model, we should compare machine learning with simpler approaches that could meet the same business objective. A simple rule can be cheap to build and maintain, while a machine learning model may pick up patterns the rule misses. The question is whether this improvement is worth the added cost.

The example below continues the equipment-inspection scenario to illustrate this trade-off.

> **Worked example: Considering alternatives**
>
> Continuing the equipment-inspection example, assume that the company could prioritize machines using a simple rule: inspect the 10 machines with the most operating hours since their last inspection.
>
> The technical team compares the simple rule with Model B to see whether preventing more failures justifies the model’s higher cost. As in the previous example, assume that inspecting a machine that would otherwise fail always prevents its failure. For the comparison, the technical team uses an estimated cost of $10,000 per unexpected failure and $200 per inspection provided by the company. They also assign a share of each approach’s development and maintenance costs to that week.
>
> | | Simple rule | Model B |
> | --- | ---: | ---: |
> | Failures prevented under the assumption | 7 | 8 |
> | Avoided failure costs | $70,000 | $80,000 |
> | Inspection costs | $2,000 | $2,000 |
> | Net benefit from inspections | $68,000 | $78,000 |
> | Development and maintenance costs allocated to the week | $1,000 | $15,000 |
> | **Total net benefit** | **$67,000** | **$63,000** |
>
> As we can see in the table above, Model B prevents one more failure, worth $10,000 under these assumptions. However, its development and maintenance costs are $14,000 higher, so the simple rule actually comes out $4,000 ahead. In this case, it would make more sense to choose the simple rule as the solution to the problem.

The example above shows that the additional cost of machine learning needs to be justified by the business value it adds. Machine learning shouldn't be considered a default approach, especially if other approaches provide higher total net benefit.

## Further reading

- **Understand the operational problem.** Chicago used a simulation to estimate how much sooner a risk-based inspection order would uncover critical food safety violations. [City of Chicago, *Food Inspection Forecasting*](https://chicago.github.io/food-inspections-evaluation/)
- **Define success.** Google distinguishes business metrics from model metrics and shows how to choose measurable targets. [Google for Developers, *Measuring success*](https://developers.google.com/machine-learning/managing-ml-projects/success)
- **Consider alternatives.** Google shows how to use a simple heuristic as a baseline and compare it with machine learning on quality, cost, and maintenance. [Google for Developers, *Understand the problem*](https://developers.google.com/machine-learning/problem-framing/problem#clear-use-case-for-ml)
