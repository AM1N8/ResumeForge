import { useMemo } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
    PieChart,
    Pie,
    Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
    BarChart3,
    PieChart as PieChartIcon,
    Zap,
    CheckCircle2,
    Activity,
    Layers
} from 'lucide-react';

interface ResumeData {
    contact: any;
    summary: string | null;
    technical_skills: {
        languages: string[];
        frameworks_libraries: string[];
        tools_platforms: string[];
        databases: string[];
        other: string[];
    };
    projects: any[];
    experience: any[];
    education: any[];
    certifications: any[];
}

interface ResumeAnalyticsProps {
    data: ResumeData;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function ResumeAnalytics({ data }: ResumeAnalyticsProps) {
    // 1. Skills Distribution (Category counts)
    const skillsData = useMemo(() => {
        const skills = data.technical_skills;
        return [
            { name: 'Languages', value: skills.languages?.length || 0 },
            { name: 'Frameworks', value: skills.frameworks_libraries?.length || 0 },
            { name: 'Tools', value: skills.tools_platforms?.length || 0 },
            { name: 'Databases', value: skills.databases?.length || 0 },
            { name: 'Other', value: skills.other?.length || 0 },
        ].filter(item => item.value > 0);
    }, [data.technical_skills]);

    // 2. Technology Frequency (Across projects and experience)
    const techFrequency = useMemo(() => {
        const counts: Record<string, number> = {};

        // Count in projects
        data.projects?.forEach(p => {
            p.technologies?.forEach((tech: string) => {
                counts[tech] = (counts[tech] || 0) + 1;
            });
        });

        // Count in experience
        data.experience?.forEach(e => {
            e.technologies?.forEach((tech: string) => {
                counts[tech] = (counts[tech] || 0) + 1;
            });
        });

        return Object.entries(counts)
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value)
            .slice(0, 10); // Top 10
    }, [data.projects, data.experience]);

    // 3. Projects by Source (GitHub vs Resume)
    const sourceData = useMemo(() => {
        const github = data.projects?.filter(p => p.source === 'github' || p.source === 'both').length || 0;
        const resume = data.projects?.filter(p => p.source === 'resume').length || 0;

        return [
            { name: 'GitHub enriched', value: github },
            { name: 'Resume only', value: resume },
        ].filter(item => item.value > 0);
    }, [data.projects]);

    // 4. Completeness Indicator
    const completeness = useMemo(() => {
        const sections = [
            { label: 'Contact Info', status: !!data.contact.email },
            { label: 'Summary', status: !!data.summary },
            { label: 'Skills', status: Object.values(data.technical_skills).some(s => s.length > 0) },
            { label: 'Projects', status: data.projects?.length > 0 },
            { label: 'Experience', status: data.experience?.length > 0 },
            { label: 'Education', status: data.education?.length > 0 },
        ];

        const filled = sections.filter(s => s.status).length;
        const total = sections.length;
        const percentage = Math.round((filled / total) * 100);

        return { percentage, filled, total };
    }, [data]);

    if (!data) return null;

    return (
        <section className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-primary" />
                <h2 className="text-2xl font-bold tracking-tight">Resume Analytics & Insights</h2>
            </div>
            <p className="text-muted-foreground -mt-4 mb-6">A quantitative overview of resume content and coverage</p>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {/* Stats Cards */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Completeness</CardTitle>
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                        </div>
                        <div className="text-2xl font-bold">{completeness.percentage}%</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {completeness.filled} of {completeness.total} key sections populated
                        </p>
                        <div className="w-full bg-secondary h-2 rounded-full mt-3 overflow-hidden">
                            <div
                                className="bg-green-500 h-full transition-all duration-1000"
                                style={{ width: `${completeness.percentage}%` }}
                            />
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
                            <Zap className="h-4 w-4 text-blue-500" />
                        </div>
                        <div className="text-2xl font-bold">{data.projects?.length || 0}</div>
                        <p className="text-xs text-muted-foreground mt-1">
                            {sourceData.find(s => s.name === 'GitHub enriched')?.value || 0} enriched from GitHub
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Skill Count</CardTitle>
                            <Layers className="h-4 w-4 text-purple-500" />
                        </div>
                        <div className="text-2xl font-bold">
                            {Object.values(data.technical_skills).reduce((acc, curr) => acc + curr.length, 0)}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                            Across {skillsData.length} distinct categories
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Top Stack</CardTitle>
                            <BarChart3 className="h-4 w-4 text-orange-500" />
                        </div>
                        <div className="text-2xl font-bold truncate">
                            {techFrequency[0]?.name || 'N/A'}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                            Most frequently referenced technology
                        </p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-12">
                {/* Skills Distribution */}
                <Card className="lg:col-span-4">
                    <CardHeader>
                        <CardTitle className="text-sm flex items-center gap-2">
                            <PieChartIcon className="w-4 h-4" /> Skills Distribution
                        </CardTitle>
                        <CardDescription>By category concentration</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        {skillsData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={skillsData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {skillsData.map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'white', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    />
                                    <Legend verticalAlign="bottom" align="center" />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-sm text-muted-foreground italic">
                                No skills data available
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Tech Frequency */}
                <Card className="lg:col-span-5">
                    <CardHeader>
                        <CardTitle className="text-sm flex items-center gap-2">
                            <BarChart3 className="w-4 h-4" /> Technology Proficiency
                        </CardTitle>
                        <CardDescription>Occurrence across projects & experience</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        {techFrequency.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                    layout="vertical"
                                    data={techFrequency}
                                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} opacity={0.3} />
                                    <XAxis type="number" hide />
                                    <YAxis
                                        type="category"
                                        dataKey="name"
                                        width={80}
                                        axisLine={false}
                                        tickLine={false}
                                        fontSize={12}
                                    />
                                    <Tooltip
                                        cursor={{ fill: 'transparent' }}
                                        contentStyle={{ backgroundColor: 'white', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    />
                                    <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20}>
                                        {techFrequency.map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[0]} opacity={1 - (index * 0.08)} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-sm text-muted-foreground italic">
                                No technology data available
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Contribution Source */}
                <Card className="lg:col-span-3">
                    <CardHeader>
                        <CardTitle className="text-sm flex items-center gap-2">
                            <Zap className="w-4 h-4" /> Enrichment Impact
                        </CardTitle>
                        <CardDescription>GitHub vs Resume projects</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px] flex flex-col justify-center gap-6">
                        {sourceData.length > 0 ? (
                            <>
                                <ResponsiveContainer width="100%" height={200}>
                                    <PieChart>
                                        <Pie
                                            data={sourceData}
                                            cx="50%"
                                            cy="50%"
                                            outerRadius={60}
                                            dataKey="value"
                                            label={({ percent }) => `${((percent || 0) * 100).toFixed(0)}%`}
                                        >
                                            <Cell fill="#3b82f6" />
                                            <Cell fill="#94a3b8" />
                                        </Pie>
                                        <Tooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="space-y-2">
                                    {sourceData.map((item, idx) => (
                                        <div key={item.name} className="flex justify-between items-center text-xs">
                                            <div className="flex items-center gap-2">
                                                <div className={`w-2 h-2 rounded-full ${idx === 0 ? 'bg-blue-500' : 'bg-slate-400'}`} />
                                                <span>{item.name}</span>
                                            </div>
                                            <span className="font-bold">{item.value}</span>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="flex items-center justify-center h-full text-sm text-muted-foreground italic">
                                No source data available
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </section>
    );
}
