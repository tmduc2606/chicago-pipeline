import type { StyleSpecification } from "maplibre-gl";

export const CHICAGO_CENTER: [number, number] = [-87.6298, 41.8781];

export const MAP_DEFAULTS = {
  cluster: { zoom: 11 },
  choropleth: { zoom: 10 },
} as const;

/** Max ms to wait for map tiles before showing an error */
export const MAP_TILE_TIMEOUT = 10000;

/**
 * Inline dark map style — uses OpenStreetMap tiles with dark filter.
 * Compatible with MapLibre GL v5.x bundled by Vite.
 */
export const MAP_STYLE: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap",
    },
  },
  layers: [
    {
      id: "osm-tiles",
      type: "raster",
      source: "osm",
      paint: {
        "raster-brightness-min": 0.3,
        "raster-brightness-max": 0.7,
        "raster-saturation": -0.3,
      },
    },
  ],
};
