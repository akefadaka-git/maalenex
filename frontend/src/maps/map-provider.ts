/**
 * Provider-neutral map contracts.
 *
 * The current product intentionally uses a local schematic renderer. A live
 * provider must implement this contract only after its licence, attribution,
 * caching, privacy, coverage and offline terms have been reviewed.
 */
export type MapCoordinate = Readonly<{ latitude: number; longitude: number }>;
export type MapBounds = Readonly<{ south: number; west: number; north: number; east: number }>;

export interface MapAttribution {
  /** Human-readable attribution that remains visible on the map. */
  label: string;
  /** Licence or provider information URL. */
  url: string;
}

export interface MapProviderCapabilities {
  online: boolean;
  offline: boolean;
  routing: boolean;
  geocoding: boolean;
}

export interface MapProviderMetadata {
  id: string;
  displayName: string;
  attribution: MapAttribution[];
  capabilities: MapProviderCapabilities;
  /** Provider terms and data licence reference for audit documentation. */
  termsUrl: string;
}

export interface MapRouteRequest {
  origin: MapCoordinate;
  destination: MapCoordinate;
  /** Routing profile is explicit; never silently assume motorcycle support. */
  profile: "driving" | "motorcycle" | "walking";
}

export interface MapRouteResult {
  geometry: ReadonlyArray<MapCoordinate>;
  distanceMeters: number;
  durationSeconds?: number;
  source: string;
  retrievedAt: string;
}

export interface MapProviderAdapter {
  readonly metadata: MapProviderMetadata;
  /** Returns a routable path only when the provider supports the requested profile. */
  getRoute?(request: MapRouteRequest, signal?: AbortSignal): Promise<MapRouteResult>;
  /** Releases provider resources such as map instances, workers and listeners. */
  dispose?(): void;
}

/**
 * Safe default until a provider and local map-data package are explicitly
 * approved. This is not a live map provider and must not be used for navigation.
 */
export const MAP_PROVIDER_MODE = "schematic" as const;
