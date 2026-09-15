\# Phase 2 - Factory Method Questions



\## A. Pattern



\### 1. State the intent of Factory Method in plain language. What problem appears when callers scatter new / constructors (or a growing if type == ...) across the application?



Factory Method is used to keep object creation in a clear place instead of letting every part of the program create objects in its own way.



If constructors or many if type checks are spread around the application then adding a new type means changing many different places. this makes the code harder to maintain and easier to break.





\### 2. Name the main participants of Factory Method (product, concrete product, creator, concrete creator, client). For each, give one sentence: what it is responsible for.



product - the common object or interface that is created



concrete product - the actual specific object that gets created



creator - defines the method that is used for creating the product



concrete creator - decides which specific product and defaults should be created



client - asks the creator for an object instead of creating the concrete object directly





\### 3. How do you add a new product variant when creators are polymorphic (new class + registry entry) versus when creation lives in one shared if/elif function? Why does that difference matter for extension?



with polymorphic creators we can add a new creator class and then add it to the registry with one big if or elif function we have to keep editing the same function every time a new type is added the creator approach is easier to extend because the existing creation code needs less change and each type can keep its own creation logic





\## B. This phase of the application



\### 4. In this lab, what is the product and what are the concrete creators? Why must the API handler (or sensor service) go through a creator/registry instead of constructing MoistureSensor / LightSensor itself?



in this project the product is the Sensor domain object the concrete creators are MoistureSensorCreator and LightSensorCreator the API should not directly construct specific sensor types because then the API would need to know all the details about how every sensor is created instead the service uses get\_creator and the selected creator creates the correct sensor with the correct defaults





\### 5. POST /api/sensors accepts a short type key such as "moisture" or "light", while the stored/returned field is device\_type (for example moisture\_sensor). Why are those two fields different? Who decides the stored device\_type and default\_config?



the type field is a short key sent by the client to choose which creator should be used device\_type is the actual value stored for the created device such as moisture\_sensor or light\_sensor the concrete creator decides the device\_type and default\_config. this keeps those details out of the API request and makes sure every sensor of that type gets the correct defaults





\### 6. Why is there a single devices table with role="sensor" instead of a dedicated sensors table? What later phase does that choice prepare for?



we use one devices table because sensors are one kind of device and later the same table can also store other device roles in phase 2 the role is sensor this prepares the project for phase 3 where actuators will also be added and the same devices table can be extended instead of creating a completely separate structure





\### 7. What should happen when the client posts an unknown type? Where should that rejection be decided (registry/service vs router constructing a concrete class anyway)?



an unknown type should be rejected and the API should return a 400 bad request the registry or service should decide that the type is unknown the router should not try to construct a concrete sensor itself because that would bypass the Factory Method design and mix creation logic into the HTTP layer





\## C. Compare, contrast, and scenarios



\### 8. Contrast Factory Method with a simple factory (one function full of if type == ...). When is the simple factory “good enough,” and why does this phase still want polymorphic creators?



a simple factory usually has one function that checks the type and creates the correct object using if or elif statements this can be good enough when there are only a few simple types and the creation logic is unlikely to grow Factory Method is more useful when different types have their own creation rules and defaults. in this phase moisture and light sensors already have different settings so separate creators make the structure easier to extend with more sensor types later





\### 9. Contrast Factory Method with Abstract Factory (Phase 3). Factory Method answers which question? Abstract Factory answers which different question? Why is Factory Method enough for Phase 2 sensors?



Factory Method mainly answers the question of how to create one specific type of product without making the caller construct it directly



Abstract Factory is used when we need to create groups or families of related products that should work together



in phase 2 we only need to create individual moisture and light sensors so Factory Method is enough phase 3 will need related device families and actuators so Abstract Factory becomes more useful there





\### 10. A classmate puts SQLAlchemy session commits (or FastAPI request parsing) inside a concrete creator. Why is that a trap? Where should persistence and HTTP stay instead?



putting database commits or FastAPI request handling inside a creator mixes different responsibilities together



the creator should only be responsible for creating the domain Sensor with the correct type and defaults, database saving and commits should stay in the infrastructure repository



HTTP request parsing and responses should stay in the API layer this keeps the domain and Factory Method code independent from FastAPI and SQLAlchemy

