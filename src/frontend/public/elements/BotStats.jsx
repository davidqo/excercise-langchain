import { Activity, Database, MessageSquare, Timer } from "lucide-react";

export default function BotStats() {
  const roomy = props.appearance === "Spacious";
  const compact = props.appearance === "Compact";
  const items = [
    {
      label: "Latency",
      value: `${props.elapsedMs} ms`,
      icon: Timer,
    },
    {
      label: "RAG context",
      value: props.hasContext ? "available" : "unavailable",
      icon: Database,
    },
    {
      label: "Sources",
      value: props.sourceCount,
      icon: Activity,
    },
    {
      label: "Messages",
      value: props.messageCount,
      icon: MessageSquare,
    },
  ];

  return (
    <div className={`grid gap-2 ${compact ? "grid-cols-2" : "grid-cols-2 md:grid-cols-4"} ${roomy ? "my-4" : "my-2"}`}>
      {items.map((item) => {
        const Icon = item.icon;
        return (
          <div key={item.label} className={`border bg-background ${roomy ? "p-4" : "p-3"} rounded-md`}>
            <div className="flex items-center gap-2 text-muted-foreground text-xs">
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </div>
            <div className="mt-1 text-sm font-semibold">{item.value}</div>
          </div>
        );
      })}
    </div>
  );
}
