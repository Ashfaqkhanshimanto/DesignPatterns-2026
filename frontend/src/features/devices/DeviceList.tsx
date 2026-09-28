import { useEffect, useState } from "react";

import {
  fetchDevices,
  provisionDeviceFamily,
  type DeviceDto,
} from "../../services/api";

import DeviceFamilySwitcher from "./DeviceFamilySwitcher";


type DeviceFamily = "simulation" | "edge";


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

      const data = await fetchDevices(
        family,
      );

      setDevices(data);
    } catch {
      setError(
        "Could not load devices.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadDevices(
      selectedFamily,
    );
  }, [selectedFamily]);


  async function handleProvision() {
    try {
      setProvisioning(true);
      setError(null);

      await provisionDeviceFamily(
        selectedFamily,
      );

      await loadDevices(
        selectedFamily,
      );
    } catch {
      setError(
        "Could not provision device family.",
      );
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
                </div>
              </div>

              <div className="mt-4 space-y-2 text-sm text-slate-600">
                {Object.entries(
                  device.default_config,
                ).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex justify-between gap-4 border-b border-slate-100 pb-2"
                  >
                    <span>
                      {key}
                    </span>

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