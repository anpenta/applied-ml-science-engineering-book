# Testing Operational Feasibility

A photo search model runs quickly on a laptop during an experiment. But will a service using that model respond just as quickly when breaking news brings a surge of searches from across the newsroom?

To answer the question, we need to define the workload, measure the full path from request to usable result, and check capacity under load. We can then use this evidence to decide what to reuse and where the design needs to change.

## Define the workload

Whether a system can meet its performance requirements depends on how and when people use it. An overnight batch must finish processing within a deadline, while an interactive service must respond quickly even when many requests arrive at once.

The example below shows how different workloads lead to different performance requirements.

> **Worked example: Defining the workload for photo search**
>
> Let us assume that a newsroom uses a system to search its photo archive. The system has two workloads with different performance requirements.
>
> | Workload | How it is used | Performance requirement |
> | --- | --- | --- |
> | Indexing photos | The system processes the photo archive overnight to prepare it for searching the next day. | The entire job must finish before the morning shift. |
> | Searching photos | Editors search the archive throughout the day, sometimes simultaneously when breaking news occurs. | At least 95 percent of searches must return results within 120 milliseconds, even when 80 searches arrive per second. |
>
> The technical team must therefore test the two workloads differently. For indexing, they need to measure whether the system can process the full archive before the deadline. For searching, they need to measure response times while many editors are using the system simultaneously.
>
> The same system can therefore meet the performance requirements of one workload while failing those of another.

As the example above shows, different uses of the same system can require different performance measures. We should define the workload before deciding what to measure and what targets to set, even if those targets are initially provisional.

## Measure the full path from request to result

Asymptotic complexity tells us how computational work grows with input size under specified assumptions. Benchmarks tell us how long an implementation takes for particular inputs and hardware. However, neither necessarily tells us how long users wait for a result. To determine that, we should measure the total response time and examine how much each stage of processing a request contributes to it.

The example below shows why making the model faster may not be enough to meet the response-time target.

> **Worked example: Finding where a search spends its time**
>
> Continuing the photo-search example, assume that the technical team measures how long each stage of a photo search takes. The stages run sequentially, with the following results for one search.
>
> | Stage | Time in milliseconds |
> | --- | ---: |
> | Prepare the query | 10 |
> | Run the model | 20 |
> | Retrieve candidates from the archive service | 80 |
> | Rank the results and prepare the response | 15 |
> | Browser processing and communication with the search service | 25 |
> | **Total time until results are displayed** | **150** |
>
> The model takes only 20 milliseconds, but the complete search takes 150 milliseconds. Even if the technical team halves the model's runtime, the total would only decrease to 140 milliseconds. Retrieving candidates from the archive service takes considerably longer, making it a more promising stage to investigate.
>
> As a side note, this example is simplified for illustrative purposes. Measuring a single search is not enough to determine whether the system meets its performance target. The technical team must also measure response times across many searches, including periods of high demand. They can then determine whether at least 95 percent of searches return results within the target of 120 milliseconds.

As the example above shows, the performance of an individual component does not necessarily reflect the performance of the entire system. We should measure end-to-end performance to determine whether the system meets its requirements, and examine individual components to identify where improvements are needed.

## Check capacity under load

Even if individual requests are processed quickly, they can still accumulate in a queue when requests arrive faster than the system can handle them. The number of requests a system can process depends on the work each request requires and how many requests it can handle concurrently.

The example below shows how a system can develop a growing backlog despite processing individual requests quickly, and how increasing its capacity can introduce memory constraints.

> **Worked example: Checking the model worker at peak demand**
>
> Continuing the photo-search example, assume that the service uses a queue and a single worker to run the model, processing one search at a time. Each search takes 20 milliseconds of model processing time, so the worker can handle up to 50 searches per second. For simplicity, assume that all other stages can keep up with demand.
>
> During breaking news, the service receives 80 searches per second. Since the worker can only process 50, another 30 searches are added to the queue every second. After 10 seconds of sustained demand, 300 searches are waiting to be processed, assuming the queue was initially empty. Even though the model processes each search quickly, users experience increasing delays.
>
> The technical team considers adding another worker to increase capacity. However, each worker requires 600 megabytes of memory to load the model, while the service has a total memory budget of 1,000 megabytes. Two workers would require 1,200 megabytes for the models alone, exceeding the available memory.
>
> To increase the number of workers without exceeding the available memory, the technical team must therefore consider alternatives, such as increasing the memory budget or reducing the model's memory requirements.

As the example above shows, a system can process individual requests quickly but still fail to keep up with demand. We should test the system under realistic workloads, measuring both response times and resource use.

## Decide what to reuse

Using an existing library or service can reduce development and maintenance effort, provided the library or service meets the system's requirements. We should compare the performance, limitations, and integration costs of existing solutions with those of building our own solution.

The example below shows how evaluating an existing library against explicit requirements can help us decide whether to reuse it.

> **Worked example: Deciding whether to reuse a search library**
>
> Continuing the photo-search example, the technical team needs a way to search the photo archive efficiently. They consider using an existing search library instead of building a custom solution.
>
> The technical team tests the library against the system's requirements using a representative photo archive and up to 80 searches per second. The following table shows hypothetical results.
>
> | Requirement | Result |
> | --- | --- |
> | At least 95 percent of searches return results within 120 milliseconds | 95th-percentile response time of 110 milliseconds: passes |
> | Total memory use stays within 2,000 megabytes | Peak use of 1,800 megabytes: passes |
> | Complete index updates before the morning shift | Passes |
> | Return only photos editors are allowed to access | Passes after integrating access checks |
>
> The library meets the tested requirements, although the team must integrate access checks and maintain the index updates. Since this work is less demanding than building and maintaining a custom search solution, the team decides to reuse the library.

As the example above shows, reusing an existing solution depends on whether it meets our requirements and how much additional work it requires. We should evaluate both before deciding whether to build our own custom solution.

## Further reading

- **Define the workload.** The chapter explains how to select indicators and objectives that reflect how a service is used. [Google, *Site Reliability Engineering*, “Service Level Objectives”](https://sre.google/sre-book/service-level-objectives/)
- **Measure the full path from request to result.** The chapter compares monitoring from the user’s perspective with monitoring internal components and discusses latency distributions. [Google, *Site Reliability Engineering*, “Monitoring Distributed Systems”](https://sre.google/sre-book/monitoring-distributed-systems/)
- **Check capacity under load.** The article explains how sustained load and failures can grow a backlog and what design choices help systems recover. [David Yanacek, *Avoiding Insurmountable Queue Backlogs*](https://aws.amazon.com/builders-library/avoiding-insurmountable-queue-backlogs/)
- **Decide what to reuse.** The guidance discusses choosing technologies and managed services in light of workload requirements and tradeoffs. [Amazon Web Services, *AWS Well-Architected Framework*, “Architecture selection”](https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/architecture-selection.html)
