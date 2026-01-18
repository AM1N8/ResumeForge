import { Link } from 'react-router-dom';
import { ArrowRight, FileText, CheckCircle, Github } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function Home() {
    return (
        <div className="flex flex-col items-center justify-center space-y-12 py-12 text-center md:py-24">
            <div className="space-y-6 max-w-3xl">
                <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
                    Build Your Perfect Internship Resume with <span className="text-primary">AI</span>
                </h1>
                <p className="mx-auto max-w-[700px] text-lg text-muted-foreground">
                    Transform your unstructured resume and GitHub data into a canonical, optimized format.
                    Stand out to recruiters with a professional, data-driven application.
                </p>
                <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
                    <Link to="/upload">
                        <Button size="lg" className="w-full sm:w-auto gap-2">
                            Start Building <ArrowRight className="w-4 h-4" />
                        </Button>
                    </Link>
                    <Link to="https://github.com/AM1N8/ResumeForge" target="_blank">
                        <Button variant="outline" size="lg" className="w-full sm:w-auto gap-2">
                            <Github className="w-4 h-4" /> View Source
                        </Button>
                    </Link>
                </div>
            </div>

            <div className="grid gap-8 sm:grid-cols-3 max-w-5xl w-full">
                <Card>
                    <CardContent className="pt-6 text-left space-y-4">
                        <div className="p-2 w-fit rounded-lg bg-primary/10">
                            <FileText className="w-6 h-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-bold">Standardized Format</h3>
                        <p className="text-muted-foreground">
                            Automatically parse PDF, Markdown, or LaTeX resumes into a canonical structure optimized for ATS.
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6 text-left space-y-4">
                        <div className="p-2 w-fit rounded-lg bg-primary/10">
                            <Github className="w-6 h-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-bold">GitHub Integration</h3>
                        <p className="text-muted-foreground">
                            Fetch top repositories and contributions to highlight your coding skills and real-world projects.
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6 text-left space-y-4">
                        <div className="p-2 w-fit rounded-lg bg-primary/10">
                            <CheckCircle className="w-6 h-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-bold">AI Structuring</h3>
                        <p className="text-muted-foreground">
                            Leverage LLMs to intelligently select best projects, normalize skills, and generate a polished resume.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
