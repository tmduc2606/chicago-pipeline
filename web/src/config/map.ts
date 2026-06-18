export const MAP_STYLE = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

export const CHICAGO_CENTER: [number, number] = [-87.6298, 41.8781];

export const MAP_DEFAULTS = {
  cluster: { zoom: 11 },
  choropleth: { zoom: 10 },
} as const;

/** Max ms to wait for map tiles before showing an error */
export const MAP_TILE_TIMEOUT = 10000;
