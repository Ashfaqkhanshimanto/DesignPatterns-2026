
# Facade Pattern — Phase 7

## What is the Facade Pattern?

The Facade Pattern provides one simple interface for working with several parts of an application.

Instead of asking different services for information separately, the client uses one Facade to get what it needs.

## Why we used it

Our greenhouse application already has locations, zones, devices, sensor readings and automation strategies.

Before Phase 7, these features were handled by different parts of the application.

To display a complete greenhouse overview, the frontend would otherwise need to collect information from several API endpoints.

We introduced `LocationOverviewFacade` so the frontend can get the main greenhouse information through one endpoint.

## Where the pattern is used

### Backend

- `backend/src/application/overview/dto.py`

  Defines the DTOs for the overview response.

- `backend/src/application/overview/facade.py`

  Contains `LocationOverviewFacade`. It combines the location, device counts, zones, readings and automation information.

- `backend/src/infrastructure/persistence/overview_repository.py`

  Reads location, zone, device and latest reading data from PostgreSQL.

- `backend/src/interfaces/api/overview.py`

  Exposes the overview endpoint and calls the Facade.

### Frontend

- `frontend/src/services/api.ts`

  Contains `fetchLocationOverview()` and the TypeScript overview types.

- `frontend/src/components/overview/OverviewPanel.tsx`

  Displays the greenhouse overview using the overview response.

- `frontend/src/pages/DashboardPage.tsx`

  Includes the Overview Panel on the dashboard.

## How it works

The frontend calls:

GET /api/locations/{location_id}/overview

The API handler calls `LocationOverviewFacade.get_overview()`.

The Facade gets the location, all its zones, assigned devices and the latest readings.

It counts assigned sensors and actuators and prepares the response for the frontend.

It also checks whether the location has a saved automation strategy.

If a strategy is saved, the Facade uses the existing `AutomationService.evaluate()` method to calculate the current recommendation.

We reuse the Strategy Pattern from Phase 6 instead of writing the strategy decision logic again.

If there is no saved strategy, the overview still works, but `strategy_key` and `last_recommendation` are null.

## Database queries

The overview repository loads locations and zones, assigned devices and latest readings using separate queries.

The latest readings query uses SQL `row_number()` with a partition for each device.

This allows the repository to select the newest reading for every assigned device without making a separate query for each device.

The overview repository does not filter readings by source.

The automation evaluation still uses the existing Phase 6 repository, which may run additional queries for each zone.

No new database tables or migrations were needed in Phase 7.

## What the response includes

The overview response contains:

- Location ID and name
- Assigned sensor and actuator counts
- All zones, including zones without devices
- Assigned devices for each zone
- Latest available reading for each device
- Device tracking and sampling settings alongside the readings
- Saved automation strategy, if one exists
- Current automation recommendation, if a strategy is saved

Unassigned devices are not included in the overview counts or zone device lists.

## Benefits

The main benefit is that the frontend does not need to know how all the backend services work internally.

The overview API provides one entry point for the required information.

It also keeps the API handler simple and avoids repeating our existing automation logic.

If the internal implementation changes later, the frontend can continue using the same overview endpoint.

## Testing

We added integration tests in:

`backend/tests/test_overview.py`

The tests check:

1. Missing locations return HTTP 404.
2. Locations without a saved strategy return null strategy and recommendation values.
3. Zones, assigned devices, latest readings and automation recommendations are returned correctly.

All three integration tests passed.
