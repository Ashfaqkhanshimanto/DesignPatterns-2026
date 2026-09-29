# Phase 04 Questions — Builder Pattern

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

**Note**

***Your Answer***

Builder is useful when a object has several parts that need to be put together before it is considered complete. Here I use it to build a location configuration step by step including the location name and its zones. The `build()` method validates the whole configuration at the end. This prevents incomplete or invalid configuration data from being saved to the database.

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

**Note**

***Your Answer***

The product is the completed `LocationConfig`, the builder is `LocationConfigBuilder` and the client is the application service that uses the builder. A director is optional and I do not need a separate one in this implementation. Before `build()` succeeds, the collected values are only construction data and not a finished valid domain configuration. This matters because incomplete data should not be treated or stored as a valid location configuration.

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

**Note**

***Your Answer***

The builder rejects an empty location name, a location with no zones, and moisture thresholds outside the range from 0.0 to 1.0. It also rejects a low threshold that is equal to or greater than the high threshold and duplicate zone names. These rules belong in the domain builder so they are applied even if the configuration is created from somewhere other than the HTTP API.

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

**Note**

***Your Answer***

The builder produces one location configuration containing a `Location` and its `Zone` objects. `location_id` is used because the location is the scope that owns the zones in this application. Using the same name in the domain, database and API also avoids introducing a different `greenhouse_id` concept that the model does not use.

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

**Note**

***Your Answer***

The API receives the request as a DTO and the application service passes its values to `LocationConfigBuilder`. The builder sets the location name, adds the zones and then calls `build()`. Only after a valid configuration is returned does the repository save it. If `build()` raises `ConfigurationError`, no location or zone from that configuration should be persisted.

Device assignment happens after the zone exists because the device needs a real zone ID from the database. The client only sends `zone_id`. From that zone the backend can find its `location_id`, so the client does not need to send both values or risk sending values that do not match.

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

**Note**

***Your Answer***

If the location is committed first and saving a zone later fails, the database could contain a location without its complete set of zones. That would leave only part of the aggregate saved. Using one transaction means either the location and all of its zones are saved successfully, or the whole operation is rolled back.

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

**Note**

***Your Answer***

The configuration wizard collects the values the user enters, such as the location name, zone names and moisture thresholds. React can do simple checks to help the user, but it does not decide whether the final domain configuration is valid. The values are sent through the API to the application service, which uses the Builder. The Builder performs the domain validation when `build()` is called.

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

**Note**

***Your Answer***

Factory Method answers which type of object should be created, such as choosing the correct sensor creator. Abstract Factory creates a matching family of related devices, such as one device family. Builder is different because it focuses on assembling one valid whole step by step, which in this phase is the location configuration with its zones.

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

**Note**

***Your Answer***

A fluent interface only means methods can be chained together. Builder is about controlling the construction of a complex product and producing the finished product after its required rules have been checked. A class can use method chaining without actually implementing the Builder pattern.

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

**Note**

***Your Answer***

If validation exists only in FastAPI or Pydantic, another part of the program could create an invalid configuration without going through the HTTP layer. The domain builder should therefore enforce the important configuration rules itself.

Changing builder fields after `build()` should also not change a product that is treated as immutable. The built `LocationConfig` should represent the finished result at that moment. Later builder changes should be part of another construction process, not hidden changes to an already built product.