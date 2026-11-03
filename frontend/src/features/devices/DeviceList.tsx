
import { useEffect, useState } from "react";

import {
  fetchDevices,
  provisionDeviceFamily,
  type DeviceDto,
} from "../../services/api";

import DeviceFamilySwitcher from "./DeviceFamilySwitcher";


type DeviceFamily = "simulation" | "edge";


function getStateColor(state: string | null): string {
  switch (state) {
    case "running":
      return "bg-green-100 text-green-800";
    case "idle":
      return "bg-blue-100 text-blue-800";
    case "off":
      return "bg-slate-200 text-slate-700";
    case "error":
      return "bg-red-100 text-red-800";
    case "maintenance":
      return "bg-yellow-100 text-yellow-800";
    default:
      return "bg-gray-100 text-gray-600";
  }
}


export default function DeviceList() {
  const [selectedFamily, setSelectedFamily] =
    useState<DeviceFamily>("simulation");

  const [devices, setDevices] =
    useState<DeviceDto[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [provisioning, setProvisioning] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function loadDevices(
    family: DeviceFamily,
  ) {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchDevices(family);

      setDevices(data);
    } catch {
      setError("Could not load devices.");
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadDevices(selectedFamily);
  }, [selectedFamily]);


  async function handleProvision() {
    try {
      setProvisioning(true);
      setError(null);

      await provisionDeviceFamily(selectedFamily);

      await loadDevices(selectedFamily);
    } catch {
      setError("Could not provision device family.");
    } finally {
      setProvisioning(false);
    }
  }


  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">
          Devices
        </h2>

        <p className="mt-1 text-sm text-slate-600">
          Provision and view coherent device families.
        </p>
      </div>

      <DeviceFamilySwitcher
        selectedFamily={selectedFamily}
        onFamilyChange={setSelectedFamily}
        onProvision={handleProvision}
        provisioning={provisioning}
      />

      <button
        type="button"
        onClick={() => loadDevices(selectedFamily)}
        disabled={loading || provisioning}
        className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
      >
        Refresh Devices
      </button>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-600">
          Loading devices...
        </p>
      ) : devices.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 p-6 text-sm text-slate-600">
          No devices found for the selected family.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {devices.map((device) => (
            <article
              key={device.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-slate-900">
                    {device.display_name}
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    {device.device_type}
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {device.role}
                  </span>

                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
                    {device.device_family}
                  </span>

                  {device.role === "actuator" && (
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${getStateColor(device.state)}`}
                      title={`Current actuator state: ${device.state ?? "unknown"}`}
                    >
                      {device.state ?? "unknown"}
                    </span>
                  )}
                </div>
              </div>

              {device.role === "actuator" && (
                <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <p className="text-sm font-semibold text-slate-800">
                    Actuator State
                  </p>

                  <p className="mt-1 text-sm">
                    Current state:{" "}
                    <strong>{device.state ?? "unknown"}</strong>
                  </p>

                  <p className="mt-2 text-sm font-medium text-slate-700">
                    Allowed Commands
                  </p>

                  {device.allowed_commands.length > 0 ? (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {device.allowed_commands.map((command) => (
                        <span
                          key={command}
                          title="Allowed in the current state. Command execution will be added in Phase 10."
                          className="rounded-md border border-blue-200 bg-blue-50 px-2 py-1 text-xs text-blue-800"
                        >
                          {command}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-1 text-sm text-slate-500">
                      No commands available.
                    </p>
                  )}

                  <p className="mt-3 text-xs text-slate-500">
                    Only commands permitted by the current
                    state are listed. Command controls will
                    be added in Phase 10.
                  </p>
                </div>
              )}

              <div className="mt-4 space-y-2 text-sm text-slate-600">
                {Object.entries(
                  device.default_config,
                ).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex justify-between gap-4 border-b border-slate-100 pb-2"
                  >
                    <span>{key}</span>

                    <span className="font-medium text-slate-900">
                      {String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
