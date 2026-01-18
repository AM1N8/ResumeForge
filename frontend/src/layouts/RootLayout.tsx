import { Outlet, Link, useLocation } from 'react-router-dom';
import { FileText, Github, Home, Upload, History } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function RootLayout() {
    const location = useLocation();

    const navItems = [
        { href: '/', label: 'Home', icon: Home },
        { href: '/upload', label: 'Upload', icon: Upload },
        { href: '/history', label: 'History', icon: History },
        { href: '/settings', label: 'Settings', icon: FileText },
    ];

    return (
        <div className="min-h-screen bg-background font-sans antialiased">
            {/* Header */}
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container flex h-14 items-center pl-6">
                    <div className="mr-4 flex">
                        <Link to="/" className="mr-6 flex items-center space-x-2">
                            <FileText className="h-6 w-6" />
                            <span className="hidden font-bold sm:inline-block">
                                Resume Agent
                            </span>
                        </Link>
                        <nav className="flex items-center space-x-6 text-sm font-medium">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    to={item.href}
                                    className={cn(
                                        "transition-colors hover:text-foreground/80",
                                        location.pathname === item.href ? "text-foreground" : "text-foreground/60"
                                    )}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </nav>
                    </div>
                    <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                        <div className="w-full flex-1 md:w-auto md:flex-none">
                            {/* Optional Search */}
                        </div>
                        <nav className="flex items-center">
                            <Link
                                to="https://github.com/AM1N8/ResumeForge"
                                target="_blank"
                                rel="noreferrer"
                            >
                                <div className={cn("inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 w-10")}>
                                    <Github className="h-4 w-4" />
                                    <span className="sr-only">GitHub</span>
                                </div>
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container py-6 pl-6">
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="border-t py-6 md:py-0">
                <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row pl-6">
                    <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
                        Built by Amine. Source code available on GitHub.
                    </p>
                </div>
            </footer>
        </div>
    );
}
