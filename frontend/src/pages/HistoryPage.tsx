import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Loader2, Calendar } from 'lucide-react';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

interface ResumeSummary {
    id: number;
    name: string;
    summary: string | null;
    created_at: string;
}

interface ResumeListResponse {
    items: ResumeSummary[];
}

export default function HistoryPage() {
    const navigate = useNavigate();

    const { data, isLoading, error } = useQuery({
        queryKey: ['resumes'],
        queryFn: async () => {
            const response = await api.get<ResumeListResponse>('/resume/');
            return response.data;
        }
    });

    if (isLoading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    if (error) return <div className="text-center text-red-500 py-10">Failed to load history.</div>;

    return (
        <div className="max-w-5xl mx-auto space-y-6 py-6">
            <h1 className="text-3xl font-bold">Resume History</h1>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {data?.items.map((resume) => (
                    <Card
                        key={resume.id}
                        className="cursor-pointer hover:bg-secondary/50 transition-colors border-2 hover:border-primary/20"
                        onClick={() => navigate(`/results/${resume.id}`)}
                    >
                        <CardHeader className="pb-3">
                            <CardTitle className="flex items-center justify-between text-lg truncate">
                                {resume.name}
                            </CardTitle>
                            <CardDescription className="flex items-center gap-1 text-xs">
                                <Calendar className="h-3 w-3" />
                                {new Date(resume.created_at).toLocaleDateString()} {new Date(resume.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground line-clamp-3">
                                {resume.summary || "No summary available."}
                            </p>
                        </CardContent>
                    </Card>
                ))}
                {data?.items.length === 0 && (
                    <p className="col-span-full text-center text-muted-foreground py-10">No resumes found. Create one first!</p>
                )}
            </div>
        </div>
    );
}
