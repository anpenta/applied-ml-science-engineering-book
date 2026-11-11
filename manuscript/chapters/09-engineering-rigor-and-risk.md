# Engineering Rigor and Risk

A technical team at a public library system is experimenting with a model to forecast book requests. What would change if its libraries began relying on those forecasts to decide how many copies to transfer between locations?

As more people begin relying on the forecasts, failures can have greater consequences. We therefore need to choose engineering practices that reflect those consequences, test both the software and the predictions, and make failure states explicit. We also need to check that the system responds to those failures as intended.

## Match engineering practices to risk

The appropriate engineering practices depend on how the code and its results are used and how long they will be maintained. Even a one-off experiment needs checks that protect its conclusions. However, as its code or results become more widely used, additional risks need to be addressed.

The example below shows how a change in use can justify additional engineering controls.

> **Worked example: Taking a library forecast beyond the notebook**
>
> A technical team uses an exploratory notebook to forecast next week's book reservation requests for each title at each library branch of a public library system. Over time, other teams begin using their data preparation code, and the forecasts become part of a daily service that branches use to plan book transfers.
>
> | Use | Possible failure and consequence | Appropriate protection |
> | --- | --- | --- |
> | An initial feasibility experiment | Duplicate records inflate request counts and make the experiment misleading. | Check that each combination of title, branch, and forecast week appears once, and save the data extract so the result can be checked. |
> | Data preparation code shared with other teams | A change to the weekly aggregation silently changes the inputs used by several models. | Document what the function returns and add a regression test that checks a small set of reservation records against known weekly counts. |
> | A daily service used by branches to plan transfers | An unavailable forecast leaves titles out of the transfer plan, which staff mistake for a complete plan. | Make unavailable forecasts visible and test that the staff-facing system marks the affected titles for attention. |
>
> The duplicate-record check is useful from the first experiment. Testing the staff-facing response becomes necessary when staff begin depending on the plan. If the notebook remains a one-off feasibility experiment, building that operational response would serve no immediate purpose.

As the example above shows, additional engineering controls should address identifiable failures and their consequences. Our goal should not be to apply as many engineering practices as possible, but to choose those that address the risks that matter.

## Test software and predictive quality

Software tests and predictive evaluation answer different questions. Software tests can check that a service performs its calculations correctly. Evaluation on held-out records tells us how well the model predicts in the setting we care about.

The example below shows how a correct calculation can still lead to a poor decision when the forecast is wrong.

> **Worked example: Checking a transfer calculation and a forecast**
>
> Continuing the library example, suppose that the technical team builds a software application that uses forecasts to recommend how many additional copies each library branch should receive. For simplicity, assume each request needs one copy for the week and that transfers can arrive before the week begins.
>
> The application calculates the number of additional copies by subtracting available copies from forecast requests. If the result is negative, it recommends zero. To test this calculation, the technical team supplies two inputs, the number of available copies and the forecast number of requests, and checks whether the application returns the expected result. Consider the two test cases below.
>
> | Available copies | Forecast requests | Expected additional copies |
> | --- | --- | --- |
> | 3 | 5 | 2 |
> | 5 | 3 | 0 |
>
> For both test cases, the test is passing. The application calculates the correct number of additional copies for the supplied inputs. However, the test does not tell us whether the forecasts are accurate.
>
> Consider what happens when the application uses an inaccurate forecast:
>
> | | Number of copies |
> | --- | ---: |
> | Available copies | 3 |
> | Forecast requests | 5 |
> | Actual requests | 2 |
> | Recommended additional copies | 2 |
> | Additional copies actually needed | 0 |
>
> The application correctly recommends two additional copies based on the forecast. However, the library branch already has enough copies to meet actual requests. The calculation is correct, but the forecast leads to an unnecessary transfer.
>
> Software tests cannot reveal this forecasting problem because they check the calculation using supplied inputs. To evaluate predictive quality, the technical team must compare the model's forecasts with actual request counts across held-out weeks.
>
> Conversely, accurate forecasts would not reveal an error in the application's calculation. That requires software testing.

As the example above shows, correct software behavior and useful predictions require separate evidence. Passing one set of checks does not remove the need for the other.

## Make failure states explicit

When a system produces a result, we need to know whether it was calculated under normal conditions or whether something went wrong. Otherwise, we risk interpreting a fallback value as a valid result.

