import { createFileRoute } from "@tanstack/react-router";
import { PageShell } from "@/components/PageShell";
import { CanvasEditor } from "@/components/canvas/CanvasEditor";

export const Route = createFileRoute("/papers_/$paperId/canvas")({
  head: ({ params }) => ({
    meta: [
      { title: `Canvas: Paper ${params.paperId} — AiSci Studio` },
    ],
  }),
  component: PaperCanvasStudio,
});

function PaperCanvasStudio() {
  const { paperId } = Route.useParams();
  return (
    <PageShell>
      <div className="mb-4">
        <h2 className="text-2xl font-bold tracking-tight">Canvas Studio</h2>
        <p className="text-muted-foreground text-sm">
          Visually connect claims, pipelines, and results.
        </p>
      </div>
      
      <CanvasEditor paperId={paperId} />
    </PageShell>
  );
}
