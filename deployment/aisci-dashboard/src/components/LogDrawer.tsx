import { useEffect, useRef, useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Loader2, CheckCircle2 } from "lucide-react";

export function LogDrawer({
  target,
  onClose,
}: {
  target: "ingest" | "fits" | null;
  onClose: () => void;
}) {
  const [lines, setLines] = useState<string[]>([]);
  const [done, setDone] = useState(false);
  const scrollRef = useRef<HTMLPreElement>(null);

  useEffect(() => {
    if (!target) return;
    setLines([]);
    setDone(false);

    const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8001/api";
    // Using current location href to extract project ID (hack for non-router context if any, but since it's mounted inside AppHeader, we'll need to pass projectId).
    // Actually, AppHeader has projectId, so let's parse from URL for now or better, update LogDrawer props to accept projectId
    const pathParts = window.location.pathname.split('/');
    const projectId = pathParts[1] === "projects" ? pathParts[2] : "robert-boson-manuscript";
    
    // map target to pipeline_id
    const pipelineId = target === "ingest" ? "ingest-validation" : "fit-validation";
    const eventSource = new EventSource(`${API_BASE}/projects/${projectId}/logs/${pipelineId}`);

    eventSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.error) {
          setLines((prev) => [...prev, `[ERROR] ${data.error}`]);
          setDone(true);
          eventSource.close();
        } else if (data.lines) {
          setLines((prev) => [...prev, ...data.lines]);
        } else if (data.line) {
          setLines((prev) => [...prev, data.line]);
        } else if (data.done) {
          setDone(true);
          eventSource.close();
        }
      } catch (err) {
        console.error("Failed to parse SSE data", err);
      }
    };

    eventSource.onerror = () => {
      setDone(true);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [target]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [lines]);

  const getLineColor = (line: string) => {
    const l = line.toLowerCase();
    if (l.includes("error") || l.includes("fail") || l.includes("traceback"))
      return "text-rose-600 dark:text-rose-400";
    if (l.includes("success") || l.includes("done") || l.includes("complete"))
      return "text-emerald-600 dark:text-emerald-400";
    return "text-zinc-600 dark:text-zinc-400";
  };

  return (
    <Sheet open={!!target} onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="w-full overflow-hidden sm:max-w-xl flex flex-col h-full border-l border-border">
        <SheetHeader className="mb-4 shrink-0">
          <SheetTitle className="flex items-center gap-2">
            {target === "ingest" ? "Ingest Pipeline" : "Physics Fits"} Logs
            {!done ? (
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-emerald-brand" />
            )}
          </SheetTitle>
          <SheetDescription>Live stream from {target}.log</SheetDescription>
        </SheetHeader>

        <pre
          ref={scrollRef}
          className="flex-1 overflow-y-auto rounded-md border border-border bg-zinc-100 dark:bg-black/95 p-4 text-xs font-mono"
        >
          {lines.map((line, i) => (
            <div key={i} className={`whitespace-pre-wrap break-all ${getLineColor(line)}`}>
              {line}
            </div>
          ))}
          {lines.length === 0 && !done && (
            <div className="text-zinc-500 animate-pulse">Waiting for logs...</div>
          )}
        </pre>
      </SheetContent>
    </Sheet>
  );
}
