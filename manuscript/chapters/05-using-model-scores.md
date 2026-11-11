# Using Model Scores

Suppose that a clinic's reception team can make up to ten reminder calls a day about patient appointments. A model scores each upcoming appointment by how likely the patient is to miss it. Should the reception team call the ten patients with the highest scores, or make fewer calls when the scores are low?

In this chapter, we consider how to turn scores into decisions, how to determine whether to change the model or the decision rule, and how to check whether the decisions actually improve the desired outcome.

## Define how scores become decisions

A model produces predictions, while a decision rule determines how to act on them. For example, when a model assigns scores to cases and capacity is limited, we can prioritize the highest-scoring cases until capacity is reached, or set a minimum score for acting, even if that means leaving some capacity unused.

The clinic example below shows how two different decision rules can lead to different actions even when they use the same scores.

> **Worked example: Deciding how many patients to call**
>
> Each morning, a model scores clinic appointments scheduled for one week later based on the likelihood that patients will miss them. The clinic's reception team can make up to ten reminder calls per day. Under the first decision rule, they call the ten patients with the highest scores. Under the second decision rule, they call only patients with scores of 0.30 or higher, starting with the highest scores and making no more than ten calls. The table below illustrates how the two rules differ.
>
> | | Monday | Tuesday |
> | --- | ---: | ---: |
> | Appointments scored | 30 | 30 |
> | Appointments with scores of 0.30 or higher | 12 | 4 |
> | Calls using the ten highest scores | 10 | 10 |
> | Calls using the cutoff, capped at ten | 10 | 4 |
>
> On Monday, both rules select the same ten appointments. On Tuesday, only four scores meet the cutoff, so the second rule leaves six call slots unused.

As the example above shows, the first decision rule uses only the order of the model's scores, while the second decision rule also considers their values, resulting in different numbers of calls. More generally, applying different decision rules to the same model predictions can lead to different actions.

## Determine whether to change the model or the decision rule

When the decisions informed by a model do not produce the desired results, we should first investigate whether changing the decision rule could improve them while keeping the model's predictions fixed. If so, we have a change to the decision rule worth testing. Otherwise, we should investigate whether the model's predictions need improvement.

The example below shows how to determine whether changing the decision rule or improving the model would be more appropriate.

> **Worked example: Finding out why the calling list misses appointments**
>
> Continuing the clinic example, the technical team looks back at a day when no reminder calls were made and four appointments were missed. They use two different candidate models, both trained on earlier data, to score all appointments for that day using only information available when the calls would have been selected. For each model, they compare two decision rules: calling up to ten patients whose scores are at least 0.30, or calling the ten patients with the highest scores regardless of the cutoff. The table below illustrates the results.
>
> | Where the four missed appointments fell | Model A | Model B |
> | --- | ---: | ---: |
> | In the top ten and met the cutoff | 1 | 1 |
> | In the top ten but below the cutoff | 3 | 0 |
> | Outside the top ten | 0 | 3 |
>
> Under the cutoff rule, only one of the four missed appointments would be selected for a reminder call with either model. Removing the cutoff would increase that number to four for Model A, while leaving it at one for Model B. For Model A, the technical team could test a different decision rule without changing the model. For Model B, they would need to improve the model's ranking to reach the other three appointments within the limit of ten calls.

As the example above shows, the same result under the current decision rule can actually point to different changes. Before deciding what to change, we need to determine where the problem comes from: the scores the model produces or how the decision rule uses them.

## Check whether the decisions improve the outcome

Suppose that we are considering replacing our current decision rule with a new one for a particular application. To determine whether the change would improve the desired outcome, we should compare that outcome under both rules.

The example below continues the clinic example and illustrates how to compare two decision rules based on the desired outcome.

> **Worked example: Should the clinic change its calling rule?**
>
> Continuing the clinic example, assume that the reception team currently calls the ten patients with the highest scores. They are considering calling only patients who score at least 0.30, starting with the highest scores and keeping the daily limit of ten calls. The clinic wants to reduce the number of unused appointment slots. A slot goes unused when a patient misses an appointment or cancels and the clinic cannot fill the opening.
>
> For the pilot, the technical team randomly assigns comparable calling days to one of the two rules, keeping the same limit of ten calls per day. They track the appointment outcomes associated with each day's list, including appointments not selected for a call. Suppose the pilot covers 200 booked slots under each rule and produces the following results.
>
> | | Current rule: ten highest scores | Proposed rule: cutoff, capped at ten |
> | --- | ---: | ---: |
> | Missed appointments | 12 | 10 |
> | Cancellations that left a slot empty | 6 | 10 |
> | **Total unused slots** | **18** | **20** |
>
> If the technical team had judged the rules by missed appointments alone, the cutoff rule would appear better. However, the clinic wants to keep appointment slots in use, and under the cutoff rule, two more slots went unused. This corresponds to 10% of slots under the proposed rule, compared with 9% under the current rule.
>
> Based on these results, the clinic decides to keep the current rule, since the proposed rule did not demonstrate an improvement in the desired outcome.

As the example above shows, we need to evaluate the decision rule against the outcome we want to improve. That outcome can be tricky to define, so we need to be explicit about what we intend to measure.

## Further reading

- **Define how scores become decisions.** The guide shows how changing a threshold can change decisions while leaving the underlying scores unchanged. [scikit-learn, *Tuning the decision threshold for class prediction*](https://scikit-learn.org/stable/modules/classification_threshold.html)
- **Determine whether to change the model or the decision rule.** This guide explains how to evaluate a model at a fixed capacity by measuring how many cases of interest appear among its highest scores. [Triage, *Metrics*](https://dssg.github.io/triage/experiments/algorithm/#metrics)
- **Check whether the decisions improve the outcome.** This randomized trial of targeted appointment reminder calls measured missed appointments, cancellations, and how far in advance patients canceled. [Shah and colleagues, *Targeted Reminder Phone Calls to Patients at High Risk of No-Show for Primary Care Appointment*](https://pubmed.ncbi.nlm.nih.gov/27503436/)
