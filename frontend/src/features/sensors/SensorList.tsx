import { useEffect, useState } from "react";

import {
  createSensor,
  fetchSensors,
  type SensorDto,
} from "../../services/api";


export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);


  async function loadSensors() {
    try {
      setError(null);

      const data = await fetchSensors();

      setSensors(data);
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

      const sensor = await createSensor(type);

      setSensors((current) => [
        sensor,
        ...current,
      ]);
    } catch {
      setError("Could not create sensor");
    } finally {
      setCreating(false);
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
          {sensors.map((sensor) => (
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
                {Object.entries(sensor.default_config).map(
                  ([key, value]) => (
                    <div
                      key={key}
                      className="flex justify-between gap-4 border-t border-slate-200 py-1"
                    >
                      <span>{key}</span>
                      <span className="font-medium">
                        {String(value)}
                      </span>
                    </div>
                  ),
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}