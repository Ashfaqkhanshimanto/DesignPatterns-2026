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


export type DeviceDto = {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: string;
  display_name: string;
  default_config: Record<string, unknown>;
  zone_id: string | null;
  location_id: string | null;
  sampling_interval_seconds: number;
  tracking_enabled: boolean;
};


export type ReadingDto = {
  device_id: string;
  value: number;
  unit: string;
  source: string;
  recorded_at: string;
};


export type LocationDto = {
  id: string;
  name: string;
};


export type ZoneDto = {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
};


export type LocationConfigDto = {
  location: LocationDto;
  zones: ZoneDto[];
};


export type ZoneCreateInput = {
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
};


export type LocationConfigCreateInput = {
  location_name: string;
  zones: ZoneCreateInput[];
};


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";


// ---------------------------------------------------------
// Health
// ---------------------------------------------------------

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${API_BASE_URL}/health`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch health status",
    );
  }

  return response.json();
}


// ---------------------------------------------------------
// Phase 2 - Sensors
// ---------------------------------------------------------

export async function fetchSensors(): Promise<SensorDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch sensors",
    );
  }

  return response.json();
}


export async function createSensor(
  type: "moisture" | "light",
  displayName?: string,
): Promise<SensorDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type,
        display_name: displayName ?? null,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      "Failed to create sensor",
    );
  }

  return response.json();
}


// ---------------------------------------------------------
// Phase 3 - Devices
// ---------------------------------------------------------

export async function fetchDevices(
  family?: string,
  role?: "sensor" | "actuator",
): Promise<DeviceDto[]> {
  const params = new URLSearchParams();

  if (family) {
    params.set(
      "family",
      family,
    );
  }

  if (role) {
    params.set(
      "role",
      role,
    );
  }

  const query = params.toString();

  const response = await fetch(
    `${API_BASE_URL}/api/devices${query ? `?${query}` : ""}`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch devices",
    );
  }

  return response.json();
}


export async function provisionDeviceFamily(
  family: "simulation" | "edge",
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/provision?family=${encodeURIComponent(
      family,
    )}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(
      "Failed to provision device family",
    );
  }

  return response.json();
}


// ---------------------------------------------------------
// Phase 4 - Locations
// ---------------------------------------------------------

export async function fetchLocations(): Promise<LocationDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch locations",
    );
  }

  return response.json();
}


export async function fetchLocationConfig(
  locationId: string,
): Promise<LocationConfigDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/config`,
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch location configuration",
    );
  }

  return response.json();
}


export async function createLocationConfig(
  input: LocationConfigCreateInput,
): Promise<LocationConfigDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/config`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        input,
      ),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to create location configuration",
    );
  }

  return response.json();
}


export async function deleteLocation(
  locationId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to delete location",
    );
  }
}


// ---------------------------------------------------------
// Phase 4 - Zones
// ---------------------------------------------------------

export async function addZone(
  locationId: string,
  input: ZoneCreateInput,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        input,
      ),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to add zone",
    );
  }

  return response.json();
}


export async function updateZone(
  locationId: string,
  zoneId: string,
  input: ZoneCreateInput,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(
        input,
      ),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to update zone",
    );
  }

  return response.json();
}


export async function deleteZone(
  locationId: string,
  zoneId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to delete zone",
    );
  }
}


// ---------------------------------------------------------
// Phase 4 - Device assignment
// ---------------------------------------------------------

export async function assignDeviceToZone(
  deviceId: string,
  zoneId: string | null,
): Promise<DeviceDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/zone`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        zone_id: zoneId,
      }),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to assign device",
    );
  }

  return response.json();
}


// ---------------------------------------------------------
// Phase 5 - Sensor readings
// ---------------------------------------------------------

export async function readSensorNow(
  deviceId: string,
): Promise<ReadingDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors/${deviceId}/read`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to read sensor",
    );
  }

  return response.json();
}


export async function fetchSensorReadings(
  deviceId: string,
  limit = 10,
): Promise<ReadingDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors/${deviceId}/readings?limit=${limit}`,
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      error?.detail ??
        "Failed to fetch sensor readings",
    );
  }

  return response.json();
}


// ---------------------------------------------------------
// Phase 5 - Sampling settings
// ---------------------------------------------------------

export async function updateDeviceSampling(
  deviceId: string,
  samplingIntervalSeconds: number,
  trackingEnabled: boolean,
): Promise<DeviceDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/sampling`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sampling_interval_seconds:
          samplingIntervalSeconds,
        tracking_enabled: trackingEnabled,
      }),
    },
  );

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => null);

    throw new Error(
      typeof error?.detail === "string"
        ? error.detail
        : "Failed to update sampling settings",
    );
  }

  return response.json();
}