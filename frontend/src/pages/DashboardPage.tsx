import DeviceList from "../features/devices/DeviceList";
import SensorList from "../features/sensors/SensorList";


const otherSections = [
  {
    id: "configuration",
    title: "Configuration",
    description: "Greenhouse and zone configuration will appear here.",
  },
  {
    id: "automation",
    title: "Automation",
    description: "Automation strategies and policies will appear here.",
  },
  {
    id: "overview",
    title: "Overview",
    description: "System overview information will appear here.",
  },
  {
    id: "controls",
    title: "Controls",
    description: "Actuator controls will appear here.",
  },
  {
    id: "events",
    title: "Events",
    description: "Alerts and live events will appear here.",
  },
];


export default function DashboardPage() {
  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">
          Dashboard
        </h2>

        <p className="mt-2 text-slate-600">
          Smart greenhouse system overview and controls.
        </p>
      </div>


      <article
        id="sensors"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <h3 className="text-xl font-semibold">
          Sensors
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Create and view greenhouse sensors.
        </p>

        <SensorList />
      </article>


      <article
        id="devices"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <DeviceList />
      </article>


      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {otherSections.map((section) => (
          <article
            key={section.id}
            id={section.id}
            className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold">
              {section.title}
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              {section.description}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}