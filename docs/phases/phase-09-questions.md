# Phase 9 — Decorator questions

**Pattern / focus:** Decorator.

**Read first:** [Guide 09](../../materials/guides/09-decorator.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example HTTP client wrappers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to `ActuatorPort`, policy decorators, and `actuator_execution_log` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Decorator in plain language. Why is stacking wrappers a flexible alternative to a combinatorial explosion of subclasses (`LoggingRetryMaxRuntimeActuator`, …)?

> [!NOTE]
> ***Your Answer***
>
> Decorator means adding extra behaviour around an existing object without changing its original code. Instead of making a new actuator class for every combination, I can put logging, max run-time and other policies around the same actuator. I can also change their order or remove one without creating lots of subclasses.

2. Name the participants (**component**, **concrete component**, **decorator**, **concrete decorators**). What interface does every decorator present to the caller, and why must that match the wrapped component?

> [!NOTE]
> ***Your Answer***
>
> In my greenhouse, `ActuatorPort` is the component interface. `SimulationActuatorAdapter` is the concrete component. The decorators are wrappers that use the same port, and my concrete decorators are `LoggingActuatorDecorator` and `MaxRuntimeActuatorDecorator`. They all provide `apply(device_id, command, payload)`, so the service can call them in the same way without needing to know which wrappers are there.

3. **Order matters.** Using logging and retry (or logging and max-run-time) as an example, explain how wrapping A around B can change what you observe compared with wrapping B around A.

> [!NOTE]
> ***Your Answer***
>
> In my app, logging is outside max run-time. So even when max run-time blocks a command, the logging decorator catches that failure and saves it. If max run-time was outside logging, it could stop the call before logging is reached, and then the blocked attempt might not appear in the log. That is why I put logging first in the chain.

## B. This phase of the application

4. What is `ActuatorPort` here, and which **at least two** decorators did you stack around the real adapter (for example logging and max run-time)? Where is the chain wired (composition root / factory), and why not inside the HTTP router?

> [!NOTE]
> ***Your Answer***
>
> `ActuatorPort` is the common interface for applying actuator commands. I wrapped the existing `SimulationActuatorAdapter` with `MaxRuntimeActuatorDecorator` and then `LoggingActuatorDecorator` on the outside. I connected them in `ActuatorExecutionService` in `application/actuators/execution_service.py`. The HTTP router should just handle requests and responses, not decide how the actuator policies are built.

5. Max run-time can **short-circuit**: the inner adapter is never called. Why must a blocked attempt still produce a row in `actuator_execution_log` with `success=false` and the policy named in `policy_applied`?

> [!NOTE]
> ***Your Answer***
>
> A blocked command is still an attempt, even though the simulation adapter never receives it. Saving `success=false` and the `maxRunTime` policy shows what happened and why it was stopped. Otherwise, the dashboard would have no record of the blocked command, which would make problems harder to understand.

6. How does max run-time know the actuator has been running too long (for example `actuator_states.updated_at` from Phase 8)? Why is that data from **State**, not something the decorator should invent as a second lifecycle?

> [!NOTE]
> ***Your Answer***
>
> The max run-time decorator reads the saved actuator state and its `updated_at` timestamp from `actuator_states`. If the state is `running` and that timestamp is at least 30 minutes old, it blocks the attempt. Phase 8 already manages the actuator lifecycle, so making a separate state system inside the decorator could give us two different answers about the same actuator.

7. `GET /api/actuators/executions` feeds the dashboard execution log. Why persist attempts in the database instead of only printing to stdout? What should the UI show after a blocked attempt and a refresh?

> [!NOTE]
> ***Your Answer***
>
> Database records stay available even after the server restarts, while printed logs are not a good way to build a dashboard history. I save each attempt in `actuator_execution_log`, and the GET endpoint reads those rows. After a blocked attempt and refresh, the UI shows a failed result, the policies `maxRunTime` and `logging`, and the message `Max run time exceeded`.

## C. Compare, contrast, and scenarios

8. Contrast Decorator with **Adapter**. Both wrap. One **keeps** the interface and **adds** behaviour; the other **changes** the interface and **translates**. Which is which in this greenhouse (Phase 9 vs Phase 5)?

> [!NOTE]
> ***Your Answer***
>
> Decorator keeps the same interface and adds behaviour. In Phase 9, my logging and max run-time decorators still use `ActuatorPort.apply()`. Adapter is used to translate between an interface the application expects and the way something actually works. In Phase 5, `SimulationActuatorAdapter` provides the actuator port using simulated behaviour instead of real hardware.

9. Contrast Decorator with **inheritance** of combined policies. How does composition let you add or remove a policy without a new subclass for every combination?

> [!NOTE]
> ***Your Answer***
>
> With inheritance, I might need separate classes for logging only, max run-time only, and every combination of policies. With composition, I just wrap the actuator with the decorators I need. If I want another policy later, I can add another wrapper instead of creating a new combined actuator subclass.

10. A classmate’s decorator changes the method signature “a little” (extra required argument, different return type). Another ignores wrap order and cannot explain whether logging runs once per logical call or per inner attempt. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> If a decorator changes the required arguments or return type, it no longer works like the same `ActuatorPort`. Then callers may need special code for that decorator, which defeats the point of wrapping. Order also matters because it decides which calls logging can see. In my Phase 9 chain, outer logging writes one row for each call to `apply()`, including a blocked call. If I added retry inside logging later, inner retries would still appear as one outer logical call unless I moved logging inside the retry wrapper.
