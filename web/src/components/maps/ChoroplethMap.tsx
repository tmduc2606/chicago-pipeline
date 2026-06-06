import { useRef, useEffect, useState } from "react";
import maplibregl from "maplibre-gl";
import { useQuery } from "@tanstack/react-query";
import { api, type ChoroplethBucket } from "@/lib/api";
import { useFilterStore, filtersToParams } from "@/stores/filters";

type GeoJSONFeature = {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: Record<string, unknown>;
};

const DARK_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

function applyChoroplethData(map: maplibregl.Map, d: ChoroplethBucket[] | undefined) {
  if (!d || d.length === 0) return;

  const features: GeoJSONFeature[] = d.map((item) => ({
    type: "Feature",
    geometry: { type: "Point", coordinates: [item.lng, item.lat] },
    properties: { key: item.key, label: item.label, value: item.value },
  }));

  const geojson = { type: "FeatureCollection" as const, features };

  try {
    if (map.getSource("choropleth")) {
      (map.getSource("choropleth") as maplibregl.GeoJSONSource).setData(geojson);
    } else {
      map.addSource("choropleth", { type: "geojson", data: geojson });
      map.addLayer({
        id: "choropleth-circle",
        type: "circle",
        source: "choropleth",
        paint: {
          "circle-radius": [
            "interpolate", ["linear"], ["get", "value"],
            0, 5, 3000, 25,
          ],
          "circle-color": "#818cf8",
          "circle-opacity": 0.7,
          "circle-stroke-width": 1,
          "circle-stroke-color": "#6366f1",
        },
      });

      const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        className: "dark-popup",
      });
      map.on("mouseenter", "choropleth-circle", (e) => {
        map.getCanvas().style.cursor = "pointer";
        const feature = e.features?.[0];
        if (feature) {
          const p = feature.properties as { label: string; value: number };
          popup
            .setHTML(`<div style="color:#e8e8f0;background:#1a1a26;padding:6px 10px;border-radius:6px;font-size:12px;border:1px solid #2a2a3d"><strong>${p.label}</strong><br/>Crimes: ${p.value.toLocaleString()}</div>`)
            .setLngLat(e.lngLat)
            .addTo(map);
        }
      });
      map.on("mouseleave", "choropleth-circle", () => {
        map.getCanvas().style.cursor = "";
        popup.remove();
      });
    }
  } catch {
    // silently ignore layer errors during rapid re-renders
  }
}

export function ChoroplethMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tilesLoaded, setTilesLoaded] = useState(false);
  const filters = useFilterStore();
  const params = filtersToParams(filters);
  params.set("level", "district");
  params.set("metric", "count");

  const { data, isLoading } = useQuery({
    queryKey: ["choropleth", params.toString()],
    queryFn: ({ signal }) => api.choropleth(params, signal),
  });

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    try {
      const map = new maplibregl.Map({
        container: mapContainer.current,
        style: DARK_STYLE,
        center: [-87.6298, 41.8781],
        zoom: 10,
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
      applyChoroplethData(map, data);
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
        <h3 className="text-sm font-semibold text-text">Choropleth by District</h3>
      </div>
      {showLoading ? (
        <div className="mx-5 mb-5 shrink-0">
          <div className="flex h-[350px] items-center justify-center rounded-lg bg-bg-muted">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
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
