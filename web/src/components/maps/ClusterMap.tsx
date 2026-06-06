import { useRef, useEffect, useState } from "react";
import maplibregl from "maplibre-gl";
import { useQuery } from "@tanstack/react-query";
import { api, type GeoCluster } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";

type GeoJSONFeature = {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: Record<string, unknown>;
};

const DARK_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

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

    try {
      const map = new maplibregl.Map({
        container: mapContainer.current,
        style: DARK_STYLE,
        center: [-87.6298, 41.8781],
        zoom: 11,
        attributionControl: false,
      });

      map.on("error", () => {});
      map.on("load", () => setTilesLoaded(true));

      mapRef.current = map;
    } catch {
      setError("Failed to initialize map");
    }

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
      setTilesLoaded(false);
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !data) return;

    const applyData = () => {
      map.resize();
      applyClusterData(map, data);
    };

    if (map.isStyleLoaded()) {
      applyData();
    } else {
      map.once("style.load", applyData);
    }
  }, [data]);

  const showLoading = isLoading || (!tilesLoaded && !error);
  const showMap = !showLoading && !error;

  return (
    <div className="card overflow-hidden p-0">
      <div className="px-5 pt-5 pb-3">
        <h3 className="text-sm font-semibold text-text">Crime Clusters</h3>
      </div>
      {showLoading ? (
        <div className="mx-5 mb-5 shrink-0">
          <div className="flex h-[350px] items-center justify-center rounded-lg bg-bg-muted">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-orange border-t-transparent" />
              <span className="text-xs text-text-dim">Loading map tiles...</span>
            </div>
          </div>
        </div>
      ) : error ? (
        <div className="mx-5 mb-5 flex h-[350px] items-center justify-center rounded-lg bg-bg-muted">
          <p className="text-sm text-text-dim">{error}</p>
        </div>
      ) : showMap ? (
        <div ref={mapContainer} className="h-[380px]" />
      ) : null}
    </div>
  );
}
