import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useSidebar } from "@/stores/ui";
import { cn } from "@/lib/utils";

type Props = {
  children: ReactNode;
};

export function AppShell({ children }: Props) {
  const collapsed = useSidebar((s) => s.collapsed);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      <MobileOverlay />
      <Sidebar />
      <div
        className={cn(
          "flex flex-1 flex-col transition-all duration-200",
          collapsed ? "md:ml-16" : "md:ml-64",
        )}
      >
        <Header />
        <main className="flex-1 overflow-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}

function MobileOverlay() {
  const collapsed = useSidebar((s) => s.collapsed);
  const toggle = useSidebar((s) => s.toggle);

  if (collapsed) return null;

  return (
    <div
      className="fixed inset-0 z-30 bg-black/50 md:hidden"
      onClick={toggle}
      onKeyDown={(e) => e.key === "Escape" && toggle()}
      role="button"
      tabIndex={0}
      aria-label="Close sidebar"
    />
  );
}
