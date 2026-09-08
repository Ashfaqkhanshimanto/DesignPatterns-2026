import { Link, Outlet } from "react-router-dom";
import HealthStatus from "./HealthStatus";

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold">Smart Greenhouse</h1>
            <p className="text-sm text-slate-500">
              Design Patterns 2026
            </p>
          </div>

          <div className="flex items-center gap-6">
            <nav className="flex gap-4 text-sm font-medium">
              <Link to="/" className="hover:text-green-700">
                Home
              </Link>
              <Link to="/dashboard" className="hover:text-green-700">
                Dashboard
              </Link>
            </nav>

            <HealthStatus />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}