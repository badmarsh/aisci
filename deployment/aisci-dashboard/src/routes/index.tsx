import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FolderTree, ArrowRight, ShieldCheck, Beaker } from "lucide-react";
import { PageShell } from "@/components/PageShell";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Portfolio — AiSci" },
      { name: "description", content: "AiSci Research Project Portfolio" },
    ],
  }),
  component: PortfolioOverview,
});

function PortfolioOverview() {
  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });

  return (
    <PageShell>
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">Research Portfolio</h2>
        <p className="text-muted-foreground mt-1">
          Select a project to enter its control plane.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="h-24 bg-muted/20" />
              <CardContent className="h-16" />
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project: any) => (
            <Link 
              key={project.id} 
              to={`/projects/${project.id}`} 
              className="group block"
            >
              <Card className="h-full glass-card transition hover:border-primary/50 hover:shadow-md cursor-pointer">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      <FolderTree className="h-5 w-5 text-primary" />
                      <CardTitle className="text-lg">{project.title}</CardTitle>
                    </div>
                    <Badge variant="outline" className="font-mono text-[10px]">
                      {project.id}
                    </Badge>
                  </div>
                  <CardDescription className="flex items-center gap-2 mt-2">
                    <Beaker className="h-3.5 w-3.5" />
                    <span>{project.research_type}</span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2 mb-4">
                    <Badge variant="secondary" className="bg-amber-brand/10 text-amber-brand">
                      <ShieldCheck className="mr-1 h-3 w-3" />
                      {project.sensitivity}
                    </Badge>
                    {project.capabilities.map((cap: string) => (
                      <Badge key={cap} variant="secondary" className="bg-muted text-muted-foreground">
                        {cap}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center text-sm font-medium text-primary group-hover:underline">
                    Enter Control Plane
                    <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </PageShell>
  );
}
