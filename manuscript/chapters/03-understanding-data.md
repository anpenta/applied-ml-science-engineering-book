# Understanding Data

Let's say that a dataset passes every check in our schema. Is that enough to trust it when training a model to predict pump failures?

To trust the dataset, we need to know when the features become available, what the data records represent, and how the labels were made. We also need to understand what unusual patterns in the data mean before deciding how to handle them.

## Check when features become available

A feature must always be available at the time of prediction. To check that, we need to know when the event occurred, when it was recorded, and when the prediction system could access the record.

The example below illustrates why recording a reading before prediction time does not guarantee that it is available in time.

> **Worked example: Reconstructing the data available at 08:00**
>
> Assume that we want to predict at 08:00 each day which pumps will fail within the next 24 hours. A historical extract contains these records for the same pump on the same day.
>
> | Record | Event time | Recorded at | Available to the prediction system | Usable at 08:00? |
> | --- | --- | --- | --- | --- |
> | First temperature reading | 07:30 | 07:31 | 07:35 | Yes |
> | Second temperature reading | 07:50 | 07:51 | 08:10 | No |
> | Inspection result | 17:00 | 17:05 | 17:10 | No |
>
> We can see above that the second temperature reading was taken before the prediction time but arrived too late to have been used for prediction. Additionally, the inspection took place after the prediction time, so its result was also unavailable, even if it is a good predictor of failure in historical data. Both records can pass dataset schema checks despite being unavailable when the prediction would have been made.
>
> To reconstruct what the model would have seen at 08:00, we should use only the first reading. The same cutoff applies to derived features. For example, we might compute the morning’s maximum temperature using only readings that had already reached the prediction system by 08:00.

As the example above shows, we must exclude the late reading both as a direct input and from the calculation of the morning’s maximum temperature. When reconstructing historical features, we need to check whether each input was available to the prediction system at the intended prediction time.

## Check what the data represent

Before preparing data for modeling, we need to determine what each row represents and how its fields were measured. A row per pump prediction, a row per inspection, and a row per sensor reading describe different observations. Confusing these can produce incorrect training examples even when every column passes schema validation.

The example below shows what can go wrong when we attempt to match temperature readings with failure outcomes.

> **Worked example: Matching readings to pump failures**
>
> Continuing the pump-failure example, suppose we are preparing training data for a model that predicts pump failures at 08:00.
>
> The first table shows one temperature value per pump, computed from readings available to the prediction system by 08:00.
>
> | Pump | Temperature (°C) |
> | --- | ---: |
> | B | 60 |
> | A | 80 |
>
> The second table shows whether each pump failed within the following 24 hours.
>
> | Pump | Failed within 24 hours? |
> | --- | --- |
> | A | Yes |
> | B | No |
>
> The two tables above list the same pumps in different orders. If we combine the rows by position, each pump will receive the other pump’s failure label. We demonstrate this in the table below. Note that the last column shows the actual recorded outcome for comparison.
>
> | Pump | Temperature (°C) | Failure label assigned by row position | Recorded outcome |
> | --- | ---: | --- | --- |
> | B | 60 | Yes | No |
> | A | 80 | No | Yes |
>
> The resulting table has the expected shape and every value is valid, yet both labels are attached to the wrong pumps.
>
> In this example, joining on the pump identifier instead would give the correct matches, as we only have one prediction time per pump. Alternatively, if the data had contained multiple prediction times per pump, we would have joined on both the pump identifier and the prediction time. Before joining, we would have verified that each combination appears at most once in each table.

The example above shows why we need to verify that a join preserves the observations we intend to model.

Beyond matching records correctly, we also need to understand what their values represent. Assume that a sensor upgrade changes temperature reporting from Celsius to Fahrenheit. A reading of 176 degrees Fahrenheit represents the same temperature as 80 degrees Celsius, but the values appear different without knowledge of their measurement units. Since both values satisfy a numeric schema, we could mistake a change in recording conventions for a change in operating conditions if we fail to check those units.

Schema validation alone cannot tell us whether records have been matched correctly or measurements have been interpreted consistently. We need to understand how the data were collected and verify that these assumptions hold before preparing them for modeling.

## Check how labels were made

A label should always represent the outcome we want to predict. However, the meaning of a label depends on how it was produced, not simply on its name or data type. Before using labels for training or evaluation, we need to understand what was actually recorded in the data.

