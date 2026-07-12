import { Lightbulb, Calendar, Send, FileText, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { fetchIdeas } from "@/lib/api";
import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export function IdeasPanel({ projectId }: { projectId: string }) {
  const { data: ideas, isLoading } = useQuery({
    queryKey: ["ideas", projectId],
    queryFn: () => fetchIdeas(projectId),
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center bg-secondary/10 rounded-xl border border-border">
        <p className="text-sm text-muted-foreground animate-pulse">Brainstorming with LLM... [Mock - Not Connected to Engine]</p>
      </div>
    );
  }

  if (!ideas || ideas.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center bg-secondary/20 rounded-xl border border-border">
        <Lightbulb className="w-8 h-8 text-muted-foreground mb-3 opacity-50" />
        <p className="text-muted-foreground">No ideas generated yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {ideas.map((idea: any) => (
        <div key={idea.id} className="relative p-5 rounded-xl border border-border bg-card shadow-sm hover:shadow-md transition-shadow group">
          <div className="absolute top-0 right-0 w-1 h-full bg-primary/20 rounded-r-xl" />

          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="bg-primary/10 p-1.5 rounded-md">
                <Lightbulb className="w-4 h-4 text-primary" />
              </div>
              <h3 className="font-semibold text-sm">Hypothesis #{idea.id}</h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded uppercase border bg-amber-500/10 text-amber-500 border-amber-500/20 ml-2">[Mock - Not Connected to Engine]</span>
            </div>
            <span className={cn(
              "text-[10px] font-mono px-2 py-0.5 rounded-full uppercase border",
              idea.status === 'proposed'
                ? "bg-amber-brand/10 text-amber-brand border-amber-brand/20"
                : "bg-secondary text-muted-foreground border-border"
            )}>
              {idea.status}
            </span>
          </div>

          <p className="text-sm text-foreground/90 leading-relaxed mb-4">
            {idea.hypothesis}
          </p>

          <div className="flex items-center justify-between text-xs text-muted-foreground mt-4 pt-3 border-t border-border/50">
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              {new Date(idea.timestamp).toLocaleDateString()}
            </div>

            <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <Link to="/projects/$projectId/evidence" params={{ projectId }} search={{ q: idea.hypothesis.slice(0,20) }}>
                <Button variant="outline" size="sm" className="h-7 text-[10px] px-2 gap-1.5">
                  <FileText className="w-3 h-3" /> Open related evidence
                </Button>
              </Link>
              <Link to="/projects/$projectId/tasks" params={{ projectId }}>
                <Button variant="default" size="sm" className="h-7 text-[10px] px-2 gap-1.5">
                  <Send className="w-3 h-3" /> Send to tasks
                </Button>
              </Link>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
