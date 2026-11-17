
import { useEffect, useState } from "react";

import {
  fetchDevices,
  type DeviceDto,
} from "../../services/api";

type CommandType =
  | "start_pump"
  | "stop_pump"
  | "set_light_level";

type CommandLogDto = {
  id: string;
  command_type: string;
  device_id: string;
  payload: Record<string, unknown>;
  status: "success" | "failed" | "rejected";
  error_message: string | null;
  created_at: string;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000";

export default function CommandPanel() {
  const [actuators, setActuators] =
    useState<DeviceDto[]>([]);

  const [history, setHistory] =
    useState<CommandLogDto[]>([]);

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [notice, setNotice] =
    useState<string | null>(null);

  const [lightLevel, setLightLevel] = useState(1);

  async function loadData() {
    setLoading(true);
    setError(null);

    try {
      const [devices, response] = await Promise.all([
        fetchDevices(undefined, "actuator"),
        fetch(`${API_BASE_URL}/api/commands?limit=50`),
      ]);

      if (!response.ok) {
        throw new Error("Could not load command history");
      }

      const records: CommandLogDto[] =
        await response.json();

      setActuators(devices);
      setHistory(records);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load command data",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function executeCommand(
    deviceId: string,
    commandType: CommandType,
  ) {
    setBusy(true);
    setNotice(null);
    setError(null);

    try {
      const payload =
        commandType === "set_light_level"
          ? { level: lightLevel }
          : {};

      const response = await fetch(
        `${API_BASE_URL}/api/commands`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            command_type: commandType,
            device_id: deviceId,
            payload,
          }),
        },
      );

      const result = await response.json();

      if (!response.ok && response.status !== 409) {
        throw new Error(
          result.detail ?? "Command request failed",
        );
      }

      setNotice(
        `${commandType}: ${result.status}` +
          (result.error_message
            ? ` — ${result.error_message}`
            : ""),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Command failed",
      );
    } finally {
      await loadData();
      setBusy(false);
    }
  }

  function canExecute(
    device: DeviceDto,
    command: CommandType,
  ) {
    return (
      !busy &&
      !loading &&
      device.allowed_commands.includes(command)
    );
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xl font-semibold text-slate-900">
            Actuator Controls
          </h3>
          <p className="mt-1 text-sm text-slate-600">
            Execute simulated commands using the
            Phase 10 Command Pattern.
          </p>
        </div>

        <button
          type="button"
          disabled={loading || busy}
          onClick={() => void loadData()}
          className="rounded-lg border border-slate-300 px-4 py-2 text-sm disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {notice && (
        <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-800">
          {notice}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">
          Loading actuators...
        </p>
      ) : actuators.length === 0 ? (
        <p className="text-sm text-slate-500">
          No actuators available.
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {actuators.map((device) => (
            <div
              key={device.id}
              className="rounded-lg border border-slate-200 p-4"
            >
              <h4 className="font-semibold text-slate-900">
                {device.display_name}
              </h4>

              <p className="mt-1 text-xs text-slate-500">
                {device.device_family} / {device.device_type}
              </p>

              <p className="mt-2 text-sm">
                State:{" "}
                <strong>{device.state ?? "unknown"}</strong>
              </p>

              <div className="mt-3 flex flex-wrap gap-2">
                {device.device_type === "water_pump" && (
                  <>
                    <button
                      type="button"
                      disabled={
                        !canExecute(device, "start_pump")
                      }
                      onClick={() =>
                        void executeCommand(
                          device.id,
                          "start_pump",
                        )
                      }
                      className="rounded-lg bg-green-700 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-30"
                    >
                      Start Pump
                    </button>

                    <button
                      type="button"
                      disabled={
                        !canExecute(device, "stop_pump")
                      }
                      onClick={() =>
                        void executeCommand(
                          device.id,
                          "stop_pump",
                        )
                      }
                      className="rounded-lg bg-red-700 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-30"
                    >
                      Stop Pump
                    </button>
                  </>
                )}

                {device.device_type === "grow_light" && (
                  <div className="flex flex-wrap items-center gap-2">
                    <label className="text-sm">
                      Light level
                      <input
                        type="number"
                        min="1"
                        max="100"
                        value={lightLevel}
                        onChange={(event) =>
                          setLightLevel(
                            Math.min(
                              100,
                              Math.max(
                                1,
                                Number(event.target.value) || 1,
                              ),
                            ),
                          )
                        }
                        className="ml-2 w-20 rounded border border-slate-300 px-2 py-1"
                      />
                    </label>

                    <button
                      type="button"
                      disabled={
                        !canExecute(
                          device,
                          "set_light_level",
                        )
                      }
                      onClick={() =>
                        void executeCommand(
                          device.id,
                          "set_light_level",
                        )
                      }
                      className="rounded-lg bg-blue-700 px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-30"
                    >
                      Set Light Level
                    </button>
                  </div>
                )}
              </div>

              <p className="mt-3 text-xs text-slate-500">
                Available:{" "}
                {device.allowed_commands.join(", ") ||
                  "None"}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="space-y-3">
        <h3 className="text-xl font-semibold text-slate-900">
          Command History
        </h3>

        {history.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">
            No commands recorded yet.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-100">
                <tr>
                  <th className="p-3">Time</th>
                  <th className="p-3">Command</th>
                  <th className="p-3">Device ID</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Error</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item) => (
                  <tr
                    key={item.id}
                    className="border-t border-slate-200"
                  >
                    <td className="whitespace-nowrap p-3">
                      {new Date(
                        item.created_at,
                      ).toLocaleString()}
                    </td>

                    <td className="p-3">
                      {item.command_type}
                    </td>

                    <td className="p-3 font-mono text-xs">
                      {item.device_id}
                    </td>

                    <td className="p-3">
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-semibold ${
                          item.status === "success"
                            ? "bg-green-100 text-green-800"
                            : item.status === "failed"
                              ? "bg-red-100 text-red-800"
                              : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {item.status}
                      </span>
                    </td>

                    <td className="p-3 text-slate-600">
                      {item.error_message ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <p className="text-xs text-slate-500">
        Buttons are disabled when the actuator's
        allowed_commands list does not permit the action.
        This phase uses simulated actuators only.
      </p>
    </section>
  );
}