The example below shows why a system needs to communicate not only its results, but also the conditions under which they were produced.

> **Worked example: Distinguishing a recommendation from a fallback**
>
> Continuing the library example, imagine that the technical team wants their application to handle situations where a forecast is unavailable. The library has approved a fallback procedure: make no new transfer and flag the affected title for staff review.
>
> This creates a problem. A recommendation of zero additional copies could mean either that the forecast indicates no additional copies are needed or that the application has used the fallback. The technical team therefore decides to return both the number of additional copies and a status indicating how the result was obtained.
>
> ```python
> from dataclasses import dataclass
>
>
> @dataclass(frozen=True, slots=True)
> class Recommendation:
>     additional_copies: int
>     status: str
>
>
> def recommend_copies(
>     available_copies: int,
>     forecast_requests: int | None,
> ) -> Recommendation:
>     if forecast_requests is None:
>         return Recommendation(0, "fallback")
>
>     additional = max(forecast_requests - available_copies, 0)
>     return Recommendation(additional, "predicted")
>
>
> assert recommend_copies(3, 2) == Recommendation(0, "predicted")
> assert recommend_copies(3, None) == Recommendation(0, "fallback")
> ```
>
> Both of the cases below return zero additional copies, but they have different meanings.
>
> | Result | Meaning | Appropriate response |
> | --- | --- | --- |
> | `Recommendation(0, "predicted")` | The forecast indicates that no additional copies are needed. | No transfer is necessary. |
> | `Recommendation(0, "fallback")` | The forecast is unavailable, so the application defers the transfer. | Flag the title for staff review. |

As the example above shows, a numerical result alone may not tell us how to interpret it. We should make failure states explicit and ensure that each one has a clearly defined meaning and an appropriate response.

## Test how the system handles failures

Returning the correct status is only one part of handling a failure. We also need to test that the rest of the system responds as intended. A function can pass its own tests while other parts of the system ignore its status and handle the result incorrectly.

The example below shows why testing individual components is not always enough to verify that a system handles failures correctly.

> **Worked example: Testing how the application handles failures**
>
> Continuing the library example, assume now that the technical team wants to verify that the application handles unavailable forecasts correctly. The recommendation function already returns a status indicating whether the result came from a forecast or a fallback. However, the application must also use that status correctly when preparing the transfer plan.
>
> The technical team tests the application using predetermined inputs and checks the resulting transfer plan.
>
> | Case introduced by the test | What the test should verify |
> | --- | --- |
> | The forecast is five requests, and the library branch has three available copies. | The transfer plan recommends receiving two additional copies. |
> | The forecast is two requests, and the library branch has three available copies. | The transfer plan recommends no additional copies without flagging the title for review. |
> | The forecast is unavailable, so the fallback is used. | The transfer plan recommends no new transfer and flags the title for staff review. |
>
> Suppose that the recommendation function correctly returns `Recommendation(0, "fallback")`, but the application ignores the status and displays "No additional copies needed." In this case, the function's tests would pass because it returned the expected result. However, the application test would fail because the title was not flagged for staff review.
>
> Using the application test, the technical team can identify a problem that would have gone unnoticed if they had tested only the recommendation function.

As the example above shows, testing individual components does not guarantee that the system behaves correctly as a whole. We need to test how components work together and verify that the system responds to failures as intended.

## Further reading

- **Match engineering practices to risk.** The guidance shows how to identify a system’s context, dependencies, and potential consequences before choosing controls. [National Institute of Standards and Technology, *AI Risk Management Framework Playbook*, “Map”](https://airc.nist.gov/airmf-resources/playbook/map/)
- **Test software and predictive quality.** The rubric covers distinct checks for data, model development, infrastructure, and monitoring in production machine learning. [Eric Breck and colleagues, *The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/)
- **Make failure states explicit.** The chapter discusses deliberate responses to overload, including rejecting work and returning degraded results. [Google, *Site Reliability Engineering*, “Handling Overload”](https://sre.google/sre-book/handling-overload/)
- **Test how the system handles failures.** The chapter covers ways to test system behavior under failure conditions as well as normal execution. [Google, *Site Reliability Engineering*, “Testing for Reliability”](https://sre.google/sre-book/testing-reliability/)
