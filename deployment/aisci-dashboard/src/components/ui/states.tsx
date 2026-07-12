import { AlertCircle, Loader2, SearchX, XCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "./alert";
import { cn } from "@/lib/utils";

export function LoadingState({
  message = "Loading...",
  className,
}: {
  message?: string;
  className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-8 text-center", className)}>
      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      <p className="mt-4 text-sm text-muted-foreground">{message}</p>
    </div>
  );
}

export function EmptyState({
  title = "No Data",
  description = "There is nothing to display here.",
  icon: Icon = SearchX,
  className,
}: {
  title?: string;
  description?: string;
  icon?: any;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-dashed p-10 text-center",
        className,
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
        <Icon className="h-6 w-6 text-muted-foreground" />
      </div>
      <h3 className="mt-4 text-sm font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

export function ErrorState({ error, className }: { error?: unknown; className?: string }) {
  const message = error instanceof Error ? error.message : "An unexpected error occurred.";
  return (
    <Alert variant="destructive" className={className}>
      <XCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}

export function UnavailableState({
  title = "Unavailable",
  description = "This feature is not available for the current project.",
  className,
}: {
  title?: string;
  description?: string;
  className?: string;
}) {
  return (
    <Alert className={cn("bg-muted/50 text-muted-foreground", className)}>
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  );
}
