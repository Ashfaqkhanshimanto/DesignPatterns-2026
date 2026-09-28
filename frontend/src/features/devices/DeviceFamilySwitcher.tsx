type DeviceFamily = "simulation" | "edge";

type Props = {
  selectedFamily: DeviceFamily;
  onFamilyChange: (family: DeviceFamily) => void;
  onProvision: () => void;
  provisioning: boolean;
};

export default function DeviceFamilySwitcher({
  selectedFamily,
  onFamilyChange,
  onProvision,
  provisioning,
}: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        type="button"
        onClick={() => onFamilyChange("simulation")}
        className={`rounded-lg px-4 py-2 text-sm font-medium ${
          selectedFamily === "simulation"
            ? "bg-slate-900 text-white"
            : "border border-slate-300 bg-white text-slate-700"
        }`}
      >
        Simulation
      </button>

      <button
        type="button"
        onClick={() => onFamilyChange("edge")}
        className={`rounded-lg px-4 py-2 text-sm font-medium ${
          selectedFamily === "edge"
            ? "bg-slate-900 text-white"
            : "border border-slate-300 bg-white text-slate-700"
        }`}
      >
        Edge
      </button>

      <button
        type="button"
        onClick={onProvision}
        disabled={provisioning}
        className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
      >
        {provisioning
          ? "Provisioning..."
          : `Provision ${selectedFamily}`}
      </button>
    </div>
  );
}