- Use your own wording. Do not paste teaching-example types (for example warrior/mage class kits) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to device families, provision, and the unified devices API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (`if format` for each piece) instead of as a **family**?

**Note**

***Your Answer***

Abstract Factory is used when we need to create a group of related objects that should work together. Instead of choosing every product separately we choose one family and create the matching products from that family. If each product is selected independantly with separate `if` statements, it becomes easy to accidentally mix products from different families and create an inconsistent setup.

2. Name the main participants (**abstract factory**, **concrete factory**, **abstract products**, **concrete products**, **client**). How does choosing a factory at the start **commit** the client to one family?

**Note**

***Your Answer***

The abstract factory defines what a family factory should create. The concrete factories are the real implementations such as the simulation factory and edge factory. The abstract products are the general device types, while the concrete products are the actual simulation or edge sensors and actuators. The client in this project is mainly the service that asks the selected factory to create a device set. Once it selects simulation or edge all devices in that set come from that same family.

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?

**Note**

***Your Answer***

Abstract Factory is useful when several related products must be created together and they should belong to the same family. It is useful in this project because sensors and actuators need matching simulation or edge configuration. I would skip it if I only needed to create one independent product or if mixing products from different families was completely valid and there was no need to keep them consistent.

## B. This phase of the application

4. In this lab, what is a **device family**, and what does `create_device_set()` (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?

**Note**

***Your Answer***

A device family in this lab is a group of sensors and actuators that belong to the same environment. We have `simulation` and `edge` families. `create_device_set()` returns four devices two sensors and two actuators. A simulation kit should not contain edge devices because the configuration is different for example simulation uses simulation settings while edge devices use settings such as modbus, i2c and gpio.

5. Phase 2 Factory Method creators still exist. How does Abstract Factory **compose** them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?

**Note**

***Your Answer***

The Abstract Factory still uses the Phase 2 sensor creators for the moisture and light sensors. The family factory asks those creators to build the sensor first and then adds the family-specific configuration. This means the Factory Method code is reused instead of deleted. If I removed the sensor creators and wrote all sensor construction inside the family factories, I would duplicate the sensor creation logic and lose the clear separation from Phase 2.

6. Why add a `device_family` column on the existing `devices` table (with a default/backfill such as `"simulation"`) instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?

**Note**

***Your Answer***

I added `device_family` to the existing `devices` table because sensors and actuators are still devices, only from different families. Creating a separate table for every family would duplicate the same structure and make queries more complicated. The default and backfill to `simulation` also keeps the old Phase 2 sensors valid. Without the backfill, old sensor rows could have no family value and the migration could fail because the new column is not nullable.

7. `POST /api/devices/provision` returns a kit (expected size: two sensors and two actuators). `GET /api/devices` can filter by `family` and `role`. Why must the UI be able to filter by family? Why do `/api/sensors` routes from Phase 2 still need to work?

**Note**

***Your Answer***

The UI needs to filter by family so when the user selects simulation or edge, only devices from that selected family are shown. Without the family filter, devices from different families would be mixed together in the dashboard. The Phase 2 `/api/sensors` routes still need to work because Phase 3 is extending the existing application, not replacing the Factory Method functionality from Phase 2.

## C. Compare, contrast, and scenarios

8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which **one** product?” versus “which product **line**?” and mention that Abstract Factory often **uses** Factory Method–style methods inside.

**Note**

***Your Answer***

Factory Method is mainly about deciding which one product should be created, for example whether the application needs a moisture sensor or a light sensor. Abstract Factory is about deciding which product line should be created, for example a complete simulation family or edge family containing both sensors and actuators. Abstract Factory can also use Factory Method-style creation inside it, which is what happens in this project because the family factories reuse the Phase 2 sensor creators.

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?

**Note**

***Your Answer***

If the HTTP handler creates concrete devices directly, it could accidentally mix simulation and edge devices or forget some family-specific configuration. That would bring back the same consistency problem that Abstract Factory is supposed to prevent. The HTTP layer should only pass the requested family to the service, and the service should resolve the correct family factory and create the full device set.

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?

**Note**

***Your Answer***

That would give one factory too many unrelated responsibilities. Abstract Factory should create related products that belong to one family, not every object in the whole application. Locations, readings and devices are different concepts and should have their own responsibilities. Putting all of them into one factory would make the code harder to understand, maintain and extend.