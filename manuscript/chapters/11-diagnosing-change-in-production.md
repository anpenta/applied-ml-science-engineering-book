# Diagnosing Change in Production

Imagine a recycling facility that uses a machine learning model to identify bottles that require manual sorting. One day, the system starts diverting more bottles than usual. Should the technical team retrain the model, repair a camera, or leave the system running as it is?

To decide, we need to monitor the system for different kinds of failure, distinguish changes in the data from declining predictive quality, and investigate the cause of any problems. Before replacing the model, we also need evidence that the replacement improves the system.

## Monitor different kinds of failure

A system can respond on time while still receiving incorrect inputs or making poor predictions. We should therefore monitor more than response times, using different measures to identify potential problems with the data, the model, and the system that uses its predictions.

The example below shows how different monitoring measures can help identify problems in a recycling facility.

> **Worked example: Monitoring a recycling system**
>
> A recycling facility uses a model to identify bottles that require manual sorting. A camera captures images of the bottles, the model predicts which ones should be diverted, and a sorting mechanism acts on those predictions. The technical team monitors the following measures.
>
> | Measure | What it helps the team check |
> | --- | --- |
> | Missing or unusable images | Whether the camera provides usable inputs |
> | Proportion of bottles recommended for diversion | Whether the model is recommending more manual sorting |
> | Response times and service errors | Whether predictions arrive reliably and on time |
> | Predictions compared with staff assessments | Whether the model correctly identifies bottles requiring manual sorting |
>
> One morning, the proportion of bottles recommended for diversion increases, while response times and service errors remain stable. The technical team knows that the model is recommending more diversions, but they cannot yet determine whether those recommendations are correct.
>
> To investigate, the team examines recent images and compares the model's predictions with staff assessments of a sample of bottles, including those not diverted. This helps determine whether more bottles genuinely require manual sorting or whether the model's predictive quality has declined.

As the example above shows, different monitoring measures help us identify different kinds of problems. We should monitor both system behavior and predictive quality to determine whether the system continues to work as intended.

## Distinguish drift from degradation

**Drift** refers to changes in the data distribution over time. These changes can affect the inputs, the outcomes, or the relationship between them. **Degradation** refers to a decline in predictive quality. Drift does not necessarily lead to degradation, even when the relationship between inputs and outcomes changes. Whether predictive quality declines depends on how the changes affect the model's predictions and the measure used to evaluate them.

The example below illustrates the difference between drift and degradation using a simplified model.

> **Worked example: Distinguishing drift from degradation**
>
> Continuing the recycling example, let's assume that the model uses a simple rule: divert bottles with blue caps and leave all other bottles on the line. Staff then check which bottles actually require manual sorting.
>
> The table compares two hypothetical scenarios against a reference group of four bottles.
>
> | Group | Bottles with blue caps | Bottles requiring manual sorting | Incorrect predictions |
> | --- | --- | --- | --- |
> | Reference | 2 of 4 | The 2 with blue caps | 0 of 4 |
> | Scenario 1 | 3 of 4 | The 3 with blue caps | 0 of 4 |
> | Scenario 2 | 2 of 4 | The 2 without blue caps | 4 of 4 |
>
> In the first scenario, the proportion of blue caps increases, but the model continues making correct predictions. This demonstrates a change in the input distribution, commonly called **covariate drift**, without degradation.
>
> In the second scenario, the proportion of blue caps remains unchanged, but the relationship between cap color and the need for manual sorting reverses. The model now makes incorrect predictions for every bottle. This demonstrates a change in the relationship between inputs and outcomes, commonly called **concept drift**, accompanied by degradation.

As the example above shows, different types of drift can have different effects on predictive quality. We should therefore monitor both changes in the data and predictive quality rather than assuming that detecting drift necessarily means the model has become less reliable.

## Investigate the cause

The same monitoring alert can have several possible causes. We should investigate these causes before deciding what to change in the system.

