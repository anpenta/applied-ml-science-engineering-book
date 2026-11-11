# Interpreting Model Explanations

Let's assume that a model flags a project as likely to miss its delivery date. The explanation points to the number of overdue tasks in the project. What does this tell us about the model, and what does it tell us about why delivery might be late?

To answer these questions, we first need to understand what the explanation describes and how dependencies between features can affect it. We can then use the explanation to decide what to investigate in the model and the data.

## Understand what the explanation describes

What does it mean when an explanation says a feature contributed to a prediction? The answer depends on how the explanation method works.

The example below shows why we need to understand how an explanation is constructed before interpreting a feature's contribution.

> **Worked example: Explaining a forecast of late delivery**
>
> Suppose that a model gives a project a risk score of 70 on a scale from 0 to 100. To explain that score, we use a Shapley-based explanation that compares it with the model's average score on a chosen set of reference projects. Assume the following results for illustration.
>
> | | Reference: Same team's projects | Reference: Company's projects |
> | --- | ---: | ---: |
> | Average model score on reference projects | 30 | 60 |
> | Current project's score | 70 | 70 |
> | Difference to explain | 40 | 10 |
> | Contribution assigned to overdue tasks | +25 | +5 |
> | Combined contribution of other features | +15 | +5 |
>
> The model predicts the same risk score of 70 in both cases. However, when compared with projects from the same team, overdue tasks contribute 25 points toward explaining why the score is higher than the reference. When compared with projects across the company, their contribution is only 5 points. The remaining contributions also differ, but in both cases they add up to the difference between the prediction and the reference score.
>
> A local surrogate provides a different kind of explanation. It fits a simpler model to approximate the risk model's predictions near the current project's inputs. Its explanation describes that local approximation, whose accuracy we also need to check.
>
> The two methods describe different aspects of the model's prediction and may therefore produce different explanations. Furthermore, neither method tells us whether finishing a particular overdue task would bring delivery forward. That requires evidence about what work is holding up the project and what changing it would do.

As the example above shows, we need to understand how an explanation is constructed before interpreting it. For methods that use a reference prediction, changing that reference can change the explanation without changing the model's prediction. More generally, different explanation methods can describe different aspects of the same prediction.

## Account for dependent features

How should we interpret a feature's contribution when another feature carries the same information? More generally, how does dependence between features affect their explanations?

The example below shows how models can agree on every observed prediction while giving credit to different features.

> **Worked example: Two reports of the same overdue tasks**
>
> Continuing the late-delivery example, suppose that the project team records the number of overdue tasks in two places: the project board, $x_1$, and a weekly report, $x_2$. The report copies the board's count at the same snapshot, so $x_1=x_2$ for every project in the dataset. Consider three simple models that score a project using $2x_1$, $2x_2$, or $x_1+x_2$.
>
> | Number of overdue tasks in both sources | Score from $2x_1$ | Score from $2x_2$ | Score from $x_1+x_2$ |
> | --- | ---: | ---: | ---: |
> | 1 | 2 | 2 | 2 |
> | 2 | 4 | 4 | 4 |
> | 3 | 6 | 6 | 6 |
>
> All three models give identical predictions for every project in the dataset. However, their explanations can differ. An explanation of the first model could attribute the score to the board's count, while an explanation of the second could attribute it to the report's count. For the third model, both features could contribute to the score.
>
> Since the report copies the board, neither source provides information that the other lacks. The different explanations therefore reflect how the models use the dependent features, rather than a difference in the information available to them.

As the example above shows, different models can make the same predictions while assigning importance to different features. More generally, when features carry overlapping information, we should consider their dependence before interpreting their contributions to a prediction.

## Use explanations to investigate

What should we check when an explanation points to a feature? We can start by investigating how the model uses that feature and whether this behavior is consistent with what we know about the task. This investigation may confirm a useful pattern or reveal a potential problem, such as target leakage, a preprocessing error, or a feature unavailable at prediction time.

The example below illustrates how examining a model's use of a feature can reveal where to look for missed predictions.

> **Worked example: Investigating how a tree uses overdue tasks**
>
> Continuing the late-delivery example, assume that the project risk model is a decision tree. An explanation points to overdue tasks as a reason for a high risk score. The technical team examines the tree's splits and finds that it first checks whether a project depends on another project team. For projects with this dependency, the tree assigns a high score when three or more tasks are overdue and a low score otherwise. For projects handled entirely by one team, it assigns a low score regardless of the number of overdue tasks.
>
> The technical team confirms this behavior by changing the overdue-task count from two to three while keeping the other inputs fixed. The table below shows the results.
>
> | Dependency on another project team? | Score with two overdue tasks | Score with three overdue tasks |
> | --- | --- | --- |
> | Yes | Low | High |
> | No | Low | Low |
>
> The results show that the tree ignores the overdue-task count for projects handled entirely by one team. To investigate whether this is a problem, the technical team checks the actual delivery dates of such projects in held-out records. Suppose they find the following results.
>
> | Projects handled entirely by one team | Projects checked | Finished late | Proportion that finished late | Tree's score |
> | --- | ---: | ---: | ---: | --- |
> | Fewer than three overdue tasks | 20 | 2 | 10 percent | Low |
> | Three or more overdue tasks | 20 | 10 | 50 percent | Low |
>
> In these records, half the projects with at least three overdue tasks finished late, yet the tree assigned all of them a low score. This gives the technical team a reason to investigate whether the model is missing a useful pattern for this group.
>
> Inspecting the tree revealed where to investigate, while checking the actual delivery dates provided evidence of a potential problem that the explanation alone could not establish.

As the example above shows, explanations can help us understand how a model uses a feature and identify patterns worth investigating. Checking the data can then help us determine whether those patterns are useful or reveal a potential problem.

## Further reading

- **Understand what the explanation describes.** This chapter explains how Shapley values assign credit relative to a reference prediction. [Christoph Molnar, *Interpretable Machine Learning*, “Shapley Values”](https://christophm.github.io/interpretable-ml-book/shapley.html)
- **Account for dependent features.** The paper shows how assumptions about feature dependence affect Shapley-based attributions. [Kjersti Aas and colleagues, *Explaining Individual Predictions When Features Are Dependent*](https://arxiv.org/abs/1903.10464)
- **Use explanations to investigate.** This paper shows how to change an input to see how a prediction responds and how to check model performance for specific groups. [James Wexler and colleagues, *The What-If Tool: Interactive Probing of Machine Learning Models*](https://arxiv.org/abs/1907.04135)
