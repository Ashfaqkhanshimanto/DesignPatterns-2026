import { useEffect, useState } from "react";

import {
  createSensor,
  fetchDevices,
  fetchSensorReadings,
  fetchSensors,
  readSensorNow,
  updateDeviceSampling,
  type DeviceDto,
  type ReadingDto,
  type SensorDto,
} from "../../services/api";


export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [readings, setReadings] = useState<
    Record<string, ReadingDto[]>
  >({});
  const [intervals, setIntervals] = useState<
    Record<string, number>
  >({});
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [busySensorId, setBusySensorId] = useState<string | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);


  async function loadSensors() {
    try {
      setError(null);

      const [sensorData, deviceData] = await Promise.all([
        fetchSensors(),
        fetchDevices(undefined, "sensor"),
      ]);

      setSensors(sensorData);
      setDevices(deviceData);

      const nextIntervals: Record<string, number> = {};

      for (const device of deviceData) {
        nextIntervals[device.id] =
          device.sampling_interval_seconds;
      }

      setIntervals(nextIntervals);
    } catch {
      setError("Could not load sensors");
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void loadSensors();
  }, []);


  async function handleCreate(
    type: "moisture" | "light",
  ) {
    try {
      setCreating(true);
      setError(null);

      await createSensor(type);
      await loadSensors();
    } catch {
      setError("Could not create sensor");
    } finally {
      setCreating(false);
    }
  }


  async function handleReadNow(sensorId: string) {
    try {
      setBusySensorId(sensorId);
      setError(null);

      await readSensorNow(sensorId);

      const history = await fetchSensorReadings(
        sensorId,
        5,
      );

      setReadings((current) => ({
        ...current,
        [sensorId]: history,
      }));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not read sensor",
      );
    } finally {
      setBusySensorId(null);
    }
  }


  async function handleLoadHistory(sensorId: string) {
    try {
      setBusySensorId(sensorId);
      setError(null);

      const history = await fetchSensorReadings(
        sensorId,
        5,
      );

      setReadings((current) => ({
        ...current,
        [sensorId]: history,
      }));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not load readings",
      );
    } finally {
      setBusySensorId(null);
    }
  }


  async function handleSaveSampling(device: DeviceDto) {
    const interval =
      intervals[device.id] ??
      device.sampling_interval_seconds;

    if (interval < 5) {
      setError(
        "Sampling interval must be at least 5 seconds.",
      );
      return;
    }

    try {
      setBusySensorId(device.id);
      setError(null);

      const updated = await updateDeviceSampling(
        device.id,
        interval,
        device.tracking_enabled,
      );

      setDevices((current) =>
        current.map((item) =>
          item.id === updated.id ? updated : item,
        ),
      );
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not update sampling settings",
      );
    } finally {
      setBusySensorId(null);
    }
  }


  async function handleTrackingChange(
    device: DeviceDto,
    trackingEnabled: boolean,
  ) {
    const interval =
      intervals[device.id] ??
      device.sampling_interval_seconds;

    try {
      setBusySensorId(device.id);
      setError(null);

      const updated = await updateDeviceSampling(
        device.id,
        interval,
        trackingEnabled,
      );

      setDevices((current) =>
        current.map((item) =>
          item.id === updated.id ? updated : item,
        ),
      );
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not update tracking",
      );
    } finally {
      setBusySensorId(null);
    }
  }


  return (
    <div className="mt-4 space-y-4">
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          disabled={creating}
          onClick={() => void handleCreate("moisture")}
          className="rounded-lg bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Add Moisture Sensor
        </button>

        <button
          type="button"
          disabled={creating}
          onClick={() => void handleCreate("light")}
          className="rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Add Light Sensor
        </button>
      </div>


      {creating && (
        <p className="text-sm text-slate-500">
          Creating sensor...
        </p>
      )}


      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}


      {loading ? (
        <p className="text-sm text-slate-500">
          Loading sensors...
        </p>
      ) : sensors.length === 0 ? (
        <p className="text-sm text-slate-500">
          No sensors have been added yet.
        </p>
      ) : (
        <div className="space-y-3">
          {sensors.map((sensor) => {
            const device = devices.find(
              (item) => item.id === sensor.id,
            );

            const sensorReadings =
              readings[sensor.id] ?? [];

            const latestReading =
              sensorReadings.length > 0
                ? sensorReadings[0]
                : null;

            const busy =
              busySensorId === sensor.id;

            return (
              <div
                key={sensor.id}
                className="rounded-lg border border-slate-200 bg-slate-50 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="font-semibold">
                      {sensor.display_name}
                    </p>

                    <p className="text-sm text-slate-500">
                      {sensor.device_type}
                    </p>
                  </div>

                  <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                    sensor
                  </span>
                </div>


                <div className="mt-3 text-sm text-slate-600">
                  {Object.entries(
                    sensor.default_config,
                  ).map(([key, value]) => (
                    <div
                      key={key}
                      className="flex justify-between gap-4 border-t border-slate-200 py-1"
                    >
                      <span>{key}</span>

                      <span className="font-medium">
                        {String(value)}
                      </span>
                    </div>
                  ))}
                </div>


                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() =>
                      void handleReadNow(sensor.id)
                    }
                    className="rounded-lg bg-green-700 px-3 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:opacity-50"
                  >
                    Read now
                  </button>

                  <button
                    type="button"
                    disabled={busy}
                    onClick={() =>
                      void handleLoadHistory(sensor.id)
                    }
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
                  >
                    Load readings
                  </button>
                </div>


                {latestReading && (
                  <div className="mt-4 rounded-lg bg-white p-3">
                    <p className="text-xs font-semibold uppercase text-slate-500">
                      Latest reading
                    </p>

                    <p className="mt-1 text-lg font-semibold">
                      {latestReading.value}{" "}
                      {latestReading.unit}
                    </p>

                    <p className="text-xs text-slate-500">
                      Source: {latestReading.source}
                    </p>

                    <p className="text-xs text-slate-500">
                      {new Date(
                        latestReading.recorded_at,
                      ).toLocaleString()}
                    </p>
                  </div>
                )}


                {sensorReadings.length > 0 && (
                  <div className="mt-4">
                    <p className="mb-2 text-sm font-semibold">
                      Recent readings
                    </p>

                    <div className="space-y-1">
                      {sensorReadings.map(
                        (reading, index) => (
                          <div
                            key={`${reading.recorded_at}-${index}`}
                            className="flex flex-wrap justify-between gap-2 rounded bg-white px-3 py-2 text-sm"
                          >
                            <span>
                              {reading.value}{" "}
                              {reading.unit}
                            </span>

                            <span className="text-slate-500">
                              {reading.source}
                            </span>

                            <span className="text-slate-500">
                              {new Date(
                                reading.recorded_at,
                              ).toLocaleString()}
                            </span>
                          </div>
                        ),
                      )}
                    </div>
                  </div>
                )}


                {device && (
                  <div className="mt-4 border-t border-slate-200 pt-4">
                    <p className="mb-3 text-sm font-semibold">
                      Automatic sampling
                    </p>

                    <div className="flex flex-wrap items-end gap-3">
                      <label className="text-sm">
                        <span className="mb-1 block text-slate-600">
                          Interval (seconds)
                        </span>

                        <input
                          type="number"
                          min={5}
                          value={
                            intervals[device.id] ??
                            device.sampling_interval_seconds
                          }
                          onChange={(event) =>
                            setIntervals(
                              (current) => ({
                                ...current,
                                [device.id]:
                                  Number(
                                    event.target.value,
                                  ),
                              }),
                            )
                          }
                          className="w-32 rounded-lg border border-slate-300 bg-white px-3 py-2"
                        />
                      </label>

                      <label className="flex items-center gap-2 pb-2 text-sm">
                        <input
                          type="checkbox"
                          checked={
                            device.tracking_enabled
                          }
                          disabled={busy}
                          onChange={(event) =>
                            void handleTrackingChange(
                              device,
                              event.target.checked,
                            )
                          }
                        />

                        Tracking enabled
                      </label>

                      <button
                        type="button"
                        disabled={busy}
                        onClick={() =>
                          void handleSaveSampling(
                            device,
                          )
                        }
                        className="rounded-lg bg-slate-800 px-3 py-2 text-sm font-medium text-white hover:bg-slate-900 disabled:opacity-50"
                      >
                        Save sampling
                      </button>
                    </div>

                    <p className="mt-2 text-xs text-slate-500">
                      Current saved interval:{" "}
                      {
                        device.sampling_interval_seconds
                      }{" "}
                      seconds
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}