The example below shows how an investigation can distinguish a technical failure from a change in the data.

> **Worked example: Investigating an increase in diversions**
>
> Continuing the recycling example, assume that the increase in diversion recommendations begins when two changes occur at the same time: a software update is deployed, and bottles with a new packaging design start arriving. Operators report that bottles with the new design are frequently sorted incorrectly.
>
> The technical team investigates two possible explanations. The table shows their findings.
>
> | Possible cause | Investigation and finding |
> | --- | --- |
> | The software update introduced an error. | The team processes the same images using the old and new software versions. Both produce identical predictions, suggesting that the update did not cause the observed errors. |
> | The new packaging design changed the relationship between bottle appearance and sorting needs. | Staff check a sample of bottles with the new design and find that the model frequently makes incorrect predictions. Bottles with the older design are still classified correctly. |
>
> The findings suggest that the new packaging design is responsible for the decline in predictive quality, rather than the software update. The technical team therefore collects additional labeled images of bottles with the new design and evaluates whether updating the model improves its predictions.
>
> Had the investigation instead identified a software error, correcting that error would have been more appropriate than retraining the model.

As the example above shows, the timing of a change does not necessarily tell us what caused a problem. We should investigate possible explanations and use the findings to determine what, if anything, needs to change in the system.

## Require evidence before replacing a model

Identifying a problem with the current model does not mean that a replacement will perform better. Before making a change, we should compare the candidate with the existing model, considering both predictive quality and operational requirements.

The example below shows how this comparison can help us decide whether a candidate is ready for a limited trial.

> **Worked example: Deciding whether to try a new model**
>
> Continuing the recycling example, the technical team trains a candidate model using newly collected data. It compares the candidate with the current model on a separate sample of 400 bottles that were not used during training or model selection. Half have the older packaging design, and half have the new design.
>
> Before the comparison, the team agrees that the candidate must reduce the total number of missed bottles without substantially increasing unnecessary diversions or making predictions too slowly. They also agree to accept no more than two additional missed bottles with the older design.
>
> The following table shows the evaluation results.
>
> | Measure | Current model | Candidate model |
> | --- | ---: | ---: |
> | Missed bottles with the older design | 8 | 10 |
> | Missed bottles with the new design | 32 | 12 |
> | **Total missed bottles** | **40** | **22** |
> | Unnecessary diversions | 16 | 18 |
> | Time within which 95% of predictions arrive | 25 ms | 30 ms |
>
> We can see that the candidate misses 18 fewer bottles overall, with only two additional misses on the older design and two additional unnecessary diversions. Its response time also remains within the team's requirement of 40 milliseconds. The candidate therefore meets the agreed criteria for a limited trial.
>
> The technical team proceeds with a limited trial, continuing to monitor predictive quality and system performance. If the candidate fails to meet the agreed requirements during the trial, the team can restore the previous model.

As the example above shows, identifying a problem with the current model does not necessarily justify replacing it. We need evidence that a candidate improves predictive quality while meeting the system's operational requirements.

## Further reading

- **Monitor different kinds of failure.** The guide covers data validation, service behavior, and checking live model quality when labels are not immediately available. [Google for Developers, *Production ML systems: Monitoring pipelines*](https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring)
- **Distinguish drift from degradation.** The survey distinguishes changes in input distributions from changes in the relationship between inputs and outcomes. [João Gama and colleagues, *A Survey on Concept Drift Adaptation*](https://doi.org/10.1145/2523813)
- **Investigate the cause.** The chapter explains how to form and test competing explanations for an operational symptom. [Google, *Site Reliability Engineering*, “Effective Troubleshooting”](https://sre.google/sre-book/effective-troubleshooting/)
- **Require evidence before replacing a model.** The “Data and model validation” section covers comparison with the current model, checks across data groups, and limited deployment before broader use. [Google Cloud, *MLOps: Continuous delivery and automation pipelines in machine learning*](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
