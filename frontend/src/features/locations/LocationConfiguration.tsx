import { useEffect, useState } from "react";

import {
  addZone,
  assignDeviceToZone,
  createLocationConfig,
  deleteLocation,
  deleteZone,
  fetchDevices,
  fetchLocationConfig,
  fetchLocations,
  updateZone,
  type DeviceDto,
  type LocationConfigDto,
  type LocationDto,
  type ZoneCreateInput,
  type ZoneDto,
} from "../../services/api";


const emptyZone: ZoneCreateInput = {
  name: "",
  moisture_threshold_low: 0.3,
  moisture_threshold_high: 0.7,
  schedule: {},
};


export default function LocationConfiguration() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState("");
  const [config, setConfig] = useState<LocationConfigDto | null>(null);
  const [devices, setDevices] = useState<DeviceDto[]>([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [newLocationName, setNewLocationName] = useState("");
  const [firstZone, setFirstZone] = useState<ZoneCreateInput>({
    ...emptyZone,
  });

  const [newZone, setNewZone] = useState<ZoneCreateInput>({
    ...emptyZone,
  });

  const [editingZoneId, setEditingZoneId] = useState<string | null>(null);
  const [editingZone, setEditingZone] = useState<ZoneCreateInput>({
    ...emptyZone,
  });


  async function loadLocations() {
    const data = await fetchLocations();
    setLocations(data);

    return data;
  }


  async function loadDevices() {
    const data = await fetchDevices();
    setDevices(data);
  }


  async function loadConfig(locationId: string) {
    const data = await fetchLocationConfig(locationId);
    setConfig(data);
  }


  async function refreshSelectedLocation(locationId: string) {
    await Promise.all([
      loadConfig(locationId),
      loadDevices(),
    ]);
  }


  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoading(true);
        setError(null);

        const [locationData] = await Promise.all([
          loadLocations(),
          loadDevices(),
        ]);

        if (locationData.length > 0) {
          const firstLocationId = locationData[0].id;

          setSelectedLocationId(firstLocationId);
          await loadConfig(firstLocationId);
        }
      } catch {
        setError("Could not load greenhouse configuration.");
      } finally {
        setLoading(false);
      }
    }

    loadInitialData();
  }, []);


  async function handleLocationChange(locationId: string) {
    try {
      setSelectedLocationId(locationId);
      setError(null);
      setMessage(null);

      if (!locationId) {
        setConfig(null);
        return;
      }

      await loadConfig(locationId);
    } catch {
      setError("Could not load the selected location.");
    }
  }


  async function handleCreateLocation() {
    try {
      setSaving(true);
      setError(null);
      setMessage(null);

      const created = await createLocationConfig({
        location_name: newLocationName,
        zones: [firstZone],
      });

      await loadLocations();
      await loadDevices();

      setSelectedLocationId(created.location.id);
      setConfig(created);

      setNewLocationName("");
      setFirstZone({
        ...emptyZone,
      });

      setMessage("Location configuration created.");
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not create location.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleAddZone() {
    if (!selectedLocationId) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setMessage(null);

      await addZone(
        selectedLocationId,
        newZone,
      );

      setNewZone({
        ...emptyZone,
      });

      await loadConfig(selectedLocationId);

      setMessage("Zone added.");
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not add zone.",
      );
    } finally {
      setSaving(false);
    }
  }


  function startEditingZone(zone: ZoneDto) {
    setEditingZoneId(zone.id);

    setEditingZone({
      name: zone.name,
      moisture_threshold_low: zone.moisture_threshold_low,
      moisture_threshold_high: zone.moisture_threshold_high,
      schedule: zone.schedule,
    });

    setError(null);
    setMessage(null);
  }


  async function handleUpdateZone() {
    if (!selectedLocationId || !editingZoneId) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setMessage(null);

      await updateZone(
        selectedLocationId,
        editingZoneId,
        editingZone,
      );

      setEditingZoneId(null);

      await loadConfig(selectedLocationId);

      setMessage("Zone updated.");
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not update zone.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDeleteZone(zoneId: string) {
    if (!selectedLocationId) {
      return;
    }

    const confirmed = window.confirm(
      "Delete this zone? Assigned devices will become unassigned.",
    );

    if (!confirmed) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setMessage(null);

      await deleteZone(
        selectedLocationId,
        zoneId,
      );

      await refreshSelectedLocation(
        selectedLocationId,
      );

      setMessage("Zone deleted.");
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not delete zone.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDeleteLocation() {
    if (!selectedLocationId) {
      return;
    }

    const confirmed = window.confirm(
      "Delete this location? Its zones will also be deleted and assigned devices will become unassigned.",
    );

    if (!confirmed) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setMessage(null);

      await deleteLocation(
        selectedLocationId,
      );

      const remainingLocations = await loadLocations();
      await loadDevices();

      if (remainingLocations.length > 0) {
        const nextLocationId = remainingLocations[0].id;

        setSelectedLocationId(nextLocationId);
        await loadConfig(nextLocationId);
      } else {
        setSelectedLocationId("");
        setConfig(null);
      }

      setMessage("Location deleted.");
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not delete location.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDeviceAssignment(
    deviceId: string,
    zoneId: string | null,
  ) {
    try {
      setSaving(true);
      setError(null);
      setMessage(null);

      await assignDeviceToZone(
        deviceId,
        zoneId,
      );

      await loadDevices();

      setMessage(
        zoneId
          ? "Device assigned to zone."
          : "Device unassigned.",
      );
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not update device assignment.",
      );
    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <p className="text-sm text-slate-600">
        Loading configuration...
      </p>
    );
  }


  return (
    <section className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">
          Configuration
        </h2>

        <p className="mt-1 text-sm text-slate-600">
          Create greenhouse locations, configure zones, and assign devices.
        </p>
      </div>


      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}


      {message && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          {message}
        </div>
      )}


      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <h3 className="text-lg font-semibold text-slate-900">
          Create Location
        </h3>

        <p className="mt-1 text-sm text-slate-600">
          A new location must start with at least one zone.
        </p>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="space-y-1">
            <span className="text-sm font-medium text-slate-700">
              Location name
            </span>

            <input
              type="text"
              value={newLocationName}
              onChange={(event) =>
                setNewLocationName(event.target.value)
              }
              placeholder="Main Greenhouse"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            />
          </label>

          <label className="space-y-1">
            <span className="text-sm font-medium text-slate-700">
              First zone name
            </span>

            <input
              type="text"
              value={firstZone.name}
              onChange={(event) =>
                setFirstZone({
                  ...firstZone,
                  name: event.target.value,
                })
              }
              placeholder="Tomato Zone"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            />
          </label>

          <label className="space-y-1">
            <span className="text-sm font-medium text-slate-700">
              Moisture low
            </span>

            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={firstZone.moisture_threshold_low}
              onChange={(event) =>
                setFirstZone({
                  ...firstZone,
                  moisture_threshold_low: Number(event.target.value),
                })
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            />
          </label>

          <label className="space-y-1">
            <span className="text-sm font-medium text-slate-700">
              Moisture high
            </span>

            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              value={firstZone.moisture_threshold_high}
              onChange={(event) =>
                setFirstZone({
                  ...firstZone,
                  moisture_threshold_high: Number(event.target.value),
                })
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            />
          </label>
        </div>

        <button
          type="button"
          disabled={saving}
          onClick={handleCreateLocation}
          className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {saving ? "Saving..." : "Create location"}
        </button>
      </div>


      {locations.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 p-6 text-sm text-slate-600">
          No locations yet. Create your first greenhouse configuration above.
        </div>
      ) : (
        <>
          <div className="flex flex-wrap items-end gap-4">
            <label className="min-w-64 flex-1 space-y-1">
              <span className="text-sm font-medium text-slate-700">
                Selected location
              </span>

              <select
                value={selectedLocationId}
                onChange={(event) =>
                  handleLocationChange(event.target.value)
                }
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
              >
                {locations.map((location) => (
                  <option
                    key={location.id}
                    value={location.id}
                  >
                    {location.name}
                  </option>
                ))}
              </select>
            </label>

            <button
              type="button"
              disabled={saving}
              onClick={handleDeleteLocation}
              className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-700 disabled:opacity-50"
            >
              Delete location
            </button>
          </div>


          {config && (
            <>
              <div>
                <h3 className="text-xl font-semibold text-slate-900">
                  {config.location.name}
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  {config.zones.length} zone
                  {config.zones.length === 1 ? "" : "s"}
                </p>
              </div>


              <div className="grid gap-4 md:grid-cols-2">
                {config.zones.map((zone) => (
                  <article
                    key={zone.id}
                    className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                  >
                    {editingZoneId === zone.id ? (
                      <div className="space-y-4">
                        <input
                          type="text"
                          value={editingZone.name}
                          onChange={(event) =>
                            setEditingZone({
                              ...editingZone,
                              name: event.target.value,
                            })
                          }
                          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                        />

                        <div className="grid grid-cols-2 gap-3">
                          <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={editingZone.moisture_threshold_low}
                            onChange={(event) =>
                              setEditingZone({
                                ...editingZone,
                                moisture_threshold_low: Number(
                                  event.target.value,
                                ),
                              })
                            }
                            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                          />

                          <input
                            type="number"
                            min="0"
                            max="1"
                            step="0.01"
                            value={editingZone.moisture_threshold_high}
                            onChange={(event) =>
                              setEditingZone({
                                ...editingZone,
                                moisture_threshold_high: Number(
                                  event.target.value,
                                ),
                              })
                            }
                            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                          />
                        </div>

                        <div className="flex gap-2">
                          <button
                            type="button"
                            disabled={saving}
                            onClick={handleUpdateZone}
                            className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
                          >
                            Save
                          </button>

                          <button
                            type="button"
                            onClick={() => setEditingZoneId(null)}
                            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h4 className="font-semibold text-slate-900">
                              {zone.name}
                            </h4>

                            <p className="mt-1 text-xs text-slate-500">
                              Zone ID: {zone.id}
                            </p>
                          </div>
                        </div>

                        <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                          <div className="rounded-lg bg-slate-50 p-3">
                            <p className="text-slate-500">
                              Moisture low
                            </p>

                            <p className="font-semibold text-slate-900">
                              {zone.moisture_threshold_low}
                            </p>
                          </div>

                          <div className="rounded-lg bg-slate-50 p-3">
                            <p className="text-slate-500">
                              Moisture high
                            </p>

                            <p className="font-semibold text-slate-900">
                              {zone.moisture_threshold_high}
                            </p>
                          </div>
                        </div>

                        <div className="mt-4 flex gap-2">
                          <button
                            type="button"
                            onClick={() => startEditingZone(zone)}
                            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium"
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            disabled={saving}
                            onClick={() => handleDeleteZone(zone.id)}
                            className="rounded-lg border border-red-300 px-3 py-2 text-sm font-medium text-red-700 disabled:opacity-50"
                          >
                            Delete
                          </button>
                        </div>
                      </>
                    )}
                  </article>
                ))}
              </div>


              <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
                <h3 className="text-lg font-semibold text-slate-900">
                  Add Zone
                </h3>

                <div className="mt-4 grid gap-4 md:grid-cols-3">
                  <input
                    type="text"
                    value={newZone.name}
                    onChange={(event) =>
                      setNewZone({
                        ...newZone,
                        name: event.target.value,
                      })
                    }
                    placeholder="Zone name"
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                  />

                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={newZone.moisture_threshold_low}
                    onChange={(event) =>
                      setNewZone({
                        ...newZone,
                        moisture_threshold_low: Number(
                          event.target.value,
                        ),
                      })
                    }
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                  />

                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={newZone.moisture_threshold_high}
                    onChange={(event) =>
                      setNewZone({
                        ...newZone,
                        moisture_threshold_high: Number(
                          event.target.value,
                        ),
                      })
                    }
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                  />
                </div>

                <button
                  type="button"
                  disabled={saving}
                  onClick={handleAddZone}
                  className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
                >
                  Add zone
                </button>
              </div>


              <div>
                <h3 className="text-lg font-semibold text-slate-900">
                  Device Assignment
                </h3>

                <p className="mt-1 text-sm text-slate-600">
                  Assign devices to zones in this location or leave them unassigned.
                </p>

                <div className="mt-4 space-y-3">
                  {devices.map((device) => (
                    <div
                      key={device.id}
                      className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 md:flex-row md:items-center md:justify-between"
                    >
                      <div>
                        <p className="font-medium text-slate-900">
                          {device.display_name}
                        </p>

                        <p className="text-sm text-slate-500">
                          {device.device_type} · {device.device_family}
                        </p>
                      </div>

                      <select
                        value={
                          device.location_id === selectedLocationId
                            ? device.zone_id ?? ""
                            : ""
                        }
                        disabled={saving}
                        onChange={(event) =>
                          handleDeviceAssignment(
                            device.id,
                            event.target.value || null,
                          )
                        }
                        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                      >
                        <option value="">
                          Unassigned
                        </option>

                        {config.zones.map((zone) => (
                          <option
                            key={zone.id}
                            value={zone.id}
                          >
                            {zone.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </>
      )}
    </section>
  );
}