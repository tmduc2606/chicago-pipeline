import { useRef, useEffect, useState } from "react";
import maplibregl from "maplibre-gl";
import { useQuery } from "@tanstack/react-query";
import { api, type GeoCluster } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";
import { MAP_STYLE, CHICAGO_CENTER, MAP_DEFAULTS, MAP_TILE_TIMEOUT } from "@/config/map";

type GeoJSONFeature = {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: Record<string, unknown>;
};

function applyClusterData(map: maplibregl.Map, d: GeoCluster[] | undefined) {
  if (!d || d.length === 0) return;

  const features: GeoJSONFeature[] = d.map((item) => ({
    type: "Feature",
    geometry: { type: "Point", coordinates: [item.lng, item.lat] },
    properties: { count: item.count },
  }));

  const geojson = { type: "FeatureCollection" as const, features };

  try {
    if (map.getSource("clusters")) {
      (map.getSource("clusters") as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      map.addSource("clusters", { type: "geojson", data: geojson });
      map.addLayer({
        id: "cluster-circles",
        type: "circle",
        source: "clusters",
        paint: {
          "circle-radius": [
            "interpolate", ["linear"], ["get", "count"],
            0, 4, 200, 20,
          ],
          "circle-color": "#fb923c",
          "circle-opacity": 0.6,
          "circle-stroke-width": 1,
          "circle-stroke-color": "#f97316",
        },
      });
    }
  } catch {
    // silently ignore layer errors during rapid re-renders
  }
}

export function ClusterMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const styleLoaded = useRef(false);
  const [error, setError] = useState<string | null>(null);
  const [tilesLoaded, setTilesLoaded] = useState(false);
  const filters = useFilterStore();
  const params = filtersToParams(filters);

  const { data, isLoading } = useQuery({
    queryKey: ["geo-clusters", params.toString()],
    queryFn: ({ signal }) => api.geoClusters(params, signal),
  });

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    let fallbackTimer: ReturnType<typeof setTimeout> | undefined;
    let timeoutTimer: ReturnType<typeof setTimeout> | undefined;

    try {
      const map = new maplibregl.Map({
        container: mapContainer.current,
        style: MAP_STYLE,
        center: CHICAGO_CENTER,
        zoom: MAP_DEFAULTS.cluster.zoom,
        attributionControl: false,
      });

      map.on("error", (e) => {
        console.error("ClusterMap error:", e.error?.message);
        setError("Map error: " + (e.error?.message ?? "unknown"));
      });
      map.on("load", () => {
        if (fallbackTimer) clearTimeout(fallbackTimer);
        if (timeoutTimer) clearTimeout(timeoutTimer);
        setTilesLoaded(true);
        styleLoaded.current = true;
      });
      map.on("style.load", () => { styleLoaded.current = true; });

      // Immediate check: style may have loaded before listeners were attached
      if (map.isStyleLoaded()) {
        if (fallbackTimer) clearTimeout(fallbackTimer);
        if (timeoutTimer) clearTimeout(timeoutTimer);
        setTilesLoaded(true);
        styleLoaded.current = true;
      }

      // Fallback: if load event hasn't fired in 5s, check isStyleLoaded()
      fallbackTimer = setTimeout(() => {
        if (map.isStyleLoaded()) {
          if (timeoutTimer) clearTimeout(timeoutTimer);
          setTilesLoaded(true);
          styleLoaded.current = true;
        }
      }, 5000);

      // Hard timeout: if tiles still haven't loaded after MAP_TILE_TIMEOUT, show error
      timeoutTimer = setTimeout(() => {
        if (!tilesLoaded) {
          setError("Map tiles timed out. Check your network connection.");
        }
      }, MAP_TILE_TIMEOUT);

      mapRef.current = map;
    } catch (err) {
      setError("Failed to initialize map: " + (err instanceof Error ? err.message : "unknown"));
    }

    return () => {
      if (fallbackTimer) clearTimeout(fallbackTimer);
      if (timeoutTimer) clearTimeout(timeoutTimer);
      styleLoaded.current = false;
      mapRef.current?.remove();
      mapRef.current = null;
      setTilesLoaded(false);
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Apply data as soon as both map and data exist, regardless of tile state
    if (data) {
      map.resize();
      applyClusterData(map, data);
    }
  }, [data]);

  // Separate effect to handle map resize when tiles finish loading
  useEffect(() => {
    if (tilesLoaded && mapRef.current && data) {
      mapRef.current.resize();
    }
  }, [tilesLoaded]);

  const showLoading = isLoading || (!tilesLoaded && !error);

  return (
    <div className="card overflow-hidden p-0">
      <div className="px-5 pt-5 pb-3">
        <h3 className="text-sm font-semibold text-text">Crime Clusters</h3>
      </div>
      <div className="relative mx-5 mb-5">
        {/* Map container is always rendered so MapLibre can initialize */}
        <div ref={mapContainer} className="h-[380px] rounded-lg overflow-hidden" />
        {/* Loading / error overlay on top of the map */}
        {showLoading && (
          <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-bg-muted/80">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-orange border-t-transparent" />
              <span className="text-xs text-text-dim">Loading map tiles...</span>
            </div>
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-bg-muted/80">
            <p className="text-sm text-text-dim px-4 text-center">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
