# Designing Experiments

Assume that we want to design an experiment which will determine whether a new model predicts weekly demand better than the currently used method. How should we design the experiment so we can trust the result?

We would need to define what we want to learn, choose a meaningful baseline, and test whether the model generalizes to the situations where we plan to use it. We would also need to make the evidence interpretable and decide when we have enough evidence to stop experimenting.

## Define what you want to learn

The first step in designing an experiment is to define what we want to learn. If we want to know whether a new forecasting method reduces error, we should compare it with the current method. If we want to know whether a specific change reduces error, we should compare two versions of the same method, with and without that change.

The example below applies this distinction to a weekly demand forecast.

> **Worked example: Asking two questions about the same forecast**
>
> Every Friday, a retailer’s planning team forecasts demand for the following week to decide how much stock each store will need. Over the next eight weeks, the retailer’s technical team tests whether a new model reduces average absolute forecast error. They compare the model’s forecasts with the planning team’s forecasts for the same stores and weeks. Both methods use only information available by the Friday deadline.
>
> The technical team also tests whether adding the promotion calendar as input information to the model reduces forecast error. They train two versions using the same model type and training procedure. One uses the promotions known by Friday, and the other leaves them out. The technical team evaluates both versions on the same stores and weeks. Because the promotion calendar is the only change, the comparison isolates its effect on forecast error.
>
> | Question | Comparison | What stays fixed? |
> | --- | --- | --- |
> | Does the new model improve on the current method? | New model versus the planning team's forecast | Evaluation stores and weeks, forecast deadline, and error measure |
> | Does the promotion calendar improve this model? | The same model with and without the promotion calendar | Training records, other inputs, model type, training procedure, and evaluation conditions |
>
> The first comparison tells us whether the new model improves on the current method, but not how much the promotion calendar contributes, since the methods may differ in other ways. The second comparison isolates the contribution of the promotion calendar by keeping everything else fixed.

As the example above shows, what we want to learn determines what the experiment should compare. A comparison can support a decision about the whole system or explain the contribution of a specific change, depending on what we hold fixed.

## Choose a meaningful baseline

When designing an experiment, we need to choose a baseline that answers the question we are interested in. If we want to know whether the model improves on a simple rule, such as a constant forecast, we should use that rule as our baseline. If we want to decide whether the model should replace the current forecasting method, our baseline should be the forecast we currently use. If obtaining that forecast is difficult or costly, we can use a defensible approximation in its place instead.

The example below shows how the same model can look much better against a simple baseline than against the forecast it would actually replace.

> **Worked example: Comparing with the planning team's forecast**
>
> Continuing the retail demand forecast example, assume that actual demand at one store is 120 units for the week. The table below shows how far each forecast was from actual demand.
>
> | Method | Forecast (units) | Absolute error (units) |
> | --- | ---: | ---: |
> | Constant forecast | 90 | 30 |
> | Planning team’s forecast | 110 | 10 |
> | New model | 116 | 4 |
>
> To measure the new model’s improvement, we subtract its absolute error from the baseline’s absolute error. We can see that the model reduces error by 26 units compared with the constant forecast and by just 6 units compared with the planning team's forecast. The smaller gain is the one the retailer should actually weigh when deciding whether to switch methods.

As the example above shows, the choice of baseline determines what the improvement tells us. When evaluating a replacement, compare it with the method currently in use under the same operating conditions to get meaningful results.

## Test the generalization you need

A data split determines what kind of generalization we test. To forecast future weeks, we should train on earlier weeks and evaluate on later ones. To forecast at new stores, we should leave entire stores out of training. If we need both, we should train on earlier weeks from one set of stores and evaluate on later weeks from a different set of stores. Additionally, a random split may be appropriate when the observations are reasonably exchangeable and the test reflects how we plan to use the model.

The example below shows why testing on new weeks at a familiar store answers a different question from testing on a store the model has never seen.

> **Worked example: Forecasting for existing and new stores**
>
> Continuing the retail demand forecast example, assume that we have eight weeks of sales data from two stores, A and B. For simplicity, assume also that both stores had enough stock to meet all demand during these weeks, so sales are equivalent to demand in this example.
>
> We use two experimental setups to test how well a model forecasts demand at an existing store and at a new store. In both setups, we train on data from weeks 1–4 and forecast demand at Store B for weeks 5–8. The test data is the same in both setups. The training data differs in whether it includes Store B or not. We demonstrate this in the table below.
>
> | Experimental setup | Training data used to fit the model | Test data used to score the forecasts |
> | --- | --- | --- |
> | Forecast for an existing store | Weeks 1–4 from Stores A and B | Weeks 5–8 from Store B |
> | Forecast for a new store | Weeks 1–4 from Store A only | Weeks 5–8 from Store B |
>
> In the first setup, the model can learn from Store B’s first four weeks of sales and use that history when making forecasts. In the second setup, we treat Store B as if it has yet to open, so we exclude its sales history from both training and forecast inputs. In both setups, we use Store B’s actual sales from weeks 5–8 only to calculate forecast errors for evaluation purposes.
>
> As a side note, demand during a store’s opening weeks may differ from demand at an established store. However, if we have no historical data from actual store openings, holding out Store B in the second setup gives us a practical way to test forecasting without local sales history. The limitation is that the resulting forecast errors may differ from those we would see at an actual opening. Let us assume that in this case they wouldn't differ.
>
> To summarize, the two experimental setups answer different questions. The first setup tells us how well the model forecasts demand for an existing store, whereas the second setup tells us how well the model forecasts demand for a new store. Even though both setups evaluate predictions for the same store and weeks, their results reflect different kinds of generalization.

