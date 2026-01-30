"use client";
import React, { useEffect, useState } from 'react';
import {
    CheckCircle,
    ShieldCheck,
    FileText,
    Download,
    ArrowRight,
    Github,
    Server,
    Database,
    AlertCircle,
    TrendingUp,
    ScrollText,
    ExternalLink,
    Code,
    Maximize2,
    Minimize2,
    Layout
} from 'lucide-react';
import { API_BASE_URL } from '../../lib/config';
import SolutionExplorer from '../SolutionExplorer';
import { Editor } from '@monaco-editor/react';
import MarkdownPreview from '../MarkdownPreview';

interface GovernanceViewProps {
    projectId: string;
}

export default function GovernanceView({ projectId }: GovernanceViewProps) {
    const [report, setReport] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    // UI State
    const [activeTab, setActiveTab] = useState<"summary" | "files">("summary");
    const [selectedFileContent, setSelectedFileContent] = useState<string>("");
    const [selectedFileName, setSelectedFileName] = useState<string>("");
    const [viewMode, setViewMode] = useState<"code" | "preview">("code");
    const [isFullScreen, setIsFullScreen] = useState(false);

    useEffect(() => {
        fetch(`${API_BASE_URL}/projects/${projectId}/governance`)
            .then(res => res.json())
            .then(data => {
                setReport(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch governance report:", err);
                setLoading(false);
            });
    }, [projectId]);

    const handleFileSelect = (content: string, name: string, path: string) => {
        setSelectedFileContent(content);
        setSelectedFileName(name);

        // Auto-switch based on extension
        if (name.endsWith(".md")) {
            setViewMode("preview");
        } else {
            setViewMode("code");
        }
    };

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center bg-gray-50/50 dark:bg-gray-950 text-gray-500">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <p className="font-bold animate-pulse">Generating Certification Report...</p>
                </div>
            </div>
        );
    }

    const auditScore = report?.score ?? 0;
    const stats = report?.stats ?? {
        bronze_count: 0,
        silver_count: 0,
        gold_count: 0,
        total_files: 0,
        total_lines: 0
    };

    return (
        <div className={`h-full bg-gray-50/50 dark:bg-gray-950 overflow-hidden flex flex-col relative`}>

            {/* --- FULLSCREEN OVERLAY MODE (Only for Files) --- */}
            {isFullScreen && (
                <div className="flex flex-col h-screen fixed inset-0 z-50 bg-gray-950">
                    <div className="h-14 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-4 shrink-0">
                        <div className="flex items-center gap-2">
                            <FileText size={16} className="text-blue-500" />
                            <span className="font-bold text-gray-200">{selectedFileName || "Solution Explorer"}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            {selectedFileName.endsWith(".md") && (
                                <div className="flex bg-gray-800 rounded-lg p-0.5 mr-4">
                                    <button
                                        onClick={() => setViewMode("preview")}
                                        className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${viewMode === "preview" ? "bg-blue-600 text-white shadow-sm" : "text-gray-400 hover:text-white"}`}
                                    >
                                        Preview
                                    </button>
                                    <button
                                        onClick={() => setViewMode("code")}
                                        className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${viewMode === "code" ? "bg-blue-600 text-white shadow-sm" : "text-gray-400 hover:text-white"}`}
                                    >
                                        Code
                                    </button>
                                </div>
                            )}
                            <button
                                onClick={() => setIsFullScreen(false)}
                                className="p-2 hover:bg-gray-800 text-gray-400 hover:text-white rounded-lg transition-colors"
                            >
                                <Minimize2 size={18} />
                            </button>
                        </div>
                    </div>
                    <div className="flex-1 flex overflow-hidden">
                        <div className="w-64 border-r border-gray-800 bg-gray-900/50 hidden md:flex flex-col">
                            <SolutionExplorer
                                projectId={projectId}
                                filterDir="Refined"
                                onFileSelect={handleFileSelect}
                            />
                        </div>
                        <div className="flex-1 bg-[#1e1e1e]">
                            {selectedFileName ? (
                                viewMode === "preview" ? (
                                    <div className="h-full overflow-y-auto p-8 bg-white dark:bg-gray-900">
                                        <MarkdownPreview content={selectedFileContent} />
                                    </div>
                                ) : (
                                    <Editor
                                        height="100%"
                                        language={selectedFileName.endsWith('.py') ? 'python' : selectedFileName.endsWith('.sql') ? 'sql' : 'markdown'}
                                        theme="vs-dark"
                                        value={selectedFileContent}
                                        options={{
                                            readOnly: true,
                                            minimap: { enabled: true },
                                            fontSize: 14,
                                            scrollBeyondLastLine: false,
                                        }}
                                    />
                                )
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-gray-500">
                                    <FileText size={48} className="opacity-20 mb-4" />
                                    <p>Select a file to review logic</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}


            {/* --- TOP HEADER (Compact) --- */}
            <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-4 shrink-0 flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-white shadow-lg">
                        <span className="font-black text-lg">{auditScore}</span>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                            Governance Output <ShieldCheck size={18} className="text-green-500" />
                        </h1>
                        <p className="text-xs text-gray-500">Migration Certified & Ready for Deployment</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <a
                        href={`${API_BASE_URL}/projects/${projectId}/export`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors font-semibold flex items-center gap-2"
                    >
                        <Download size={16} /> Assets
                    </a>
                    <button
                        className="px-4 py-2 text-sm bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold shadow-sm flex items-center gap-2"
                        title="Push to Git (Coming Soon)"
                    >
                        <Github size={16} /> Push to Git
                    </button>
                    <a
                        href={`${API_BASE_URL}/projects/${projectId}/governance/report`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-sm flex items-center gap-2"
                    >
                        <FileText size={16} /> PDF Report
                    </a>
                </div>
            </div>

            {/* --- TABS --- */}
            <div className="flex items-center gap-6 px-6 border-b border-gray-200 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-950/50 shrink-0">
                <button
                    onClick={() => setActiveTab("summary")}
                    className={`py-3 text-sm font-bold border-b-2 transition-all ${activeTab === "summary"
                        ? "border-blue-500 text-blue-600 dark:text-blue-400"
                        : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                        }`}
                >
                    Executive Summary
                </button>
                <button
                    onClick={() => setActiveTab("files")}
                    className={`py-3 text-sm font-bold border-b-2 transition-all flex items-center gap-2 ${activeTab === "files"
                        ? "border-blue-500 text-blue-600 dark:text-blue-400"
                        : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                        }`}
                >
                    Solution Explorer <Code size={14} />
                </button>
            </div>

            {/* --- CONTENT AREA --- */}
            <div className="flex-1 overflow-hidden p-6 relative">

                {activeTab === "summary" && (
                    <div className="h-full overflow-y-auto custom-scrollbar max-w-5xl mx-auto space-y-8 pb-20">
                        {/* Metrics Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard label="Total Refined" value={stats.total_files} icon={<ScrollText className="text-blue-500" />} />
                            <StatCard label="Pyspark Lines" value={stats.total_lines} icon={<Code className="text-purple-500" />} />
                            <StatCard label="Medallion Layers" value="3/3" icon={<Database className="text-green-500" />} />
                            <StatCard label="Idempotency" value="100%" icon={<ShieldCheck className="text-indigo-500" />} />
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* Lineage */}
                            <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                                    <TrendingUp size={20} className="text-indigo-500" /> Architecture Lineage
                                </h3>
                                <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                    {report?.lineage?.map((item: any, idx: number) => (
                                        <LineageRow key={idx} item={item} />
                                    ))}
                                </div>
                            </div>

                            {/* Logs */}
                            <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                                    <CheckCircle size={20} className="text-green-500" /> Audit Trail
                                </h3>
                                <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                    {report?.compliance_logs?.length > 0 ? (
                                        report.compliance_logs.map((log: any, idx: number) => (
                                            <LogItem
                                                key={idx}
                                                status={log.status}
                                                message={log.message}
                                                time={log.time}
                                            />
                                        ))
                                    ) : (
                                        <div className="text-center py-4 text-gray-400 text-sm italic">
                                            No certification logs found.
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "files" && (
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">
                        {/* Sidebar Tree */}
                        <div className="lg:col-span-3 h-full overflow-hidden bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col">
                            <div className="p-3 border-b border-gray-100 dark:border-gray-800 font-bold text-xs uppercase text-gray-500">
                                Project Artifacts
                            </div>
                            <div className="flex-1 overflow-y-auto p-2">
                                <SolutionExplorer
                                    projectId={projectId}
                                    filterDir="Refined"
                                    onFileSelect={handleFileSelect}
                                />
                            </div>
                        </div>

                        {/* Content Viewer */}
                        <div className="lg:col-span-9 h-full bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col">
                            <div className="p-2 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex justify-between items-center shrink-0">
                                <h3 className="text-xs font-bold uppercase text-gray-500 flex items-center gap-2 pl-2">
                                    <Code size={14} className="text-indigo-500" />
                                    {selectedFileName || "Editor"}
                                </h3>
                                <div className="flex items-center gap-2">
                                    {selectedFileName.endsWith(".md") && (
                                        <div className="flex bg-gray-200 dark:bg-gray-800 rounded-lg p-0.5 mr-2">
                                            <button
                                                onClick={() => setViewMode("preview")}
                                                className={`px-2 py-0.5 text-[10px] font-bold rounded transition-all ${viewMode === "preview" ? "bg-white dark:bg-gray-700 shadow-sm" : "text-gray-400"}`}
                                            >
                                                Preview
                                            </button>
                                            <button
                                                onClick={() => setViewMode("code")}
                                                className={`px-2 py-0.5 text-[10px] font-bold rounded transition-all ${viewMode === "code" ? "bg-white dark:bg-gray-700 shadow-sm" : "text-gray-400"}`}
                                            >
                                                Code
                                            </button>
                                        </div>
                                    )}
                                    <button
                                        onClick={() => setIsFullScreen(true)}
                                        className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-400 transition-colors"
                                        title="Full Screen"
                                    >
                                        <Maximize2 size={14} />
                                    </button>
                                </div>
                            </div>
                            <div className="flex-1 bg-[#1e1e1e] overflow-hidden relative">
                                {selectedFileName ? (
                                    viewMode === "preview" ? (
                                        <div className="h-full overflow-y-auto p-6 bg-white dark:bg-gray-900">
                                            <MarkdownPreview content={selectedFileContent} />
                                        </div>
                                    ) : (
                                        <Editor
                                            height="100%"
                                            language={selectedFileName.endsWith('.py') ? 'python' : selectedFileName.endsWith('.sql') ? 'sql' : 'markdown'}
                                            theme="vs-dark"
                                            value={selectedFileContent}
                                            options={{
                                                readOnly: true,
                                                minimap: { enabled: false },
                                                fontSize: 13,
                                                padding: { top: 16 },
                                                scrollBeyondLastLine: false,
                                            }}
                                        />
                                    )
                                ) : (
                                    <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500 z-0">
                                        <FileText size={48} className="opacity-20 mb-4" />
                                        <p className="text-sm">Select a file to review</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}

function StatCard({ label, value, icon }: any) {
    return (
        <div className="bg-white dark:bg-gray-900 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm flex items-center gap-4">
            <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded-xl">
                {icon}
            </div>
            <div>
                <span className="block text-xl font-black text-gray-900 dark:text-white leading-none">{value}</span>
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">{label}</span>
            </div>
        </div>
    );
}

function LogItem({ status, message, time }: any) {
    return (
        <div className="flex items-start gap-4 p-3 hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded-2xl transition-all cursor-default group">
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full mt-1 ${status === 'PASSED' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                }`}>
                {status}
            </span>
            <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-snug">{message}</p>
                <span className="text-[10px] text-gray-400">{time}</span>
            </div>
        </div>
    );
}

function LineageRow({ item }: any) {
    return (
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-4 rounded-xl bg-gray-50 dark:bg-gray-800/30 border border-gray-100 dark:border-gray-800">
            <LineageNode label="Source" name={item.source} icon={<FileText size={14} />} color="gray" />
            <LineageConnector />
            <LineageNode label="Bronze" name={item.targets.bronze} icon={<Database size={14} />} color="blue" />
            <LineageConnector />
            <LineageNode label="Silver" name={item.targets.silver} icon={<ShieldCheck size={14} />} color="indigo" />
            <LineageConnector />
            <LineageNode label="Gold" name={item.targets.gold} icon={<TrendingUp size={14} />} color="green" />
        </div>
    );
}

function LineageNode({ label, name, icon, color }: any) {
    const colors: any = {
        gray: "bg-gray-500",
        blue: "bg-blue-500",
        indigo: "bg-indigo-500",
        green: "bg-green-500"
    };

    return (
        <div className="flex flex-col items-center gap-1 min-w-[100px]">
            <span className="text-[9px] font-bold text-gray-400 uppercase">{label}</span>
            <div className={`p-2 rounded-xl ${colors[color]} text-white shadow-sm flex items-center gap-2 w-full justify-center`}>
                {icon}
                <span className="text-[10px] font-bold truncate max-w-[100px]">{name.split('.').pop()}</span>
            </div>
        </div>
    );
}

function LineageConnector() {
    return (
        <div className="hidden md:flex flex-1 items-center justify-center">
            <div className="h-[1px] w-full bg-gray-300 dark:bg-gray-700 relative">
                <ArrowRight size={10} className="absolute right-0 -top-[4px] text-gray-300 dark:text-gray-700" />
            </div>
        </div>
    );
}
