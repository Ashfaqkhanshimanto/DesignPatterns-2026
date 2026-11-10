
import { useEffect, useState } from "react";

type ExecutionDto = {
  id: string;
  device_id: string;
  success: boolean;
  policy_applied: string[];
  message: string | null;
  created_at: string;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000";

export default function ExecutionLog() {
  const [executions, setExecutions] =
    useState<ExecutionDto[]>([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadExecutions() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/actuators/executions?limit=20`,
      );

      if (!response.ok) {
        throw new Error("Unable to load executions");
      }

      const data: ExecutionDto[] = await response.json();
      setExecutions(data);
    } catch {
      setError("Could not load actuator execution history.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadExecutions();
  }, []);

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xl font-semibold text-slate-900">
            Actuator Execution Log
          </h3>
          <p className="mt-1 text-sm text-slate-600">
            Recent simulated actuator attempts and applied policies.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void loadExecutions()}
          disabled={loading}
          className="rounded-lg bg-slate-800 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Loading..." : "Refresh Executions"}
        </button>
      </div>

      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-slate-700">
        <p>
          In Phase 9, any command succeeds unless its actuator
          has been in the running state for at least 30 minutes.
        </p>
        <p className="mt-2">
          Successful attempts have an empty message and
          the logging policy.
        </p>
        <p className="mt-2">
          Blocked attempts show "Max run time exceeded"
          with maxRunTime and logging policies.
        </p>
        <p className="mt-2 font-medium">
          These commands are simulated. No physical hardware
          is controlled.
        </p>
      </div>

      {error && (
        <p className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">
          Loading executions...
        </p>
      ) : executions.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 p-6">
          <p className="text-sm text-slate-600">
            No actuator executions recorded yet.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-100 text-slate-700">
              <tr>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Device ID</th>
                <th className="px-4 py-3">Result</th>
                <th className="px-4 py-3">Policies</th>
                <th className="px-4 py-3">Message</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100 bg-white">
              {executions.map((execution) => (
                <tr key={execution.id}>
                  <td className="whitespace-nowrap px-4 py-3">
                    {new Date(
                      execution.created_at,
                    ).toLocaleString()}
                  </td>

                  <td className="px-4 py-3 font-mono text-xs">
                    {execution.device_id}
                  </td>

                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        execution.success
                          ? "bg-green-100 text-green-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {execution.success ? "Success" : "Blocked / Failed"}
                    </span>
                  </td>

                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {execution.policy_applied.map((policy) => (
                        <span
                          key={policy}
                          className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700"
                        >
                          {policy}
                        </span>
                      ))}
                    </div>
                  </td>

                  <td className="px-4 py-3 text-slate-600">
                    {execution.message ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
