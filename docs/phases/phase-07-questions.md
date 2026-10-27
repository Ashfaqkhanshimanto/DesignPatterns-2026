
# Phase 7 — Facade questions

**Pattern / focus:** Facade.

**Read first:** [Guide 07](../../materials/guides/07-facade.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a video publish pipeline) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the location overview, the facade, and the dashboard Overview page from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Facade in plain language. What problem appears when every HTTP handler (or every UI screen) repeats the same multi-step dance across repositories and services?

> [!NOTE]
> **_Your Answer_**
>
> Facade gives us one simple place to access several parts of the application. Without it, every API handler or frontend page would need to call different repositories and services to collect the same information. This would repeat code and make changes harder because we might need to update the same logic in many places.

2. A facade **orchestrates** collaborators. What should it **not** become (a god object that owns all domain logic)? Where should irrigation policy, sensor translation, and persistence stay instead?

> [!NOTE]
> **_Your Answer_**
>
> A facade should not become a huge class that does everything itself. Its job is to connect the existing parts, not replace them. In our greenhouse app, irrigation decisions stay in the Strategy classes, sensor translation stays in the Phase 5 adapters, and database operations stay in the repositories. The facade just uses these parts to prepare the overview.

3. When should you use Facade, and when should you skip it (a single repository call is enough; or you actually need to **translate** a mismatched interface)?

> [!NOTE]
> **_Your Answer_**
>
> Facade is useful when one operation needs information from several services or repositories. For example, our greenhouse overview needs locations, devices, readings and automation information together. But if we only need one simple repository call, adding a facade may be unnecessary. If the problem is converting one interface or data format into another, Adapter would be a better choice.

## B. This phase of the application

4. What does `GET /api/locations/{location_id}/overview` return? Name the main pieces of the overview DTO: location, assigned device counts, and `zones` (thresholds, assigned devices, and those devices’ latest readings, including `tracking_enabled` and `sampling_interval_seconds`), plus strategy key and last recommendation. Why may those reading rows come from the sampler or MQTT ingest, not only from `POST /read`? Why is overview scoped by `location_id`?

> [!NOTE]
> **_Your Answer_**
>
> This endpoint returns the complete overview of one greenhouse location. It includes the location ID and name, the number of assigned sensors and actuators, and all zones with their moisture thresholds. Each zone also contains its assigned devices and their latest available readings, including value, unit, time, tracking status and sampling interval.
>
> It also returns the saved strategy key and the current automation recommendation. The readings can come from manual reads, the automatic sampler or MQTT ingestion because all of them use the same readings table. We use `location_id` because our application stores and manages greenhouse areas as locations, and the overview should show only the information belonging to the selected location.

5. Why does this phase **not** require a new business table? What already exists from Phases 2–6 that the facade only **composes**?

> [!NOTE]
> **_Your Answer_**
>
> We don't need a new table because the information is already stored in our database. Previous phases created devices, locations, zones, sensor readings and automation rules. The facade simply reads and combines that existing data into one response. The recommendation is calculated using our existing AutomationService, so we don't need to store it separately.

6. The overview HTTP handler should call **only** the facade, not reading/strategy/device repositories directly. Why? How does that help tests and later changes to the query shape?

> [!NOTE]
> **_Your Answer_**
>
> The HTTP handler should only call the facade because the handler should not be responsible for collecting data from different places. In our app, it calls `get_overview()` and gets the complete result. This makes the API code easier to understand and test. If we change the database queries later, we can update the repository or facade without changing how the endpoint works.

7. The location selector may use the existing locations list. The Overview cards come from **one** overview fetch, and Refresh repeats that same fetch. Why must the React page not stitch device, reading, and automation calls together to build the same snapshot? How does a new reading or a saved strategy show up on overview without extra frontend glue?

> [!NOTE]
> **_Your Answer_**
>
> React should not collect all this information using separate calls because it would repeat backend logic in the frontend. It could also become confusing if different requests finish at different times. In our Overview Panel, we use `fetchLocationOverview()` to get the complete information in one response.
>
> When we click Refresh, the same endpoint loads the latest stored readings and checks the saved strategy again. The backend calculates the recommendation, so React only needs to display the updated response.

## C. Compare, contrast, and scenarios

8. Contrast Facade with **Adapter**. One makes an existing interface usable; the other makes a subsystem simpler to call. Which is which, and how do both appear in this greenhouse app (Phase 5 vs Phase 7)?

> [!NOTE]
> **_Your Answer_**
>
> Adapter makes different interfaces work in a common format, while Facade provides a simpler way to use several existing parts together. In Phase 5, our sensor adapters convert different sensor data into a common Reading format. In Phase 7, LocationOverviewFacade combines location, device, reading and automation information into one overview. So Adapter helps with compatibility, while Facade makes the system easier to use.

9. This phase mentions **N+1** queries. What is an N+1 problem in an overview that lists latest readings for many devices, and what can the facade (or its repository) do about it without putting SQL in the router?

> [!NOTE]
> **_Your Answer_**
>
> N+1 happens when we first load a list of devices and then run another database query for every device to get its latest reading. If there are many devices, this creates too many queries and can slow down the overview. In our application, OverviewRepository uses a SQL window function to find the latest reading for all assigned devices in one query. The SQL stays inside the repository, not in the API handler.

10. A classmate hides every error behind a generic “overview failed,” so a missing location, a DB outage, and a strategy error look the same. Why is that a trap for a facade?

> [!NOTE]
> **_Your Answer_**
>
> This is a problem because different errors need different handling. For example, if a location does not exist, our API returns 404. But a database connection problem or a strategy error is something different. If the facade hides everything behind one message, it becomes difficult to understand and fix the real problem. The facade should keep errors meaningful instead of hiding them.
