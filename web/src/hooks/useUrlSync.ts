import { useEffect, useRef } from "react";
import { useFilterStore } from "@/stores/filters";

export function useUrlSync() {
  const hydrated = useRef(false);

  useEffect(() => {
    if (hydrated.current) return;
    hydrated.current = true;

    const params = new URLSearchParams(window.location.search);
    const from = params.get("from_date");
    const to = params.get("to_date");
    const typesRaw = params.get("types");
    const areasRaw = params.get("community_areas");
    const districtsRaw = params.get("districts");

    const store = useFilterStore.getState();
    if (from) store.setFrom(from);
    if (to) store.setTo(to);
    if (typesRaw) store.setTypes(typesRaw.split(","));
    if (areasRaw) store.setCommunityAreas(areasRaw.split(",").map(Number));
    if (districtsRaw) store.setDistricts(districtsRaw.split(",").map(Number));
  }, []);

  useEffect(() => {
    const unsub = useFilterStore.subscribe((state) => {
      const params = new URLSearchParams();
      if (state.from) params.set("from_date", state.from);
      if (state.to) params.set("to_date", state.to);
      if (state.types && state.types.length > 0) params.set("types", state.types.join(","));
      if (state.districts && state.districts.length > 0) params.set("districts", state.districts.join(","));
      if (state.communityAreas && state.communityAreas.length > 0)
        params.set("community_areas", state.communityAreas.join(","));

      const qs = params.toString();
      const newUrl = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
      window.history.replaceState(null, "", newUrl);
    });
    return unsub;
  }, []);
}
