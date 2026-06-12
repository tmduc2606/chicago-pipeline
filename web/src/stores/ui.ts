import { create } from "zustand";

type SidebarState = {
  collapsed: boolean;
  toggle: () => void;
};

const isMobile = () => typeof window !== "undefined" && window.innerWidth < 768;

export const useSidebar = create<SidebarState>((set) => ({
  collapsed: isMobile(),
  toggle: () => set((s) => ({ collapsed: !s.collapsed })),
}));
