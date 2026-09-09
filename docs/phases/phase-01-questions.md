\# Phase 1 - Skeleton Questions



\## A. Pattern



\### 1. In your own words, what is a design pattern? What is it not?



a design pattern is basically a common way to solve a software design problem that happens many times in different projects. it gives us an idea how we can organize the code better but it is not ready made code libraries that we just copy and use. also it doesnt mean we need to use a pattern for every small problem. sometimes it is better not to use design pattern for smaller projects.





\### 2. Name the three GoF pattern families. For each family, give one-sentence: what kind of design problem it addresses. Then place Factory Method and Strategy into the correct family.



the three GoF pattern families are:

1- Creational - mainly about how objects are created

2- Structural - mainly about how classes and objects are connected and organized together

3- Behavioral - mainly about how objects communicate and how their behaviour can change

Factory Method is a Creational patter

Strategy is a Behavioral pattern





\### 3. A teammate wants to add a pattern because it is on the course list, even though the feature is small and unlikely to grow. When should you skip a pattern? What risk do you take if you apply one too early?



i think we should skip a pattern if the problem is already simple and can be solved easily with normal code

we should not add a design pattern only because it is in the course. if we use it too early it can make the code more complicated than it actually needs to be and also harder to understand





\## B. This phase of the application



\### 4. Why does Phase 1 ship a vertical slice that does almost no greenhouse business logic? What does empty but running prove that a folder of unimplemented classes would not?



phase 1 is more about making sure the basic structure of the application is working before we start adding the actual greenhouse features even if it is mostly empty we can already prove that postgres is running, backend can connect to database, migrations work, api works and frontend is also running if we only made some empty folders and classes then we would not really know if all these parts are actually working together





\### 5. List the four backend layer packages used in this course domain, application, infrastructure, interfaces/api. For each, state what belongs there and give one example of something that must not live in domain.



the four backend layers are

1- domain - this is for the main business ideas rules entities and pattern interfaces

2- application - this is for use cases and coordinating what the application needs to do

3- infrastructure - this is for technical things like database settings adapters and external services

4- interfaces/api - this is where FastAPI routes and http requests and responses are handled

for example FastAPI routes or SQLAlchemy database code should not be inside domain because domain should not depend on those technical frameworks





\### 6. What does GET /health return, and why does it check the database instead of only reporting that the HTTP process is up? Why is API documentation served at /scalar, and why is /docs disabled?



GET /health returns the status of the api and also the database when everything is working it gives something like

{"status": "ok","db": "ok"}

it checks the database because just because FastAPI is running doesnt mean the whole backend is working. the application also needs postgres to work. we use /scalar because Scalar is the api documentation tool used in this course and the normal FastAPI /docs page is disabled so Scalar is used instead





\### 7. Phase 1 requires Alembic with a baseline migration and no business tables such as devices. Why introduce the migration toolchain before any product schema? What would go wrong if you created tables by hand in Postgres and only added migrations later?



Alembic is added from the beginning so database changes can be tracked properly from the start. the baseline migration also proves that Alembic can connect to postgres and run correctly even when we still dont have any business tables, if we manually create tables in postgres first and only add migrations later then the real database structure and migration history can become different. this can create problems later when the project is run on another computer





\## C. Compare, contrast, and scenarios



\### 8. Explain dependency direction in this skeleton: which layers may import which? Why must domain code not import FastAPI, SQLAlchemy, or Pydantic models used as HTTP schemas?



the dependency direction should go toward the important business logic. the api layer can call the application layer. the application layer can use the domain and it can also work with infrastructure when needed. the domain should stay independent and should not import FastAPI SQLAlchemy or http related Pydantic models. this is useful because if we change the api framework or database technology later the main business logic should not need to be completely rewritten.





\### 9. The frontend cannot show a healthy badge. A classmate blames the patterns. What should you check first and why is that a Phase 1 concern rather than a later pattern concern?



first i would check if postgres backend and frontend are all actually running. then i would open /health directly and check if it returns the correct json.
after that i would check the api url and CORS or proxy settings to make sure the frontend can communicate with the backend.

this is a phase 1 problem because it is about the basic connection between frontend backend and database. design patterns come later and they are not the first thing to check for this kind of connection problem.





\### 10. Course completion is at Phase 12, not Phase 1. What is still missing after a successful skeleton, and how do later phases add behaviour without rewriting the foundations you laid here?



after phase 1 we mostly have the working base of the project but we still dont have most of the actual smart greenhouse features
for example we dont have real devices sensors locations automation rules actuator states commands alerts or websocket updates yet
the later phases will add these things step by step using Factory Method Abstract Factory Builder Adapter Strategy Facade State Decorator Command and Observer
because phase 1 already gives us the backend structure database migrations api setup and frontend shell we can add those features later without rebuilding the whole project again

