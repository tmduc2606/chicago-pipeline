import { useState, useRef, useEffect } from "react";

type Props = {
  content: string;
};

export function HelpTooltip({ content }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <div ref={ref} className="relative inline-flex">
      <button
        onClick={() => setOpen(!open)}
        className="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-bg-muted text-text-dim transition-colors hover:bg-border hover:text-text"
        title="Help"
      >
        <span className="text-[10px] font-bold">?</span>
      </button>
      {open && (
        <div className="absolute bottom-full left-1/2 z-50 mb-2 w-56 -translate-x-1/2 rounded-lg border border-border bg-bg-card p-3 text-xs text-text-muted shadow-xl">
          {content}
          <div className="absolute -bottom-1 left-1/2 h-2 w-2 -translate-x-1/2 rotate-45 border-b border-r border-border bg-bg-card" />
        </div>
      )}
    </div>
  );
}
