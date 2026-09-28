export type HealthResponse = {
  status: string;
  db: "ok" | "fail";
};

export type SensorDto = {
  id: string;
  device_type: string;
  display_name: string;
  default_config: Record<string, unknown>;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";


export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error("Failed to fetch health status");
  }

  return response.json();
}


export async function fetchSensors(): Promise<SensorDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`);

  if (!response.ok) {
    throw new Error("Failed to fetch sensors");
  }

  return response.json();
}


export async function createSensor(
  type: "moisture" | "light",
  displayName?: string,
): Promise<SensorDto> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name: displayName ?? null,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to create sensor");
  }

  return response.json();
}
export type DeviceDto = {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: string;
  display_name: string;
  default_config: Record<string, unknown>;
};


export async function fetchDevices(
  family?: string,
  role?: "sensor" | "actuator",
): Promise<DeviceDto[]> {
  const params = new URLSearchParams();

  if (family) {
    params.set("family", family);
  }

  if (role) {
    params.set("role", role);
  }

  const query = params.toString();

  const response = await fetch(
    `${API_BASE_URL}/api/devices${query ? `?${query}` : ""}`,
  );

  if (!response.ok) {
    throw new Error("Failed to fetch devices");
  }

  return response.json();
}


export async function provisionDeviceFamily(
  family: "simulation" | "edge",
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/provision?family=${encodeURIComponent(family)}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to provision device family");
  }

  return response.json();
}