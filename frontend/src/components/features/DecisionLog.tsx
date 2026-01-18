import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MessageSquare, CheckCircle, XCircle, RefreshCw, Layers } from "lucide-react";

interface DecisionEntry {
    section: string;
    action: "included" | "excluded" | "merged" | "normalized";
    items: string[];
    reason: string;
    source: "resume" | "github" | "both";
    confidence: "high" | "medium" | "low";
}

interface DecisionLogProps {
    entries: DecisionEntry[];
}

const ActionIcon = ({ action }: { action: DecisionEntry["action"] }) => {
    switch (action) {
        case "included": return <CheckCircle className="w-4 h-4 text-green-500" />;
        case "excluded": return <XCircle className="w-4 h-4 text-rose-500" />;
        case "merged": return <Layers className="w-4 h-4 text-blue-500" />;
        case "normalized": return <RefreshCw className="w-4 h-4 text-purple-500" />;
        default: return <MessageSquare className="w-4 h-4 text-slate-500" />;
    }
};

const formatSection = (section: string) => section.charAt(0).toUpperCase() + section.slice(1);

export default function DecisionLog({ entries }: DecisionLogProps) {
    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-primary" />
                    AI Decision Log
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {entries.length === 0 ? (
                    <p className="text-sm text-muted-foreground italic">No decision logs recorded for this process.</p>
                ) : (
                    entries.map((entry, idx) => (
                        <div key={idx} className="flex gap-4 p-3 rounded-lg border bg-slate-50/50 hover:bg-slate-50 transition-colors">
                            <div className="mt-1 flex-shrink-0">
                                <ActionIcon action={entry.action} />
                            </div>
                            <div className="space-y-1 flex-grow">
                                <div className="flex items-center justify-between gap-2">
                                    <span className="text-xs font-bold text-muted-foreground">
                                        {formatSection(entry.section)} • {entry.action.toUpperCase()}
                                    </span>
                                    <Badge
                                        variant="outline"
                                        className={`text-[10px] px-1.5 h-4 font-mono ${entry.confidence === 'high' ? 'bg-green-50 text-green-700 border-green-200' :
                                                entry.confidence === 'medium' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                                    'bg-slate-50 text-slate-700 border-slate-200'
                                            }`}
                                    >
                                        {entry.confidence} conf.
                                    </Badge>
                                </div>
                                <p className="text-sm font-semibold">{entry.reason}</p>
                                {entry.items?.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-1">
                                        {entry.items.slice(0, 5).map((item, iIdx) => (
                                            <Badge key={iIdx} variant="secondary" className="text-[10px] py-0 px-1 bg-white border-slate-200 font-normal">
                                                {item}
                                            </Badge>
                                        ))}
                                        {entry.items.length > 5 && (
                                            <span className="text-[10px] text-muted-foreground pl-1">+{entry.items.length - 5} more</span>
                                        )}
                                    </div>
                                )}
                                <div className="text-[10px] text-muted-foreground pt-1 flex items-center gap-1">
                                    Source: <span className="capitalize">{entry.source}</span>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </CardContent>
        </Card>
    );
}
