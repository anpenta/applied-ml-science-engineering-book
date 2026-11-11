# From Experiment to System

We have a model that predicts missed bus connections well in an experiment. What could go wrong when we put that model into a system that makes predictions throughout the day?

To ensure the system works as intended, we need to preserve the meaning of the model's inputs, train the model on the kind of inputs it is expected to receive, and evaluate how changes to individual components affect the whole system.

## Preserve the meaning of inputs

When moving a model from an experiment into production, we need to preserve how its inputs are calculated and interpreted. A production pipeline can supply the expected feature names and data types while calculating values differently from the training pipeline. We need to ensure that these differences do not occur.

The example below shows how two implementations can give the same model different inputs for the same event.

> **Worked example: Checking the meaning of arrival delay**
>
> Assume that a model predicts whether passengers will miss a planned transfer between two buses, using the arrival delay at the last stop the first bus reached. During training, the delay was calculated as actual arrival time minus scheduled arrival time, in minutes. However, the production pipeline mistakenly reverses this calculation, subtracting actual arrival time from scheduled arrival time.
>
> Consider a bus scheduled to arrive at 08:20 that arrives at 08:28. The table below shows what each pipeline produces.
>
> | Pipeline | Calculation | Input to the model |
> | --- | --- | ---: |
> | Training | Actual arrival minus scheduled arrival | 8 |
> | Production | Scheduled arrival minus actual arrival | −8 |
>
> Both pipelines produce a number, so a numeric type check passes. However, the model learned that positive values mean the bus was late. The production pipeline gives it a negative value, which the model interprets as indicating that the bus was early.
>
> To prevent this mismatch, we should define a **feature contract** specifying how arrival delay must be calculated. We should then test both pipelines using the same arrival times to verify that both of them produce the same value.

As the example above shows, checking feature names and data types is insufficient to ensure consistency between training and production. We also need to test that both pipelines produce the intended values from the same records. Where practical, sharing calculation code between training and production can help prevent such inconsistencies.

## Train on realistic upstream inputs

A model always needs to be trained on inputs that reflect what it will receive in production. Otherwise, differences between training and production inputs can undermine its performance, even when the model performs well in an experiment.

The example below shows how a pattern learned by a model from actual delays can fail to predict missed connections when the model receives forecast delays as input instead.

> **Worked example: Learning from forecast delays**
>
> Continuing the bus-connection example, let us suppose that the system uses two models. The first model forecasts the bus’s arrival delay at the transfer stop. The second model uses that forecast to predict whether passengers will miss their bus connection.
>
> For illustration, assume that passengers miss their connection whenever the actual arrival delay exceeds 5 minutes. The first model underestimates every delay in this small example by 2 minutes.
>
> | Journey | Actual delay | Forecast delay | Missed connection? |
> | --- | ---: | ---: | --- |
> | A | 2 minutes | 0 minutes | No |
> | B | 4 minutes | 2 minutes | No |
> | C | 6 minutes | 4 minutes | Yes |
> | D | 8 minutes | 6 minutes | Yes |
>
> If we train the second model using actual delays, it can learn to flag delays above 5 minutes. That rule correctly separates the outcomes in the table. However, production supplies forecast delays from the first model as input to the second model. Consequently, for journey C, the second model receives 4 minutes as input and predicts that passengers will make their connection, although they actually miss it.
>
> If we instead train the second model using the forecast delays along with the recorded connection outcomes, it could learn a threshold above 3 minutes that separates these four cases correctly. This would allow the second model to account for the first model's underestimation in this example.
>
> To construct the training forecasts described above, we should fit the first model on earlier journeys and use it to predict delays for later journeys that were excluded from its training. We should then repeat this process across successive time periods. The resulting forecasts would then become inputs for training the second model, paired with the recorded connection outcomes. Finally, we should evaluate both models together on a separate, later period.

As the example above shows, training a model on inputs that reflect what it will receive in production helps it learn patterns that account for errors in those inputs.

## Evaluate changes to the whole system

Improving one component does not guarantee that the whole system will improve. When another component has learned to use the outputs of the component we changed, changing those outputs can affect the final predictions as well. We should therefore evaluate a proposed replacement together with the components that depend on it.

The example below shows how a more accurate delay forecast can make the system’s connection predictions worse.

> **Worked example: Replacing the delay model**
>
> Continuing the bus-connection example, let's assume that the second model learned to flag forecast delays above 3 minutes. This accounted for the original delay model's consistent underestimation by 2 minutes.
>
> We now consider replacing the delay model. For illustration, assume that the replacement predicts the actual delays exactly on the four journeys below. The second model remains unchanged.
>
> | Journey | Actual delay | Old forecast | New forecast | Missed connection? | Old system prediction | New system prediction |
> | --- | ---: | ---: | ---: | --- | --- | --- |
> | A | 2 minutes | 0 minutes | 2 minutes | No | No | No |
> | B | 4 minutes | 2 minutes | 4 minutes | No | No | Yes |
> | C | 6 minutes | 4 minutes | 6 minutes | Yes | Yes | Yes |
> | D | 8 minutes | 6 minutes | 8 minutes | Yes | Yes | Yes |
>
> The new delay forecasts are more accurate, but the unchanged second model now incorrectly flags journey B. Its threshold still compensates for an underestimation that the new model no longer makes.
>
> Before replacing the delay model, we should compare the old and new combinations on the same held-out journeys, checking the final predictions against recorded missed connections. If the second model needs retraining, we should train it on out-of-sample forecasts from the replacement model and evaluate the revised combination on separate held-out data.

As the example above shows, a component can improve at its own task while making the assembled system worse overall. We should therefore evaluate how a replacement affects the final predictions and determine whether the components that depend on it also need to change.

## Further reading

- **Preserve the meaning of inputs.** Rules 29 and 32 explain how to check consistency between training and production features and reduce discrepancies by sharing calculation code. [Martin Zinkevich, *Rules of Machine Learning*, Rules 29 and 32](https://developers.google.com/machine-learning/guides/rules-of-ml)
- **Train on realistic upstream inputs.** The documentation explains how a final estimator is trained on cross-validated predictions from earlier estimators, rather than their predictions on their own training data. [scikit-learn, *StackingRegressor*](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingRegressor.html)
- **Evaluate changes to the whole system.** The guide covers testing pipeline components together and checking predictive quality when introducing new model versions. [Google for Developers, *Production ML systems: Deployment testing*](https://developers.google.com/machine-learning/crash-course/production-ml-systems/deployment-testing)
