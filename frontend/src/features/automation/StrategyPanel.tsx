
import { useEffect, useState } from "react";

import {
  evaluateAutomation,
  fetchLocations,
  fetchLocationConfig,
  fetchSavedStrategy,
  saveAutomationStrategy,
  type AutomationEvaluationDto,
  type LocationDto,
  type StrategyKey,
} from "../../services/api";

export default function StrategyPanel() {
  const [locations, setLocations] = useState<LocationDto[]>([]);
  const [locationId, setLocationId] = useState("");
  const [strategyKey, setStrategyKey] =
    useState<StrategyKey>("conservative");

  const [savedKey, setSavedKey] = useState<StrategyKey | null>(null);
  const [zoneNames, setZoneNames] = useState<Record<string, string>>({});
  const [result, setResult] =
    useState<AutomationEvaluationDto | null>(null);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchLocations()
      .then((data) => {
        setLocations(data);
        if (data.length > 0) {
          setLocationId(data[0].id);
        }
      })
      .catch(() => setError("Could not load locations."));
  }, []);

  useEffect(() => {
    if (!locationId) return;

    let cancelled = false;

    setResult(null);
    setSavedKey(null);
    setZoneNames({});
    setMessage("");
    setError("");

    Promise.all([
      fetchSavedStrategy(locationId),
      fetchLocationConfig(locationId),
    ])
      .then(([saved, config]) => {
        if (cancelled) return;

        setStrategyKey(saved.strategy_key);
        setSavedKey(saved.strategy_key);

        setZoneNames(
          Object.fromEntries(
            config.zones.map((zone) => [zone.id, zone.name]),
          ),
        );
      })
      .catch(() => {
        if (!cancelled) {
          setError("Could not load automation settings.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [locationId]);

  async function handleSave() {
    if (!locationId) return;

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const saved = await saveAutomationStrategy(
        locationId,
        strategyKey,
      );

      setSavedKey(saved.strategy_key);
      setResult(null);
      setMessage("Strategy saved successfully.");
    } catch {
      setError("Could not save strategy.");
    } finally {
      setLoading(false);
    }
  }

  async function handleEvaluate() {
    if (!locationId) return;

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const evaluation = await evaluateAutomation(locationId);
      setResult(evaluation);
      setMessage("Evaluation completed.");
    } catch {
      setError("Could not evaluate automation.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-xl font-semibold">
          Automation Strategy
        </h3>
        <p className="mt-1 text-sm text-slate-500">
          Choose how the greenhouse decides when irrigation is needed.
        </p>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium">
          Location
        </label>
        <select
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

      <div className="space-y-2">
        <label className="block text-sm font-medium">
          Irrigation Strategy
        </label>
        <select
          value={strategyKey}
          onChange={(event) =>
            setStrategyKey(event.target.value as StrategyKey)
          }
          className="w-full rounded-lg border border-slate-300 p-2"
        >
          <option value="conservative">Conservative</option>
          <option value="aggressive">Aggressive</option>
        </select>

        <p className="text-xs text-slate-500">
          Saved strategy: {savedKey ?? "Not loaded"}
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleSave}
          disabled={loading || !locationId}
          className="rounded-lg bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          Save Strategy
        </button>

        <button
          onClick={handleEvaluate}
          disabled={loading || !locationId || savedKey === null}
          className="rounded-lg bg-green-600 px-4 py-2 text-white disabled:opacity-50"
        >
          Evaluate
        </button>
      </div>

      {savedKey !== null && strategyKey !== savedKey && (
        <p className="text-sm text-amber-700">
          Your selection is not saved yet. Save it before evaluating.
        </p>
      )}

      {message && (
        <p className="text-sm text-green-700">{message}</p>
      )}

      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}

      {result && (
        <div className="space-y-3 rounded-lg border border-slate-200 p-4">
          <h4 className="font-semibold">
            Evaluation Result
          </h4>

          <p>
            <strong>Strategy:</strong> {result.strategy_key}
          </p>

          <p>
            <strong>Overall action:</strong> {result.action}
          </p>

          <p className="text-sm">{result.reason}</p>

          <div className="space-y-3">
            {result.zones.map((zone) => (
              <div
                key={zone.zone_id}
                className="rounded-lg bg-slate-50 p-3"
              >
                <p className="font-medium">
                  {zoneNames[zone.zone_id] ?? zone.zone_id}
                </p>

                <p className="text-sm">
                  Action: <strong>{zone.action}</strong>
                </p>

                <p className="text-sm text-slate-600">
                  {zone.reason}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
