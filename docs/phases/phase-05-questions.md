# Phase 5 — Adapter questions

**Pattern / focus:** Adapter.

**Read first:** [Guide 05](../../materials/guides/05-adapter.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

> [!NOTE]
> ***Your Answer***
>
> Adapter basically helps two different interfaces work together. For example a vendor sensor can give data with different field names, units or formats, but our application expects one common format. If the business code handles all the vendor specific things directly, it will get messy and also become dependent on that vendor. Adapter keeps those differences in one place.

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

> [!NOTE]
> ***Your Answer***
>
> The target or port is the interface our application expects. The adaptee is the external system or device that already has its own format. The adapter sits between them and converts that data into the format our application understands. The client just uses the common interface. The adapter should only translate the data, it should not make business decisions like deciding when the greenhouse should start watering.

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

> [!NOTE]
> ***Your Answer***
>
> Modern code usually prefers object adapter using composition. It uses or wraps another object instead of inheriting from it. This is more flexible because the adapter does not need to be tightly connected to the adaptee class and it is easier to replace or test different implementations.

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

> [!NOTE]
> ***Your Answer***
>
> `SensorPort` is the common sensor interface in our application. The adapters return a normalized `Reading` with device id, value, unit, source and recorded time. Application services should depend on the common port instead of knowing details about a simulation driver or vendor SDK. This way adding or changing a sensor integration does not require changing the main application logic.

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

> [!NOTE]
> ***Your Answer***
>
> The different raw formats are actually the main reason for using Adapter here. Simulation, vendor and MQTT data can come in different shapes, but after translation the application gets the same `Reading` format. The `source` tells us where the reading came from, like `simulation`, `vendor` or `mqtt`. In this phase MQTT only translates a payload dict. It should not connect to a broker or HTTP transport because that is not the job of this adapter in this phase. Later Phase 12 can deliver the payload and the adapter can still just focus on translating it.

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

> [!NOTE]
> ***Your Answer***
>
> We append readings to `sensor_readings` because we need the history, not only the latest value. If we overwrite the same row or only keep the value in memory, the old readings would be lost and later features that need the history could not use them. Manual read, automatic simulation sampling and later MQTT should use the same writer so readings are always stored in one consistent way. The sampler skips devices with tracking off because they should not be sampled automatically. It also skips MQTT devices because MQTT readings come from incoming messages instead of our simulation timer. For now the sensor cards poll the stored readings until Phase 12 adds the later real-time part.

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

> [!NOTE]
> ***Your Answer***
>
> If the device does not exist, `404 Not Found` makes sense. If the device exists but its adapter cannot read it or the protocol is unsupported, that is a different error. In our current API this kind of adapter problem is returned as a `400` error. The router should only work with our normal DTOs and application types, not vendor-shaped data. Otherwise vendor specific details would start leaking into the API layer.

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

> [!NOTE]
> ***Your Answer***
>
> Adapter changes one interface or data shape into the interface our application expects. In this phase our sensor adapters are an example because different sensor data becomes the same `Reading`. Facade is different because it gives a simpler way to use a bigger subsystem instead of mainly translating an interface. In Phase 7 a greenhouse Facade could give one simple operation that internally works with several greenhouse services or devices.

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

> [!NOTE]
> ***Your Answer***
>
> Adapter and Decorator can both wrap another object, but their purpose is different. Adapter presents a different interface so incompatible code can work together. Decorator normally keeps the same interface and adds some extra behaviour around the original object.

10. A classmate puts irrigation policy (“if moisture < 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

> [!NOTE]
> ***Your Answer***
>
> Putting something like `if moisture < 0.3 then water` inside the vendor adapter would mix business rules with data translation. Then the adapter would start deciding how the greenhouse should behave instead of just adapting sensor data. That watering decision should later be handled by the Strategy part of the application. The adapter should only read or translate the vendor data into our normal `Reading`.