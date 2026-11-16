# Choosing Model Complexity

We have a model that predicts which bike-share stations will run out of bikes the next morning. It misses some stations that do run out. Would a more complex model help, or are we leaving out information the current model could use?

Before moving to a more complex model, we should check whether a simple change to the model's inputs is sufficient. We should then examine whether the model's assumptions are appropriate for the task and whether a more complex model improves predictions enough to justify its additional cost.

## Check whether a simple feature is enough

When a model misses an important pattern, we should check whether its inputs make that pattern visible. For example, if an input combines measurements from several days into a single total, even a more complex model cannot tell when the events had occurred.

The bike-share example below shows how a simple change to an input can give the existing model information that the total hides.

> **Worked example: Using recent failed rentals to predict shortages**
>
> Assume that a technical team uses a model that relies on four days of bike-share app activity to predict whether a station will run out of bikes the next morning. The model uses the number of failed rental attempts, meaning the number of times customers attempted to rent a bike but found none available. The table below shows the daily counts for two stations, with day 4 being the most recent day before the prediction.
>
> | Station | Day 1 | Day 2 | Day 3 | Day 4 | Four-day total |
> | --- | ---: | ---: | ---: | ---: | ---: |
> | A | 2 | 0 | 0 | 0 | 2 |
> | B | 0 | 0 | 0 | 2 | 2 |
>
> If the four-day total is the only input to the model, both stations look identical to it. However, if the model also uses the previous day's count, it can distinguish between the two stations.

As the example above shows, adding a simple feature can help a model use information that would otherwise be lost through aggregation. We should test whether such changes improve the existing model before considering a more complex one. More generally, improving the model's inputs may be sufficient to achieve the desired performance for our task without increasing model complexity.

## Check the method’s assumptions

A model can have the inputs it needs and still make the wrong assumption about how to use them. For example, a simpler model may assume that the relationship between an input and the outcome is the same across groups. This assumption is worth checking when we have reason to expect those groups to behave differently.

Building on the bike-share example, the example below shows how the same count can be a stronger warning at one type of station than at another.

> **Worked example: Comparing shortage forecasts across station types**
>
> Continuing the bike-share example, suppose the technical team uses yesterday’s failed rentals to predict whether a station will run out of bikes the next morning. The table shows hypothetical shortage rates for commuter and residential stations.
>
> | Station type | Ran out next morning after no failed rentals | Ran out next morning after two failed rentals |
> | --- | ---: | ---: |
> | Commuter | 10% | 40% |
> | Residential | 10% | 15% |
>
> With no failed rentals the day before, both station types ran out on 10% of mornings. With two failed rentals the day before, the rate was 40% for commuter stations and 15% for residential stations.
>
> We can express this difference with two logistic regression models. Let $x$ be yesterday's failed-rental count, $g=1$ for a commuter station and $g=0$ for a residential station, and $p$ the predicted probability of running out the next morning. Logistic regression models the log odds, $\log(p/(1-p))$, as a linear function of the inputs and converts them into probabilities between zero and one using the sigmoid function.
>
> The simpler model uses:
>
> $$
> \log\left(\frac{p}{1-p}\right)=a+bx+cg.
> $$
>
> The coefficients $a$, $b$, and $c$ are learned from training data. The station-type term $cg$ allows different starting risks, but each additional failed rental changes the log odds by the same amount $b$ for both station types.
>
> The more flexible model adds one interaction term:
>
> $$
> \log\left(\frac{p}{1-p}\right)=a+bx+cg+dxg.
> $$
>
> For residential stations, $g=0$, so the count has weight $b$. For commuter stations, $g=1$, so its weight is $b+d$. The extra coefficient $d$ lets the relationship differ by station type while keeping one model.
>
> In the table, both groups start at 10 percent when $x=0$. Matching those starting probabilities forces $c=0$. The simpler model would then predict the same probability for both groups at $x=2$, so it cannot reproduce both 40 percent and 15 percent. The interaction term in the more flexible model allows for that difference. Therefore, it is worth testing whether the more flexible model improves predictive performance.

As the example above shows, adding complexity can be worth testing when it lets the model represent a specific pattern the simpler model misses.

## Test the value of added complexity

When a simpler model misses a useful pattern, we can start by adding enough flexibility to capture it. If a more complex model improves predictions further, we then need to determine whether the additional improvement justifies the added complexity and its associated costs.

The example below shows how a small change to a model can deliver most of the benefit of a more complex approach.

> **Worked example: Choosing how much flexibility to add**
>
> Continuing the bike-share example, the technical team wants to predict which stations will run out of bikes the next morning. The team trains three models on the same earlier records, using yesterday's failed-rental count and station type as inputs. They then compare them over the same four weeks of mornings excluded from training and model selection. Each model flags the same number of stations each morning. The team counts how often a station runs out of bikes without being flagged.
>
> | Model | How it uses yesterday's failed-rental count | Missed shortages |
> | --- | --- | ---: |
> | Logistic regression with a shared relationship | Uses the count in the same way for commuter and residential stations | 75 |
> | Logistic regression with an interaction term | Allows the count to have a different weight for commuter and residential stations | 65 |
> | Ensemble of decision trees | Can capture threshold effects in the count that differ by station type | 64 |
>
> The logistic regression model with an interaction term allows the count to have a different weight for each station type, reducing missed shortages by ten over four weeks compared with the simpler logistic regression model. The tree ensemble offers even more flexibility, as it can capture how the relationship between failed rentals and shortage risk changes at different count values within each station type. However, this additional flexibility reduces missed shortages by only one more, while requiring the technical team to tune additional hyperparameters, such as the number and depth of the trees, and explain the more complex model to stakeholders. The team therefore chooses to proceed with the logistic regression model with an interaction term, because the small improvement offered by the tree ensemble does not justify the additional complexity and work involved.

As the example above shows, we should always evaluate whether the improvement offered by a more complex model justifies its additional costs. A relatively simple change may already capture most of the potential benefit, making further complexity unnecessary.

## Further reading

- **Check whether a simple feature is enough.** The example shows how lagged values and summaries over different time windows give a model different views of the same event history. [scikit-learn, *Lagged features for time series forecasting*](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html)
- **Check the method’s assumptions.** The example shows how an interaction in logistic regression lets the relationship between a numerical input and a predicted probability differ across groups. [UCLA Office of Advanced Research Computing, *How can I understand a categorical by continuous interaction in logistic regression?*](https://stats.oarc.ucla.edu/stata/faq/how-can-i-understand-a-categorical-by-continuous-interaction-in-logistic-regression-stata-12/)
- **Test the value of added complexity.** Rule 16 explains why the benefit of a more complex model should be weighed against the work of updating and verifying it over time. [Martin Zinkevich, *Rules of Machine Learning*, Rule 16](https://developers.google.com/machine-learning/guides/rules-of-ml)
