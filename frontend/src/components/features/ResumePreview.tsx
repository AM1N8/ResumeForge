import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Project {
    name: string;
    description: string;
    technologies: string[];
    url?: string;
    highlights: string[];
}

interface Experience {
    role: string;
    organization: string;
    location?: string;
    start_date: string;
    end_date: string;
    description: string[];
    technologies: string[];
}

interface Education {
    degree: string;
    institution: string;
    location?: string;
    graduation_date?: string;
    gpa?: string;
    relevant_coursework: string[];
    honors: string[];
}

interface ResumeData {
    contact: {
        full_name: string;
        email: string;
        phone?: string;
        location?: string;
        github?: string;
        linkedin?: string;
        website?: string;
    };
    summary: string | null;
    technical_skills: {
        languages: string[];
        frameworks_libraries: string[];
        tools_platforms: string[];
        databases: string[];
        other: string[];
    };
    projects: Project[];
    experience: Experience[];
    education: Education[];
    certifications: any[];
}

interface ResumePreviewProps {
    data: ResumeData;
}

export default function ResumePreview({ data }: ResumePreviewProps) {
    if (!data) return null;

    return (
        <Card className="w-full max-w-4xl mx-auto bg-white text-slate-900 shadow-lg border-slate-200">
            <CardHeader className="text-center pb-2">
                <CardTitle className="text-3xl font-bold uppercase tracking-tight">
                    {data.contact.full_name}
                </CardTitle>
                <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-sm text-slate-600 mt-2">
                    <span>{data.contact.email}</span>
                    {data.contact.phone && <span>{data.contact.phone}</span>}
                    {data.contact.location && <span>{data.contact.location}</span>}
                </div>
                <div className="flex flex-wrap justify-center gap-x-4 text-sm text-blue-600 font-medium pt-1">
                    {data.contact.linkedin && (
                        <a href={data.contact.linkedin} target="_blank" rel="noreferrer" className="hover:underline">LinkedIn</a>
                    )}
                    {data.contact.github && (
                        <a href={data.contact.github} target="_blank" rel="noreferrer" className="hover:underline">GitHub</a>
                    )}
                    {data.contact.website && (
                        <a href={data.contact.website} target="_blank" rel="noreferrer" className="hover:underline">Portfolio</a>
                    )}
                </div>
            </CardHeader>

            <CardContent className="space-y-6 pt-4">
                {/* Summary */}
                {data.summary && (
                    <section>
                        <h2 className="text-lg font-bold border-b border-slate-900 mb-2 uppercase tracking-wide">Summary</h2>
                        <p className="text-sm leading-relaxed text-slate-700">{data.summary}</p>
                    </section>
                )}

                {/* Technical Skills Section */}
                {data.technical_skills && (
                    <section>
                        <h2 className="text-lg font-bold border-b border-slate-900 mb-2 uppercase tracking-wide">Technical Skills</h2>
                        <div className="space-y-1 text-sm">
                            {data.technical_skills.languages?.length > 0 && (
                                <p><span className="font-bold">Languages:</span> {data.technical_skills.languages.join(", ")}</p>
                            )}
                            {data.technical_skills.frameworks_libraries?.length > 0 && (
                                <p><span className="font-bold">Frameworks & Libraries:</span> {data.technical_skills.frameworks_libraries.join(", ")}</p>
                            )}
                            {data.technical_skills.tools_platforms?.length > 0 && (
                                <p><span className="font-bold">Tools & Platforms:</span> {data.technical_skills.tools_platforms.join(", ")}</p>
                            )}
                            {data.technical_skills.databases?.length > 0 && (
                                <p><span className="font-bold">Databases:</span> {data.technical_skills.databases.join(", ")}</p>
                            )}
                        </div>
                    </section>
                )}

                {/* Experience Section */}
                {data.experience?.length > 0 && (
                    <section>
                        <h2 className="text-lg font-bold border-b border-slate-900 mb-2 uppercase tracking-wide">Work Experience</h2>
                        {data.experience.map((exp, idx) => (
                            <div key={idx} className="mb-4 last:mb-0">
                                <div className="flex justify-between items-baseline mb-1">
                                    <span className="font-bold">{exp.organization}</span>
                                    <span className="text-sm text-slate-600 tabular-nums">
                                        {exp.start_date} - {exp.end_date}
                                    </span>
                                </div>
                                <p className="italic text-sm mb-1">{exp.role} {exp.location ? `| ${exp.location}` : ''}</p>
                                <ul className="list-disc list-outside ml-4 text-sm space-y-0.5">
                                    {exp.description.map((bullet, bIdx) => (
                                        <li key={bIdx}>{bullet}</li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </section>
                )}

                {/* Projects Section */}
                {data.projects?.length > 0 && (
                    <section>
                        <h2 className="text-lg font-bold border-b border-slate-900 mb-2 uppercase tracking-wide">Key Projects</h2>
                        {data.projects.map((proj, idx) => (
                            <div key={idx} className="mb-3 last:mb-0">
                                <div className="flex justify-between items-baseline">
                                    <span className="font-bold underline decoration-slate-300 underline-offset-2">
                                        {proj.url ? (
                                            <a href={proj.url} target="_blank" rel="noreferrer" className="hover:text-blue-600">{proj.name}</a>
                                        ) : proj.name}
                                    </span>
                                    <div className="flex gap-1">
                                        {proj.technologies.slice(0, 3).map(tech => (
                                            <Badge key={tech} variant="secondary" className="text-[10px] py-0 px-1.5 h-4 bg-slate-100 text-slate-600 border-slate-200">
                                                {tech}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                                <p className="text-sm mt-1">{proj.description}</p>
                                {proj.highlights?.length > 0 && (
                                    <ul className="list-disc list-outside ml-4 mt-1 text-xs text-slate-600 space-y-0.5">
                                        {proj.highlights.map((h, hIdx) => (
                                            <li key={hIdx}>{h}</li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        ))}
                    </section>
                )}

                {/* Education Section */}
                {data.education?.length > 0 && (
                    <section>
                        <h2 className="text-lg font-bold border-b border-slate-900 mb-2 uppercase tracking-wide">Education</h2>
                        {data.education.map((edu, idx) => (
                            <div key={idx} className="mb-2 last:mb-0">
                                <div className="flex justify-between items-baseline">
                                    <div>
                                        <span className="font-bold">{edu.institution}</span>
                                        <span className="mx-2 text-slate-400">|</span>
                                        <span className="italic">{edu.degree}</span>
                                    </div>
                                    <div className="text-sm text-slate-600 tabular-nums">
                                        {edu.graduation_date}
                                    </div>
                                </div>
                                {edu.location && <p className="text-xs text-slate-500">{edu.location}</p>}
                                {edu.relevant_coursework?.length > 0 && (
                                    <p className="text-xs mt-1 text-slate-600">
                                        <span className="font-medium">Relevant Coursework:</span> {edu.relevant_coursework.join(", ")}
                                    </p>
                                )}
                            </div>
                        ))}
                    </section>
                )}
            </CardContent>
        </Card>
    );
}
