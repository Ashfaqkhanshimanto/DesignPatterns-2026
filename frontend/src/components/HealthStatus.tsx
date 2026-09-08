import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "../services/api";

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data);
        setError(false);
      })
      .catch(() => {
        setError(true);
      });
  }, []);

  if (error) {
    return (
      <span className="rounded-full bg-red-100 px-3 py-1 text-sm font-medium text-red-700">
        API unavailable
      </span>
    );
  }

  if (!health) {
    return (
      <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-600">
        Checking...
      </span>
    );
  }

  const healthy = health.status === "ok" && health.db === "ok";

  return (
    <span
      className={`rounded-full px-3 py-1 text-sm font-medium ${
        healthy
          ? "bg-green-100 text-green-700"
          : "bg-yellow-100 text-yellow-700"
      }`}
    >
      API: {health.status} | DB: {health.db}
    </span>
  );
}