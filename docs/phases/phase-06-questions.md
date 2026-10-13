# Phase 6 — Strategy Questions

## A. Pattern

### 1. What is the intent of Strategy?

**Your Answer**

Strategy pattern allows us to use different algorithms for the same task without changing the main application code.

In my greenhouse project the application selects either conservative or aggressive strategy. The application service give the zone context to the selected strategy and calls `decide(context)`.

Choosing the strategy and running it are separate because we can change the irrigation policy without changing how the evaluation works.

### 2. Name the participants and explain the problem with if/elif.

**Your Answer**

The main participants in my project are:

- **Strategy:** `AutomationStrategy`, which defines `decide(context)`.
- **Concrete strategies:** `ConservativeMoistureStrategy` and `AggressiveMoistureStrategy`.
- **Context:** `LocationAutomationContext`, which contains the moisture reading and zone thresholds.
- **Client:** `AutomationService`, which selects and calls the strategy.

If I put all the irrigation rules inside `if/elif` statements in the service or API, the code will become messy when adding more strategies. Separate classes make it easier to update and test each strategy.

### 3. When should you use Strategy, and when should you skip it?

**Your Answer**

I should use Strategy when I have different algorithms for the same task and need to switch between them. For example, my greenhouse can use conservative or aggressive irrigation depending on the selected policy.

If there is only one simple algorithm and no need to change it, Strategy might be unnecessary.

Also, if the changes are based on the system's lifecycle, like a pump being idle, running, or stopped, the State pattern would be more suitable.

## B. This Phase of the Application

### 4. What does decide(context) return?

**Your Answer**

In my application, `decide(context)` returns a `Recommendation` object containing an action, reason, and optional score.

For example, if a zone has a low threshold of `0.30`, a high threshold of `0.70`, and moisture reading of `0.40`:

- Conservative returns `wait` because moisture is not below `0.30`.
- Aggressive returns `irrigate` because moisture is below the midpoint `0.50`.

So both strategies use the same reading and thresholds but can give different recommendations.

### 5. Where does the context data come from?

**Your Answer**

The moisture reading comes from the `sensor_readings` table in PostgreSQL. The repository finds the latest reading from moisture sensors assigned to that specific zone.

The low and high thresholds come from the `zones` table, which we created in Phase 4.

Phase 5 already handles getting sensor readings through manual reads, simulation sampling, and translated MQTT data, so we don't need another scheduler or MQTT broker in Phase 6.

I use a plain Python `LocationAutomationContext` because the Strategy classes should only handle decision logic. They don't need to know about SQLAlchemy, FastAPI, or database tables.

Thresholds are loaded from the database because different zones can have different settings. Hardcoding the values would make the strategies less flexible.

### 6. Why must evaluate use the saved strategy key?

**Your Answer**

The selected strategy is stored in the `automation_rules` table using `location_id`, so each location has its own active strategy.

The evaluate API should use the saved strategy because the selected policy needs to stay the same between requests and after restarting the application. Otherwise, the client would have to send the strategy every time, and the result could depend on what the client sends instead of the actual saved configuration.

If the operator changes from conservative to aggressive and saves it, the next evaluation uses aggressive. Even if moisture stays the same, the recommendation can change because the strategies have different rules.

### 7. Why separate decide from execute?

**Your Answer**

The Strategy pattern should only decide what action is recommended, like `irrigate` or `wait`. It should not directly start the water pump.

This is important because making a decision and controlling a real device are different responsibilities. We might also need to check safety conditions before executing anything.

The Command pattern in the later phase can handle carrying out actions like starting or stopping the pump.

## C. Compare, Contrast, and Scenarios

### 8. Strategy vs State

**Your Answer**

Strategy is mainly used to select between different algorithms or policies. Usually the client or operator chooses which strategy to use.

In my greenhouse project, the operator chooses conservative or aggressive irrigation and saves it.

State is different because it represents the current lifecycle or condition of an object. The object or its state logic can change the active state when something happens.

For example, a pump might move from idle to running and then stopped. That's a lifecycle change, not a choice between irrigation policies.

### 9. Strategy vs Adapter vs Builder

**Your Answer**

These three patterns solve different problems.

**Adapter (Phase 5)** converts sensor readings from different sources into a format the application understands. For example, our sensor adapters handle simulated readings and translated MQTT payloads.

**Builder (Phase 4)** helps create a valid greenhouse location configuration with zones and moisture thresholds step by step.

**Strategy (Phase 6)** allows the application to switch between different irrigation algorithms, like conservative and aggressive, without changing the main evaluation code.

So Adapter translates data, Builder creates a configuration, and Strategy changes the algorithm.

### 10. Why are mega-strategy and direct actuator calls bad designs?

**Your Answer**

If someone puts `if conservative` and `if aggressive` inside one big strategy class, it doesn't really solve the original problem. Every time a new strategy is added, that same class needs to be modified. It would become difficult to maintain.

Each strategy should have its own class and implement the same interface.

The second problem is starting the pump directly inside the strategy. A strategy should only return a recommendation, not execute hardware actions.

If it controls the pump directly, testing becomes harder and the decision logic is mixed with device control. Keeping them separate makes the system safer and easier to extend.