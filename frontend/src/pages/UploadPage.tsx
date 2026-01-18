import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Loader2, ArrowRight, Sparkles } from 'lucide-react';

import api from '@/services/api';
import ResumeUpload from '@/components/features/ResumeUpload';
import GitHubConnect from '@/components/features/GitHubConnect';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useSettings } from '@/hooks/use-settings';

interface StructureResponse {
    structured_resume_id: number;
    status: string;
}

export default function UploadPage() {
    const navigate = useNavigate();
    const [resumeUploadId, setResumeUploadId] = useState<number | null>(null);
    const [githubDataId, setGithubDataId] = useState<number | null>(null);
    const [customInstructions, setCustomInstructions] = useState<string>('');
    const [error, setError] = useState<string | null>(null);
    const settings = useSettings();

    const structureMutation = useMutation({
        mutationFn: async () => {
            const response = await api.post<StructureResponse>('/resume/structure', {
                resume_upload_id: resumeUploadId,
                github_data_id: githubDataId,
                custom_instructions: customInstructions.trim() || null,
                settings: {
                    project_count: settings.projectCount,
                    resume_language: settings.resumeLanguage,
                    verbosity: settings.verbosity,
                    primary_color: settings.primaryColor,
                }
            });
            return response.data;
        },
        onSuccess: (data) => {
            navigate(`/results/${data.structured_resume_id}`);
        },
        onError: (err: any) => {
            setError(err.response?.data?.error?.message || "Failed to start structuring process.");
        },
    });

    const canProceed = resumeUploadId !== null || githubDataId !== null;

    return (
        <div className="max-w-4xl mx-auto space-y-8 py-8">
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-bold">Upload & Connect</h1>
                <p className="text-muted-foreground">
                    Provide your resume and connect GitHub to get the best results.
                </p>
            </div>

            <div className="grid gap-8 md:grid-cols-2">
                <div className="space-y-4">
                    <div className="flex items-center gap-2 font-semibold">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm">1</span>
                        Upload Resume
                    </div>
                    <ResumeUpload
                        onUploadSuccess={(id) => setResumeUploadId(id)}
                    />
                    {resumeUploadId && (
                        <p className="text-sm text-green-600 font-medium text-center">
                            Resume uploaded successfully!
                        </p>
                    )}
                </div>

                <div className="space-y-4">
                    <div className="flex items-center gap-2 font-semibold">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm">2</span>
                        Connect GitHub (Optional)
                    </div>
                    <GitHubConnect
                        onConnected={(id) => setGithubDataId(id)}
                    />
                    {githubDataId && (
                        <p className="text-sm text-green-600 font-medium text-center">
                            GitHub connected successfully!
                        </p>
                    )}
                </div>
            </div>

            {/* Custom Instructions Section */}
            <Card className="border-dashed border-2 border-primary/20 bg-primary/5">
                <CardHeader className="pb-3">
                    <div className="flex items-center gap-2">
                        <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm">3</span>
                        <CardTitle className="text-lg font-semibold">Custom Instructions (Optional)</CardTitle>
                    </div>
                    <CardDescription className="ml-8">
                        Provide specific instructions to customize how the AI structures your resume.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Textarea
                        placeholder="e.g., Focus on AI/ML projects, emphasize Python experience, highlight leadership roles, tailor for software engineering internships..."
                        value={customInstructions}
                        onChange={(e) => setCustomInstructions(e.target.value)}
                        maxLength={2000}
                        className="min-h-[100px] bg-background"
                    />
                    <div className="flex justify-between mt-2">
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            The AI will follow your instructions while structuring the resume
                        </p>
                        <p className="text-xs text-muted-foreground">
                            {customInstructions.length}/2000
                        </p>
                    </div>
                </CardContent>
            </Card>

            <div className="flex flex-col items-center space-y-4 pt-4">
                <Button
                    size="lg"
                    className="w-full md:w-1/3 text-lg"
                    disabled={!canProceed || structureMutation.isPending}
                    onClick={() => structureMutation.mutate()}
                >
                    {structureMutation.isPending ? (
                        <>
                            <Loader2 className="w-5 h-5 mr-2 animate-spin" /> Processing...
                        </>
                    ) : (
                        <>
                            Generate Resume <ArrowRight className="w-5 h-5 ml-2" />
                        </>
                    )}
                </Button>
                {error && (
                    <p className="text-sm text-destructive">{error}</p>
                )}
                <p className="text-xs text-muted-foreground">
                    At least one source (Resume or GitHub) is required.
                </p>
            </div>
        </div>
    );
}
