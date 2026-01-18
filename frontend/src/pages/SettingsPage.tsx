import { ArrowLeft, RotateCcw } from 'lucide-react';
import { Link } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useSettings } from '@/hooks/use-settings';
import { cn } from '@/lib/utils';

export default function SettingsPage() {
    const {
        projectCount,
        resumeLanguage,
        verbosity,
        primaryColor,
        updateSettings,
        resetSettings
    } = useSettings();

    const colors = [
        { name: 'blue', value: 'RoyalBlue', class: 'bg-blue-600' },
        { name: 'navy', value: 'NavyBlue', class: 'bg-blue-900' },
        { name: 'teal', value: 'TealBlue', class: 'bg-teal-600' },
        { name: 'maroon', value: 'Maroon', class: 'bg-red-800' },
        { name: 'purple', value: 'Plum', class: 'bg-purple-600' },
        { name: 'black', value: 'black', class: 'bg-black' },
    ];

    const languages = ['English', 'French', 'Spanish', 'German', 'Italian'];
    const verbosities = ['Concise', 'Standard', 'Detailed'];

    return (
        <div className="max-w-2xl mx-auto space-y-8 py-8">
            <div className="flex items-center gap-4">
                <Link to="/">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold">Settings</h1>
                    <p className="text-muted-foreground">Customize your resume generation preferences.</p>
                </div>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Content Preferences</CardTitle>
                    <CardDescription>Control how the AI structures and writes your resume.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Project Count */}
                    <div className="space-y-2">
                        <Label htmlFor="projectCount">Number of Projects ({projectCount})</Label>
                        <div className="flex items-center gap-4">
                            <input
                                type="range"
                                id="projectCount"
                                min="1"
                                max="10"
                                className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
                                value={projectCount}
                                onChange={(e) => updateSettings({ projectCount: parseInt(e.target.value) })}
                            />
                            <span className="w-8 text-center font-mono">{projectCount}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Projects to include from your parsed data.</p>
                    </div>

                    {/* Language */}
                    <div className="space-y-2">
                        <Label>Resume Language</Label>
                        <div className="grid grid-cols-3 gap-2">
                            {languages.map((lang) => (
                                <Button
                                    key={lang}
                                    variant={resumeLanguage === lang ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => updateSettings({ resumeLanguage: lang })}
                                    className="w-full"
                                >
                                    {lang}
                                </Button>
                            ))}
                        </div>
                    </div>

                    {/* Verbosity */}
                    <div className="space-y-2">
                        <Label>Writing Style</Label>
                        <div className="grid grid-cols-3 gap-2">
                            {verbosities.map((verb) => (
                                <Button
                                    key={verb}
                                    variant={verbosity === verb ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => updateSettings({ verbosity: verb })}
                                    className="w-full"
                                >
                                    {verb}
                                </Button>
                            ))}
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Appearance</CardTitle>
                    <CardDescription>Styling options for the generated PDF export.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Primary Color */}
                    <div className="space-y-3">
                        <Label>Accent Color</Label>
                        <div className="flex flex-wrap gap-3">
                            {colors.map((color) => (
                                <button
                                    key={color.name}
                                    onClick={() => updateSettings({ primaryColor: color.name })}
                                    className={cn(
                                        "w-10 h-10 rounded-full transition-all ring-offset-2 ring-offset-background",
                                        color.class,
                                        primaryColor === color.name ? "ring-2 ring-foreground scale-110" : "hover:scale-105"
                                    )}
                                    title={color.name}
                                />
                            ))}
                        </div>
                        <p className="text-xs text-muted-foreground">Used for headings and links in the LaTeX export.</p>
                    </div>
                </CardContent>
            </Card>

            <div className="flex justify-end">
                <Button variant="ghost" onClick={resetSettings} className="gap-2 text-muted-foreground hover:text-destructive">
                    <RotateCcw className="h-4 w-4" /> Reset Defaults
                </Button>
            </div>
        </div>
    );
}
