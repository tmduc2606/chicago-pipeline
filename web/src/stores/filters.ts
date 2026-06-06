import { create } from "zustand";

export type FilterState = {
  from: string | null;
  to: string | null;
  types: string[] | null;
  communityAreas: number[] | null;
};

type FilterActions = {
  setFrom: (v: string | null) => void;
  setTo: (v: string | null) => void;
  setTypes: (v: string[] | null) => void;
  setCommunityAreas: (v: number[] | null) => void;
  reset: () => void;
};

const INITIAL: FilterState = {
  from: null,
  to: null,
  types: null,
  communityAreas: null,
};

export const useFilterStore = create<FilterState & FilterActions>((set) => ({
  ...INITIAL,
  setFrom: (v) => set({ from: v }),
  setTo: (v) => set({ to: v }),
  setTypes: (v) => set({ types: v }),
  setCommunityAreas: (v) => set({ communityAreas: v }),
  reset: () => set(INITIAL),
}));

export function filtersToParams(state: FilterState): URLSearchParams {
  const p = new URLSearchParams();
  if (state.from) p.set("from_date", state.from);
  if (state.to) p.set("to_date", state.to);
  if (state.types && state.types.length > 0) p.set("types", state.types.join(","));
  if (state.communityAreas && state.communityAreas.length > 0)
    p.set("community_areas", state.communityAreas.join(","));
  return p;
}