As the example above shows, we need to choose a split that reflects how we plan to use the model. When reporting the experimental result, we should explicitly state which future observations the test set is meant to represent.

## Make the evidence interpretable

When reporting an experimental result, we should show how performance varies across the conditions that matter to the decision. For example, an average can summarize the overall result while hiding a drop in performance under conditions where errors are especially costly.

The example below shows how separating ordinary weeks from promotion weeks changes what we learn from a forecast comparison.

> **Worked example: Comparing forecasts during promotions**
>
> Continuing the retail demand forecast example, assume that the technical team compares the new model with the planning team's forecast at one store over four weeks. One of those weeks includes a promotion campaign. Forecast accuracy matters especially during promotion campaigns because the retailer orders extra stock and needs to decide how much to buy.
>
> | Week | Conditions | Planning team's forecast absolute error | New model absolute error | Reduction in absolute error |
> | --- | --- | ---: | ---: | ---: |
> | 1 | Ordinary week | 20 | 8 | 12 |
> | 2 | Ordinary week | 18 | 8 | 10 |
> | 3 | Ordinary week | 16 | 8 | 8 |
> | 4 | Promotion week | 30 | 40 | −10 |
> | **Average** | **All four weeks** | **21** | **16** | **5** |
>
> We can see in the table above that the new model reduces absolute error by 5 units per week on average. However, although the new model performs better in all three ordinary weeks, its error is 10 units higher than the planning team's forecast during the promotion week. If the retailer is considering replacing the planning team's forecast for all weeks, this result gives the technical team a reason to check whether the same pattern holds across more promotion weeks.

As the example above shows, reporting results by operating condition helps us see where the overall improvement holds and where we need more evidence before deciding how to use the model.

## Know when to stop

When considering whether to run another experiment, we should ask what we would do differently depending on its result. If the likely results would all lead to the same decision, we have enough evidence to stop experimenting.

The example below shows how a threshold can help us decide whether another test is worth running.

> **Worked example: Deciding when we have enough evidence**
>
> Continuing the retail demand forecast example, assume that the retailer is trying to decide whether to use the new model during ordinary weeks. The switch is worth making only if the new model reduces average absolute forecast error by at least **5 units**.
>
> Note that the ranges below are illustrative estimates of uncertainty about the average improvement, not the smallest and largest errors observed. They are assumed for this example and are not calculated from the four-week table in the previous example. In practice, the team would need enough evaluation data and a method that accounts for dependence between stores and weeks to compute these ranges.
>
> | Evidence | Plausible reduction in average error | What the retailer does |
> | --- | --- | --- |
> | After the first test | 2–8 units | **Keep testing.** The gain could be below or above 5 units. More evidence could change the decision. |
> | After testing the same model on more ordinary weeks | 1–4 units | **Stop and keep the current forecast method.** Even a gain of 4 units would be too small to justify switching. |
>
> As we can see above, the first test leaves the decision open, whereas the second test gives the retailer enough evidence to decide. Whether the gain is closer to 1 unit or 4 units, the retailer would still keep the current forecast method, so collecting more evidence about this candidate is unlikely to change the replacement decision.

As the example above shows, we should stop experimenting when the remaining uncertainty is unlikely to change our decision. Another test might give us a more precise estimate, but that extra precision is hard to justify if we would spend time and resources only to make the same decision.

## Further reading

- **Define what you want to learn.** The guidelines describe how to test a component’s contribution by removing one component at a time. [NeurIPS, *Guidelines for Writing a Good NIPS Paper*](https://neurips.cc/Conferences/2016/PaperInformation/EvaluationCriteria)
- **Choose a meaningful baseline.** The guide explains how the current solution can serve as a baseline for evaluating a new model and how to choose a simple baseline when no solution exists. [Google for Developers, *Experiments*](https://developers.google.com/machine-learning/managing-ml-projects/experiments)
- **Test the generalization you need.** The guide compares ordinary, group-based, and time-ordered splits and explains when to use them. [scikit-learn, *Cross-validation: evaluating estimator performance*](https://scikit-learn.org/stable/modules/cross_validation.html)
- **Make the evidence interpretable.** The paper proposes reporting model performance separately under conditions relevant to its intended use. [Margaret Mitchell and colleagues, *Model Cards for Model Reporting*](https://research.google/pubs/model-cards-for-model-reporting/)
- **Know when to stop.** The report introduces value of information analysis, which helps determine whether collecting more evidence could improve a decision enough to justify the cost of the research. [Elisabeth Fenwick and colleagues, *Value of Information Analysis for Research Decisions—An Introduction*](https://www.ispor.org/heor-resources/good-practices/article/value-of-information-analysis-for-research-decisions-an-introduction)
