# ow-challenge

## Running the app

Install uv (package manager for python): https://docs.astral.sh/uv/getting-started/installation/

Install, test, and run the app:
```bash
make install
make test
make run
```

## Major decisions

- FastAPI for the API (alternatives: Flask (slower), Django (solves different problems))
- Caching responses from the API or calculations: No, because the number of messages is small, and the use case is unlikely to repeatedly hit the same report more than once every day, and there aren't too too many messages in the same endpoint.
- Containerization/deployment: Not yet, not in scope.
- Package manager: uv because I've had trouble with poetry and scientific/ml packages, and uv is great.
- Logging/Monitoring/Alerting: Not yet, not in scope.
- Batch text process vs. per-message processing: Batch processing is probably much more efficient, and not too hard to implement.
- Pandas vs. PyTorch for batch text processing: PyTorch is faster. See below.

### Pandas vs PyTorch for batch text processing

I haven't used PyTorch before, and this seemed like a good opportunity to try it out. The environment variable `CREDIT_CALCULATION_METHOD` can be set to `pandas` or `pytorch` to choose which implementation to use.

```bash
make perf
Running performance comparison...
PYTHONPATH=$PYTHONPATH:src/ uv run python tests/compare_performance.py
PyTorch Duration: 1.53 seconds
Pandas Duration: 5.50 seconds
```

## LLM usage

ChatGPT canvas chat: https://chatgpt.com/share/6741db7b-bc10-800f-bfc4-c609774d8c5d
Cursor IDE used.

## technical project

Lantum is a marketplace for locums (freelance doctors) to work at practices and hospitals. The main benefit of the platform is automating much of the admin work on both sides that comes with locum work. A major portion of the admin work is billing and payments. A year after its series-A funding the ops and finance team still had to hand-manage all of this, and as the company scaled, it was beginning to burn them out.

The system we were working in had fairly significant data modelling debt, especially in the modelling of shifts, which are the core entity that billing and payments come from. Billing and payments has notoriously deep business logic in every industry, and ours was no different. Billing and payments was extremely visible to customers on both sides, as well as within the company.

I was the tech lead of the project, with two mid-junior developers, and I was responsible for design and delivery. There was also a product manager and a financial analyst that I helped upskill into a data analyst role. We made aggressive estimates for delivering by the end of the quarter, then iterating and finishing it as we rolled it out to more customers. We delivered something that worked within a month and a half, piloting it with two customers, then a couple more, then rolling it out to all customers within a few months. We first produced a monthly invoicing and payments system, and then delivered a weekly option where locums got paid weekly - making the product stickier for both sides.

It was a resounding success, but it was not over! About six months after launch, our CTO decided to embark on a rebuild of the entire system to tackle data modelling debt and improve our ability to scale the team. We rebuilt the monolith in microservices. I was responsible for reimplementing the billing and payments system. I didn't have to change too much of the original design, other than updating the data model and conforming to the new architecture. As part of the rebuild, I also built an API gateway with a GraphQL-like protocol before GraphQL existed, for accessing nested resources across microservices in a single call.

This time, the release of the rebuild project had highly visible problems with billing and payments. They stemmed from silently failing async inter-service calls across the whole system, which were driving much of the behaviour of the new architecture. The problems spanned the whole system, but people only noticed them when irregularities surfaced in billing and payments. In retrospect, the monolith wasn't the problem that the rebuild should have solved - the team should have focused on cleaning up the data model and inter-domain calls. Splitting the monolith into microservices created as many problems as it solved.