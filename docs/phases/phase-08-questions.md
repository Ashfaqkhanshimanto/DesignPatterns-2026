
# Phase 8 — State questions

**Pattern / focus:** State.

**Read first:** [Guide 08](../../materials/guides/08-state.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example support-ticket states) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to actuator lifecycle, persisted state, and `allowed_commands` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of the State pattern in plain language. What problem appears when lifecycle is modelled as boolean flags and scattered `if` guards?

> [!NOTE]
> ***Your Answer***
>
> The State pattern helps an object behave differently depending on its current state. It also controls which state changes are allowed. If we use many boolean flags and `if` conditions in different places, the code becomes confusing and can allow invalid situations. In our greenhouse app, we keep the actuator transition rules in one place instead.

2. Name the participants (**context**, **state interface**, **concrete states**, **client**). How does a successful command lead to a **transition**, and where do **guards** live?

> [!NOTE]
> ***Your Answer***
>
> The main participants are the context, state interface, concrete states and client. The context holds the current state, while the state interface defines common behaviour and concrete states handle their own rules. The client asks the context to perform an action.
>
> In our application, we used a transition table instead of separate state classes. `ActuatorContext` is the context, and `state.py` contains the transition rules. When a transition is requested, the domain checks whether it is allowed. If it is valid, the service saves the new state to PostgreSQL. The guards stay in the domain, not in the API or frontend.

3. What is `allowed_commands` (or equivalent) for? Why is exposing “what can I do **now**?” better than letting the UI guess from a raw state string?

> [!NOTE]
> ***Your Answer***
>
> `allowed_commands` tells us which actions are possible in the actuator's current state. For example, when our water pump is running, it allows `stop_pump` and `report_error`.
>
> This is better than letting React guess the commands because the backend already knows the correct rules. The UI can simply display the allowed actions without repeating the same logic.

## B. This phase of the application

4. Which actuator states did you implement (for example idle, running, error)? Sketch the **legal** transitions (which command or event moves idle → running, running → idle, into error, and out of error).

> [!NOTE]
> ***Your Answer***
>
> We implemented five states: `idle`, `running`, `off`, `error` and `maintenance`.
>
> The main transitions are:
>
> - `idle → running` using `start_pump`
> - `running → idle` using `stop_pump`
> - `idle → off` using `turn_off`
> - `off → idle` using `turn_on`
> - `idle → maintenance` using `enter_maintenance`
> - `maintenance → idle` using `finish_maintenance`
> - `idle`, `running`, `off` or `maintenance → error` using `report_error`
> - `error → idle` using `reset`
>
> These transitions are defined in our domain transition table. Any transition not listed there is rejected.

5. Why is actuator state stored in `actuator_states` (or equivalent) rather than only in process memory? What must still be true after you restart the backend?

> [!NOTE]
> ***Your Answer***
>
> We store actuator states in PostgreSQL because memory data can disappear when the backend restarts. If we only kept the state in Python, our water pump could lose its previous state after restarting.
>
> The `actuator_states` table stores the device ID, current state and update time. After restarting the backend, the actuator should still return its previously saved state and the correct allowed commands.

6. An **illegal** transition must raise a domain error and **must not** update the database. Why? Which HTTP status is reasonable for that case (400 or 409), and why should the rule live in the domain rather than in React?

> [!NOTE]
> ***Your Answer***
>
> An illegal transition should not update the database because it could put an actuator into a state that is not allowed. In our app, we tried changing the Simulation Water Pump directly from `running` to `maintenance`. The API returned HTTP `409`, and the database still showed `running`.
>
> I think 409 is suitable because the requested change conflicts with the actuator's current state. The rules belong in the domain because React is only the user interface. Even if someone calls the API directly, the same rules must still be enforced.

7. Device JSON gains `state` and `allowed_commands`. How does the dashboard use those fields (badges, disable illegal buttons)? How does this prepare **Phase 10 Command**?

> [!NOTE]
> ***Your Answer***
>
> Our device API now returns `state` and `allowed_commands` for actuators. The dashboard uses these fields to show coloured state badges and a list of permitted commands.
>
> For example, our Simulation Water Pump showed a green `running` badge with `stop_pump` and `report_error` as allowed commands.
>
> We haven't added execution buttons yet. In Phase 10, these fields can help the Command Pattern show or enable only valid commands. The backend will still check the state before accepting a command.

## C. Compare, contrast, and scenarios

8. Contrast State with **Strategy**. Both look like “context delegates to an object.” Who typically **changes** the active object, and is the variation a **lifecycle** or a **selectable policy**? Give a greenhouse example of each (this phase vs Phase 6).

> [!NOTE]
> ***Your Answer***
>
> State and Strategy are similar because they both change behaviour without putting everything into one large class. But they are used for different reasons.
>
> State is about an object's lifecycle. The active state changes when an allowed transition happens. In Phase 8, our water pump changes from `idle` to `running` and then back to `idle`.
>
> Strategy is about choosing between different ways of doing something. In Phase 6, we selected `conservative` or `aggressive` irrigation strategies for a greenhouse location. The user can choose the strategy, while actuator state changes follow the lifecycle rules.

9. Contrast State with a pile of booleans (`is_running`, `is_fault`, `is_maintenance`). Why do illegal combinations of flags appear, and how do explicit state objects (or a transition table) prevent that?

> [!NOTE]
> ***Your Answer***
>
> With separate boolean flags, we could accidentally have `is_running` and `is_maintenance` both set to true. That would be confusing because the actuator should not be running and under maintenance at the same time.
>
> In our application, each actuator has one state value instead of several flags. The transition table also checks which state changes are allowed. This prevents invalid combinations and makes the lifecycle easier to manage.

10. A classmate puts HTTP status mapping or SQLAlchemy commits **inside** a concrete state class. Another state mutates a flag directly and skips `transition` / `set_state`. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> Putting HTTP errors or database commits inside a state class mixes different responsibilities. The domain should only handle state rules, while the API handles HTTP responses and the repository handles database operations. Otherwise, the code becomes harder to test and maintain.
>
> Directly changing a flag is also a problem because it skips the transition rules. That could allow an illegal state change. In our greenhouse app, `ActuatorContext` checks the transition first, and the application service saves it only when the change is valid.
