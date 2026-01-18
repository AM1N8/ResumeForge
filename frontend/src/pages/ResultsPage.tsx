import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { cn } from '@/lib/utils';
import {
    FileJson,
    FileCode,
    FileType,
    Loader2,
    ChevronLeft,
    CheckCircle2,
    Printer,
    AlertCircle,
    Bookmark,
    BookmarkCheck
} from 'lucide-react';

import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import ResumePreview from '@/components/features/ResumePreview';
import DecisionLog from '@/components/features/DecisionLog';
import ResumeAnalytics from '@/components/features/ResumeAnalytics';

interface StructuredResume {
    id: number;
    resume: any; // CanonicalResume
    decision_log: any[];
    sources: {
        resume: boolean;
        github: boolean;
    };
    created_at: string;
    updated_at: string;
}

export default function ResultsPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [isExporting, setIsExporting] = useState(false);
    const [isSaved, setIsSaved] = useState(false);

    const { data, isLoading, error } = useQuery({
        queryKey: ['resume', id],
        queryFn: async () => {
            const response = await api.get<StructuredResume>(`/resume/${id}`);
            return response.data;
        },
        // We don't need polling here because GET /resume/:id only returns if it exists (is ready)
        retry: 3,
        retryDelay: 1000,
    });

    const handleExport = async (format: 'json' | 'markdown' | 'latex') => {
        setIsExporting(true);
        try {
            const response = await api.get(`/resume/${id}/export?format=${format}`, {
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const extension = format === 'json' ? 'json' : format === 'markdown' ? 'md' : 'tex';
            link.setAttribute('download', `resume_${id}.${extension}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Export failed:', err);
        } finally {
            setIsExporting(false);
        }
    };

    const handlePrint = () => {
        window.print();
    };

    const handleSave = () => {
        setIsSaved(true);
        // In a real app, this is already saved in DB. We just simulate the interaction.
        // User requested: "save button where i can save the page in a header section page called history"
        if (confirm("Resume saved to History! View history now?")) {
            navigate('/history');
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
                <p className="text-muted-foreground animate-pulse text-lg">Loading your structured resume...</p>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="max-w-xl mx-auto py-12 text-center space-y-6">
                <div className="bg-destructive/10 p-4 rounded-full w-fit mx-auto">
                    <AlertCircle className="w-12 h-12 text-destructive" />
                </div>
                <h2 className="text-2xl font-bold">Resume not found</h2>
                <p className="text-muted-foreground">We couldn't retrieve your structured resume. It might still be processing or the ID is invalid.</p>
                <Link to="/upload">
                    <Button variant="outline">Back to Upload</Button>
                </Link>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto pb-12 space-y-8">
            {/* Action Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 sticky top-14 bg-background/95 backdrop-blur z-40 py-4 border-b">
                <div className="flex items-center gap-4">
                    <Link to="/upload">
                        <Button variant="ghost" size="sm" className="gap-2">
                            <ChevronLeft className="w-4 h-4" /> Back
                        </Button>
                    </Link>
                    <div className="flex items-center gap-2">
                        <h1 className="text-xl font-bold">Structured Resume</h1>
                        <Badge variant="default" className="gap-1 bg-green-500 hover:bg-green-600">
                            <CheckCircle2 className="w-3 h-3" /> Ready
                        </Badge>
                    </div>
                </div>

                <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0">
                    <Button variant="outline" size="sm" onClick={() => handleExport('json')} disabled={isExporting} className="gap-2">
                        <FileJson className="w-4 h-4" /> JSON
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleExport('markdown')} disabled={isExporting} className="gap-2">
                        <FileCode className="w-4 h-4" /> MD
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleExport('latex')} disabled={isExporting} className="gap-2">
                        <FileType className="w-4 h-4" /> LaTeX
                    </Button>
                    <Button variant="default" size="sm" onClick={handlePrint} className="gap-2 shadow-sm">
                        <Printer className="w-4 h-4" /> Print PDF
                    </Button>
                    <Separator orientation="vertical" className="h-8 mx-1 hidden md:block" />
                    <Button
                        variant="ghost"
                        size="sm"
                        className={cn("gap-2", isSaved && "text-primary font-medium")}
                        onClick={handleSave}
                    >
                        {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                        {isSaved ? "Saved" : "Save"}
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left Column: Preview */}
                <div className="lg:col-span-8 space-y-6 print:lg:col-span-12 print:max-w-none">
                    <div id="resume-print-area">
                        <ResumePreview data={data.resume} />
                    </div>
                </div>

                {/* Right Column: Decisions & Info */}
                <div className="lg:col-span-4 space-y-6 print:hidden">
                    <DecisionLog entries={data.decision_log || []} />

                    <Card className="bg-primary/5 border-primary/10">
                        <CardContent className="pt-6">
                            <h4 className="font-bold text-sm mb-2 flex items-center gap-2">
                                <CheckCircle2 className="w-4 h-4 text-primary" />
                                Structuring Summary
                            </h4>
                            <div className="text-xs space-y-2 text-muted-foreground">
                                <p>• Source: <span className="text-foreground font-medium">{data.sources.resume ? 'Resume' : ''} {data.sources.github ? '+ GitHub' : ''}</span></p>
                                <p>• Date normalization: <span className="text-foreground font-medium">Automatic</span></p>
                                <p>• Version: <span className="text-foreground font-medium">Canonical v1.0</span></p>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* Analytics Section */}
            <div className="print:hidden pt-8 border-t">
                <ResumeAnalytics data={data.resume} />
            </div>
        </div>
    );
}
