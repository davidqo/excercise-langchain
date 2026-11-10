import { ChevronDown, FileText } from "lucide-react";

export default function RagSources() {
  const spacious = props.appearance === "Spacious";
  const sources = props.sources || [];

  return (
    <div className={`space-y-2 ${spacious ? "my-4" : "my-2"}`}>
      {sources.map((source, index) => (
        <details key={`${source.title}-${index}`} className="rounded-md border bg-background p-3" open={index === 0}>
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3">
            <span className="flex min-w-0 items-center gap-2 text-sm font-medium">
              <FileText className="h-4 w-4 shrink-0 text-teal-700" />
              <span className="truncate">{source.title}</span>
            </span>
            <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
          </summary>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">Matched by RAG. Document text is hidden in the UI.</p>
          {source.metadata && Object.keys(source.metadata).length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {Object.entries(source.metadata).map(([key, value]) => (
                <span key={key} className="rounded border px-2 py-1 text-xs text-muted-foreground">
                  {key}: {String(value)}
                </span>
              ))}
            </div>
          ) : null}
        </details>
      ))}
    </div>
  );
}
