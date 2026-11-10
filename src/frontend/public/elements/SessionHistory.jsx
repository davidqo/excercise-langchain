import { Bot, User } from "lucide-react";

export default function SessionHistory() {
  const compact = props.appearance === "Compact";
  const items = props.items || [];

  return (
    <div className={`rounded-md border bg-background ${compact ? "p-3" : "p-4"} my-2`}>
      <div className="mb-3 text-sm font-semibold">Session history</div>
      <div className="space-y-2">
        {items.map((item, index) => {
          const isUser = item.role === "user";
          const Icon = isUser ? User : Bot;
          return (
            <div key={index} className="flex gap-2 text-sm">
              <Icon className="mt-0.5 h-4 w-4 shrink-0 text-teal-700" />
              <div className="min-w-0">
                <div className="text-xs uppercase text-muted-foreground">{isUser ? "User" : "Bot"}</div>
                <div className="line-clamp-3 whitespace-pre-wrap">{item.content}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
