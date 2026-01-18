import { useState, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Upload, X, FileText, AlertCircle, Loader2 } from 'lucide-react';

import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface UploadResponse {
    upload_id: number;
    filename: string;
    status: string;
}

interface ResumeUploadProps {
    onUploadSuccess?: (id: number) => void;
}

export default function ResumeUpload({ onUploadSuccess }: ResumeUploadProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [file, setFile] = useState<File | null>(null);
    const [dragActive, setDragActive] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const uploadMutation = useMutation({
        mutationFn: async (fileToUpload: File) => {
            const formData = new FormData();
            formData.append('file', fileToUpload);

            const response = await api.post<UploadResponse>('/resume/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        },
        onSuccess: (data) => {
            if (onUploadSuccess) {
                onUploadSuccess(data.upload_id);
            }
        },
        onError: (err: any) => {
            setError(err.response?.data?.error?.message || "Failed to upload resume. Please try again.");
        },
    });

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const validateAndSetFile = (selectedFile: File) => {
        setError(null);
        const validTypes = ['application/pdf', 'text/markdown', 'application/x-latex'];
        // Simple check - backend does robust check
        if (!validTypes.includes(selectedFile.type) && !selectedFile.name.endsWith('.md') && !selectedFile.name.endsWith('.tex') && !selectedFile.name.endsWith('.pdf')) {
            setError("Invalid file type. Please upload PDF, Markdown, or LaTeX.");
            return;
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            setError("File too large. Maximum size is 10MB.");
            return;
        }

        setFile(selectedFile);
    };

    const clearFile = () => {
        setFile(null);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleUpload = () => {
        if (file) {
            uploadMutation.mutate(file);
        }
    };

    return (
        <Card className="w-full max-w-xl mx-auto">
            <CardHeader>
                <CardTitle>Upload Resume</CardTitle>
                <CardDescription>
                    Supported formats: PDF, Markdown, LaTeX (max 10MB)
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div
                    className={cn(
                        "relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-colors",
                        dragActive ? "border-primary bg-primary/5" : "border-border bg-background hover:bg-accent/50",
                        error ? "border-destructive/50" : ""
                    )}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        accept=".pdf,.md,.tex,.latex"
                        onChange={handleChange}
                    />

                    {!file ? (
                        <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                            <Upload className="w-10 h-10 mb-3 text-muted-foreground" />
                            <p className="mb-2 text-sm text-foreground">
                                <span className="font-semibold">Click to upload</span> or drag and drop
                            </p>
                            <p className="text-xs text-muted-foreground">
                                PDF, Markdown, or LaTeX
                            </p>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                            <FileText className="w-10 h-10 mb-3 text-primary" />
                            <p className="mb-1 text-sm font-medium text-foreground">
                                {file.name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                                {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            <Button
                                variant="ghost"
                                size="sm"
                                className="mt-2 text-destructive hover:text-destructive hover:bg-destructive/10 z-10"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    clearFile();
                                }}
                            >
                                <X className="w-4 h-4 mr-1" /> Remove
                            </Button>
                        </div>
                    )}
                </div>

                {error && (
                    <div className="flex items-center p-3 text-sm text-destructive rounded-md bg-destructive/10">
                        <AlertCircle className="w-4 h-4 mr-2" />
                        {error}
                    </div>
                )}
            </CardContent>
            <CardFooter className="flex justify-end">
                <Button
                    disabled={!file || uploadMutation.isPending}
                    onClick={handleUpload}
                    className="w-full sm:w-auto"
                >
                    {uploadMutation.isPending ? (
                        <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Uploading...
                        </>
                    ) : (
                        <>
                            Upload Resume
                        </>
                    )}
                </Button>
            </CardFooter>
        </Card>
    );
}