The example below shows how different records can produce labels with different meanings.

> **Worked example: What counts as a pump failure?**
>
> Continuing the pump-failure example, suppose we want to predict whether a pump will fail within the next 24 hours. Our dataset contains a binary column called `failure`, but different data collection procedures could have produced that column.
>
> | How the label was produced | What it actually records |
> | --- | --- |
> | A maintenance record confirms that the pump stopped working | An observed pump failure |
> | A technician replaced the pump because it appeared likely to fail | A preventive maintenance action |
> | A temperature alarm exceeded a predefined threshold | An alarm event |
>
> These records describe different events. A pump can trigger an alarm without failing, and a technician may replace a pump before it fails. Treating either event as a confirmed failure would change what the model learns to predict.
>
> To construct the label from maintenance records, we would need to identify confirmed failures and determine when they occurred. We should then label each prediction according to whether a confirmed failure occurred in the following 24 hours.

As the example above shows, if our only record is a temperature alarm, the labels tell us whether the alarm went off. Consequently, we can only evaluate predictions of alarms with those labels. Evaluating predictions of pump failures instead requires records that tell us when the pumps actually failed.

## Diagnose the data problem

Data validation can identify unexpected patterns, but it cannot always determine whether they make the data unsuitable for the prediction task. A validation warning is therefore a reason to investigate, as the same warning may have different causes that require different responses.

The example below illustrates this distinction.

> **Worked example: Investigating missing sensor readings**
>
> Continuing the pump-failure example, suppose we predict pump failures at 08:00 each morning. Historically, the prediction system has a temperature reading for almost every pump by that time. One morning, data validation reports that no reading is available to the prediction system at 08:00 for 30% of the pumps.
>
> There are several possible explanations:
>
> | Possible cause | What it means | Appropriate response |
> | --- | --- | --- |
> | A data pipeline delay | Readings exist but have not reached the prediction system | Investigate the pipeline and determine whether predictions can proceed with the available data |
> | Sensors report only while pumps are running | More pumps may be switched off than usual | Check operating records and determine whether this explains the missing readings and whether the model can handle them |
> | Sensors have stopped working | Measurements that would normally be available for prediction are missing | Investigate the affected sensors and determine whether predictions remain reliable
>
> The same validation warning can therefore indicate a data pipeline problem, meaningful operating behavior, or missing information that compromises predictions.
>
> Automatically rejecting every pump without a reading would treat these situations as equivalent. Instead, we need to identify the cause and evaluate its consequences for the prediction task before deciding what to do.
>
> Suppose the investigation finds that all affected pumps were switched off before 08:00 and that their sensors report only while running. The missing readings are expected under these conditions, so repairing the data pipeline would not address the cause. The technical team checks whether switched-off pumps were represented in training and whether predictions remain reliable for them. Until that is known, it flags the affected pumps for review rather than filling in a temperature and treating the result as an ordinary prediction.

In the example above, the missing readings do not indicate a data pipeline failure but reflect how the pumps operate, requiring a different response. More generally, understanding the causes of validation warnings helps us determine whether the available data can still support reliable predictions and how to respond appropriately.

## Further reading

- **Check when features become available.** The guide shows how to reconstruct historical feature values and explains why event timestamps alone can admit values that were backfilled or corrected later. [Feast, *Point-in-time joins*](https://docs.feast.dev/getting-started/concepts/point-in-time-joins)
- **Check what the data represent.** The proposed questions cover what observations represent, how they were collected, and how they were processed. [Timnit Gebru and colleagues, *Datasheets for Datasets*](https://www.microsoft.com/en-us/research/publication/datasheets-for-datasets/)
- **Check how labels were made.** Section 4.1 describes how models trained with heuristic labels were evaluated on a separate, hand-labeled test set. [Alexander Ratner and colleagues, *Snorkel: Rapid Training Data Creation with Weak Supervision*](https://link.springer.com/article/10.1007/s00778-019-00552-1)
- **Diagnose the data problem.** The paper shows how a production validation system flags missing features and explains why alerts need enough context for engineers to investigate the cause. [Eric Breck and colleagues, *Data Validation for Machine Learning*](https://research.google/pubs/data-validation-for-machine-learning/)
