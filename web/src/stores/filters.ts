import { create } from "zustand";

export type FilterState = {
  from: string | null;
  to: string | null;
  types: string[] | null;
  districts: number[] | null;
  communityAreas: number[] | null;
};

type FilterActions = {
  setFrom: (v: string | null) => void;
  setTo: (v: string | null) => void;
  setTypes: (v: string[] | null) => void;
  setDistricts: (v: number[] | null) => void;
  setCommunityAreas: (v: number[] | null) => void;
  reset: () => void;
};

const INITIAL: FilterState = {
  from: null,
  to: null,
  types: null,
  districts: null,
  communityAreas: null,
};

export const useFilterStore = create<FilterState & FilterActions>((set, get) => ({
  ...INITIAL,
  setFrom: (v) => {
    const { to } = get();
    if (v && to && v > to) return;
    set({ from: v });
  },
  setTo: (v) => {
    const { from } = get();
    if (from && v && v < from) return;
    set({ to: v });
  },
  setTypes: (v) => set({ types: v && v.length > 0 ? v : null }),
  setDistricts: (v) => set({ districts: v && v.length > 0 ? v : null }),
  setCommunityAreas: (v) => set({ communityAreas: v && v.length > 0 ? v : null }),
  reset: () => set(INITIAL),
}));

export function filtersToParams(state: FilterState): URLSearchParams {
  const p = new URLSearchParams();
  if (state.from) p.set("from_date", state.from);
  if (state.to) p.set("to_date", state.to);
  if (state.types && state.types.length > 0) p.set("types", state.types.join(","));
  if (state.districts && state.districts.length > 0)
    p.set("districts", state.districts.join(","));
  if (state.communityAreas && state.communityAreas.length > 0)
    p.set("community_areas", state.communityAreas.join(","));
  return p;
}
