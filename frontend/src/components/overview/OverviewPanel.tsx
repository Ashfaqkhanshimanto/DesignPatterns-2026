
import { useEffect, useState } from "react";

import {
  fetchLocations,
  fetchLocationOverview,
  type LocationDto,
  type LocationOverviewDto,
} from "../../services/api";


export default function OverviewPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [locationId, setLocationId] = useState("");
  const [overview, setOverview] =
    useState<LocationOverviewDto | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchLocations()
      .then((data) => {
        setLocations(data);

        if (data.length > 0) {
          setLocationId(data[0].id);
        }
      })
      .catch(() => {
        setError("Could not load locations.");
      });
  }, []);

  useEffect(() => {
    if (!locationId) {
      setOverview(null);
      return;
    }

    let cancelled = false;

    setOverview(null);
    setError("");
    setLoading(true);

    fetchLocationOverview(locationId)
      .then((data) => {
        if (!cancelled) {
          setOverview(data);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Could not load overview.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [locationId]);

  async function handleRefresh() {
    if (!locationId) return;

    setLoading(true);
    setError("");

    try {
      const data = await fetchLocationOverview(locationId);
      setOverview(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not refresh overview.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-xl font-semibold">
          Greenhouse Overview
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Location, devices, readings and automation in one view.
        </p>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="min-w-56 flex-1">
          <label
            htmlFor="overview-location"
            className="mb-2 block text-sm font-medium"
          >
            Location
          </label>

          <select
            id="overview-location"
            value={locationId}
            onChange={(event) => setLocationId(event.target.value)}
            className="w-full rounded-lg border border-slate-300 p-2"
          >
            {locations.length === 0 && (
              <option value="">No locations available</option>
            )}

            {locations.map((location) => (
              <option key={location.id} value={location.id}>
                {location.name}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={handleRefresh}
          disabled={!locationId || loading}
          className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}

      {!overview && loading && (
        <p className="text-sm text-slate-500">
          Loading overview...
        </p>
      )}

      {overview && (
        <div className="space-y-5">
          <h4 className="font-semibold">
            {overview.location.name}
          </h4>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="text-sm text-slate-500">
                Assigned Sensors
              </p>
              <p className="text-2xl font-bold">
                {overview.device_counts.sensor}
              </p>
            </div>

            <div className="rounded-lg bg-slate-50 p-4">
              <p className="text-sm text-slate-500">
                Assigned Actuators
              </p>
              <p className="text-2xl font-bold">
                {overview.device_counts.actuator}
              </p>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 p-4">
            <h4 className="font-semibold">
              Automation
            </h4>

            <p className="mt-2 text-sm">
              <strong>Saved strategy:</strong>{" "}
              {overview.strategy_key ?? "No strategy saved"}
            </p>

            {overview.last_recommendation ? (
              <div className="mt-2 space-y-1 text-sm">
                <p>
                  <strong>Recommendation:</strong>{" "}
                  {overview.last_recommendation.action}
                </p>

                <p className="text-slate-600">
                  {overview.last_recommendation.reason}
                </p>
              </div>
            ) : (
              <p className="mt-2 text-sm text-slate-500">
                No recommendation available.
              </p>
            )}
          </div>

          <div className="space-y-3">
            <h4 className="font-semibold">
              Zones
            </h4>

            {overview.zones.map((zone) => (
              <div
                key={zone.id}
                className="rounded-lg border border-slate-200 p-4"
              >
                <h5 className="font-semibold">
                  {zone.name}
                </h5>

                <p className="mt-1 text-sm text-slate-500">
                  Moisture thresholds: {zone.moisture_threshold_low}
                  {" - "}
                  {zone.moisture_threshold_high}
                </p>

                {zone.devices.length === 0 ? (
                  <p className="mt-3 text-sm text-slate-500">
                    No assigned devices.
                  </p>
                ) : (
                  <div className="mt-3 space-y-3">
                    {zone.devices.map((device) => {
                      const reading = zone.latest_readings.find(
                        (item) => item.device_id === device.id,
                      );

                      return (
                        <div
                          key={device.id}
                          className="rounded-lg bg-slate-50 p-3"
                        >
                          <p className="font-medium">
                            {device.display_name ?? device.device_type}
                          </p>

                          <p className="text-sm text-slate-600">
                            {device.role} / {device.device_type}
                          </p>

                          {reading ? (
                            <div className="mt-2 space-y-1 text-sm">
                              <p>
                                <strong>Latest reading:</strong>{" "}
                                {reading.value} {reading.unit}
                              </p>

                              <p>
                                <strong>Recorded:</strong>{" "}
                                {new Date(reading.recorded_at).toLocaleString()}
                              </p>

                              <p>
                                <strong>Tracking:</strong>{" "}
                                {reading.tracking_enabled
                                  ? "Enabled"
                                  : "Disabled"}
                              </p>

                              <p>
                                <strong>Sampling interval:</strong>{" "}
                                {reading.sampling_interval_seconds} seconds
                              </p>
                            </div>
                          ) : (
                            <p className="mt-2 text-sm text-slate-500">
                              No reading available.
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}

            {overview.zones.length === 0 && (
              <p className="text-sm text-slate-500">
                No zones available for this location.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
