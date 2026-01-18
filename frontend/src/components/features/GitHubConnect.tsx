import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Github, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface GitHubResponse {
    github_data_id: number;
    profile: {
        username: string;
        public_repos: number;
        followers: number;
    };
    cached: boolean;
}

interface GitHubConnectProps {
    onConnected: (id: number) => void;
}

export default function GitHubConnect({ onConnected }: GitHubConnectProps) {
    const [username, setUsername] = useState("");
    const [error, setError] = useState<string | null>(null);

    const fetchMutation = useMutation({
        mutationFn: async (user: string) => {
            const response = await api.post<GitHubResponse>('/github/fetch', { username: user });
            return response.data;
        },
        onSuccess: (data) => {
            onConnected(data.github_data_id);
            setError(null);
        },
        onError: (err: any) => {
            setError(err.response?.data?.error?.message || "Failed to fetch GitHub data.");
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (username.trim()) {
            fetchMutation.mutate(username.trim());
        }
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Github className="w-5 h-5" />
                    Connect GitHub
                </CardTitle>
                <CardDescription>
                    Fetch your projects and repositories to enrich your resume.
                </CardDescription>
            </CardHeader>

            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="username">GitHub Username</Label>
                        <div className="flex gap-2">
                            <Input
                                id="username"
                                placeholder="e.g. amine-elq"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                disabled={fetchMutation.isPending || fetchMutation.isSuccess}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="flex items-center p-3 text-sm text-destructive rounded-md bg-destructive/10">
                            <AlertCircle className="w-4 h-4 mr-2" />
                            {error}
                        </div>
                    )}

                    {fetchMutation.isSuccess && (
                        <div className="flex items-center p-3 text-sm text-green-600 rounded-md bg-green-50">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Successfully connected as {fetchMutation.data.profile.username}
                        </div>
                    )}
                </CardContent>

                <CardFooter>
                    <Button
                        type="submit"
                        className="w-full"
                        disabled={!username.trim() || fetchMutation.isPending || fetchMutation.isSuccess}
                    >
                        {fetchMutation.isPending ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Fetching...
                            </>
                        ) : fetchMutation.isSuccess ? (
                            "Connected"
                        ) : (
                            "Connect Account"
                        )}
                    </Button>
                </CardFooter>
            </form>
        </Card>
    );
}
