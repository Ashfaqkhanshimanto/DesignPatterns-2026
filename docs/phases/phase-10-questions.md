# Phase 10 — Command questions

**Pattern / focus:** Command.

**Read first:** [Guide 10](../../materials/guides/10-command.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example editor undo commands) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to command objects, the invoker, `command_log`, and the controls UI from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Command in plain language. What does it mean to **objectify a request**, and what can you do with that object that you cannot do with a bare `actuator.start()` call (queue, audit, undo, history)?

> [!NOTE]
> **_Your Answer_**
>
> Command means making an action into an object instead of calling something like `actuator.start()` directly. In my greenhouse, a command has the device id and the action it needs to do. Because it is an object, I can keep track of it and save its result in history. It could also be queued or used for undo later, but I did not add those features in Phase 10.

2. Name the participants (**command**, **receiver**, **invoker**, **client**). Who creates the command, who triggers `execute()`, and who actually changes actuator/hardware state?

> [!NOTE]
> **_Your Answer_**
>
> In my app, the commands are `StartPumpCommand`, `StopPumpCommand`, and `SetLightLevelCommand`. The receiver is the `ActuatorPort`, which goes through the decorators to the simulation adapter. The `CommandService` uses `CommandInvoker` to create the command, and the invoker calls `execute()`. The request comes from the controls UI through the API. The adapter simulates the action, and after it works, the service saves the new actuator state in the database.

3. If a command supports undo, when must it capture the data needed to reverse the action? Why is “capture **before** mutate” critical?

> [!NOTE]
> **_Your Answer_**
>
> It needs to save the old value before making any change. For example, if the light was at 20 and I changed it to 50, undo would need to know that the old level was 20. If I only check after changing it, I might not know the old value anymore. I have not implemented undo in this phase.

## B. This phase of the application

4. Which command types did you implement (for example `start_pump`, `stop_pump`, `set_light_level`)? Why does the HTTP handler create a command and pass it to an **invoker** (or application service) instead of calling the actuator adapter from the router?

> [!NOTE]
> **_Your Answer_**
>
> I made three commands: `start_pump`, `stop_pump`, and `set_light_level`. The router sends the request to `CommandService`, and it uses `CommandInvoker` to pick the correct command. I did it this way so the router does not have to handle everything. The service checks the state, runs the command through the decorators, and saves the result in `command_log`.

5. Walk through the execute path: (1) consult State / `allowed_commands`, (2) if illegal → **rejected**, (3) if legal → decorated `apply`, update `actuator_states`, log **success** or **failed**. Why must a rejected command **not** change actuator state and **not** reach inner `apply`?

> [!NOTE]
> **_Your Answer_**
>
> First, the service finds the actuator and checks its current state and `allowed_commands`. It also checks if that command is for the correct device type. If it is not allowed, it saves `rejected` in `command_log` and stops. If it is allowed, the invoker calls the command and it goes through the Phase 9 decorated `apply`. If it works, the service updates `actuator_states` when needed and saves `success`. If execution has an error, it saves `failed`. A rejected command should never reach `apply`, because then the state check would be useless and an illegal action might run.

6. Distinguish **`rejected`** vs **`failed`** vs **`success`** in `command_log`. Give one greenhouse example of each. Why is “illegal in this state” not the same as “policy or adapter error after the command was accepted”?

> [!NOTE]
> **_Your Answer_**
>
> `rejected` means the command was not allowed in that state. For example, I tried to set the light level while the grow light was idle. `failed` means the command was allowed, but it could not finish, like when the max run time blocked my pump command. `success` means it worked, like when I started the Phase 10 Test Pump. So rejected is stopped before execution, but failed means execution was attempted and something went wrong.

7. Why is `command_log` a **different** table from Phase 9 `actuator_execution_log`? What concern does each log record (operator intent vs policy/adapter attempt)?

> [!NOTE]
> **_Your Answer_**
>
> I use `command_log` to see what the user asked the system to do. It saves the command type, payload, and the result, even when a command gets rejected. The Phase 9 `actuator_execution_log` is different. It shows what happened when a command actually reached the decorated actuator port, including the policies. So a rejected command can be in `command_log` but not in `actuator_execution_log`.

## C. Compare, contrast, and scenarios

8. Contrast Command with **Strategy**. Strategy is an interchangeable **algorithm** (decide / quote). Command is a **side-effectful request** with history. How do they cooperate in this app (Phase 6 recommends; Phase 10 executes)?

> [!NOTE]
> **_Your Answer_**
>
> Strategy decides what action might be needed, but Command is used to request an action. In Phase 6, my conservative and aggressive strategies check moisture and recommend if the greenhouse needs irrigation. In Phase 10, I can use `start_pump` to actually request the pump action and save its history. So the two patterns can work together, but I have not connected the recommendation to automatic command execution yet.

9. Contrast Command with **State**. Who **triggers** the action, and who **decides whether it is legal**? Why must commands not bypass state guards?

> [!NOTE]
> **_Your Answer_**
>
> Command says what action I want to run, and the invoker calls it. State checks whether that action is allowed right now. For example, I can start an idle pump, but starting a pump that is already running should be rejected. Without the State check, a command could do something that is not allowed and the saved state could become wrong.

10. The controls UI should disable actions that are not in `allowed_commands`. Why must the **backend** still reject illegal commands even if the UI is correct? What happens if a classmate’s command calls the raw adapter and skips State and Decorator?

> [!NOTE]
> **_Your Answer_**
>
> The UI disables buttons to help users avoid wrong actions, but someone can still call the API directly. Also, the state might change after the page loads. That is why the backend must check again. If someone calls the raw adapter directly, they skip the State checks and Phase 9 decorators. Then the command could run when it should not, and the max-run-time check and execution logging would also be skipped.
