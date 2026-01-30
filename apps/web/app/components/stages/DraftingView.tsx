"use client";
import { useState, useEffect } from "react";
import { Play, FileText, Folder, CheckCircle, Terminal, RefreshCw, FolderOpen, FileCode, Lock, ChevronRight, ChevronDown } from "lucide-react";
import { API_BASE_URL } from "../../lib/config";
import PromptsExplorer from "../PromptsExplorer";
import LoadingOverlay from "../ui/LoadingOverlay";
import SolutionExplorer from "../SolutionExplorer";

// --- Types ---
interface FileNode {
    name: string;
    path: string;
    type: "file" | "folder";
    children?: FileNode[];
    last_modified?: number;
}

interface DraftingViewProps {
    projectId: string;
    onStageChange: (stage: number) => void;
    onCompletion?: (completed: boolean) => void;
}

export default function DraftingView({ projectId, onStageChange, onCompletion }: DraftingViewProps) {
    const [activeTab, setActiveTab] = useState<"execution" | "prompts" | "files">("execution");
    const [isRunning, setIsRunning] = useState(false);
    const [logs, setLogs] = useState<string[]>([]); // Simple log stream simulation
    const [progress, setProgress] = useState(0);

    // Load logs on mount
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/projects/${projectId}/logs`);
                const data = await res.json();
                if (data.logs) {
                    const logLines = data.logs.split("\n").filter((l: string) => l.trim() !== "");
                    setLogs(logLines);

                    // Check for completion
                    if (data.logs.includes("Migration Complete.")) {
                        setProgress(100);
                        if (onCompletion) onCompletion(true);
                    }
                }
            } catch (e) {
                console.error("Failed to load logs", e);
            }
        };
        fetchLogs();
    }, [projectId]);

    // --- Tab 1: Execution Handlers ---
    const handleRunMigration = async () => {
        setIsRunning(true);
        setLogs(["Creating Migration Orchestrator...", "Validating Governance Status: DRAFTING... OK"]);
        setProgress(10);

        // --- Start Polling ---
        const logInterval = setInterval(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/projects/${projectId}/logs?type=migration`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.logs) {
                        const logLines = data.logs.split("\n").filter((l: string) => l.trim() !== "");
                        setLogs(logLines);
                    }
                }
            } catch (err) {
                console.error("Polling error", err);
            }
        }, 1500);

        try {
            const res = await fetch(`${API_BASE_URL}/transpile/orchestrate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    project_id: projectId,
                    limit: process.env.NEXT_PUBLIC_MIGRATION_LIMIT ? parseInt(process.env.NEXT_PUBLIC_MIGRATION_LIMIT) : 0
                })
            });
            const data = await res.json();

            if (data.error) {
                setLogs(prev => [...prev, `[ERROR] ${data.error}`]);
            } else {
                // Final logs are handled by the next polling tick or the next step
                setProgress(100);
                if (onCompletion) onCompletion(true);
            }
        } catch (e) {
            setLogs(prev => [...prev, `[Network Error] ${e}`]);
        } finally {
            clearInterval(logInterval);
            setIsRunning(false);

            // Final log sync
            try {
                const res = await fetch(`${API_BASE_URL}/projects/${projectId}/logs?type=migration`);
                const data = await res.json();
                if (data.logs) {
                    const logLines = data.logs.split("\n").filter((l: string) => l.trim() !== "");
                    setLogs(logLines);
                }
            } catch (e) { }
        }
    };


    const handleApprove = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/projects/${projectId}/stage`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ stage: "3" })
            });
            const data = await res.json();
            if (data.success) {
                onStageChange(3);
            }
        } catch (e) {
            console.error("Failed to update stage", e);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
            {/* Header Tabs */}
            <div className="flex items-center px-4 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800">
                <TabButton
                    active={activeTab === "execution"}
                    onClick={() => setActiveTab("execution")}
                    icon={<Play size={16} />}
                    label="Orchestration"
                />
                <TabButton
                    active={activeTab === "prompts"}
                    onClick={() => setActiveTab("prompts")}
                    icon={<Terminal size={16} />}
                    label="Agent Prompts"
                />
                <TabButton
                    active={activeTab === "files"}
                    onClick={() => setActiveTab("files")}
                    icon={<FolderOpen size={16} />}
                    label="Output Explorer"
                />
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden p-6">
                {activeTab === "execution" && (
                    <ExecutionTab
                        isRunning={isRunning}
                        logs={logs}
                        progress={progress}
                        onRun={handleRunMigration}
                        onApprove={handleApprove}
                    />
                )}
                {activeTab === "prompts" && <div className="h-full bg-white dark:bg-gray-950 p-6 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm"><PromptsExplorer projectId={projectId} /></div>}
                {activeTab === "files" && <FileManagerTab projectId={projectId} />}
            </div>
            <LoadingOverlay isVisible={isRunning && logs.length <= 2} message="Generando Código (Drafting)..." />

        </div>
    );
}

// --- Sub-Components ---

function TabButton({ active, onClick, icon, label }: any) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${active
                ? "border-primary text-primary"
                : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                }`}
        >
            {icon} {label}
        </button>
    );
}

function ExecutionTab({ isRunning, logs, progress, onRun, onApprove }: any) {
    return (
        <div className="h-full flex flex-col gap-6 max-w-4xl mx-auto">
            {/* Control Panel */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <div>
                    <h2 className="text-xl font-bold flex items-center gap-2"><Play className="text-primary" /> Start Migration</h2>
                    <p className="text-gray-500 text-sm mt-1">Execute the full pipeline: Librarian → Topology → Developer → Compliance.</p>
                </div>
                <div className="flex items-center gap-3">
                    {progress === 100 && (
                        <button
                            onClick={onApprove}
                            className="px-6 py-3 rounded-lg font-bold text-primary border border-primary hover:bg-primary/10 transition-all flex items-center gap-2"
                        >
                            <CheckCircle size={18} /> Approve & Refine
                        </button>
                    )}
                    <button
                        onClick={onRun}
                        disabled={isRunning}
                        className={`px-6 py-3 rounded-lg font-bold text-white shadow-lg transition-all ${isRunning ? "bg-gray-400 cursor-not-allowed" : "bg-primary hover:bg-primary/90 hover:scale-105"
                            }`}
                    >
                        {isRunning ? "Running..." : "Execute Pipeline"}
                    </button>
                </div>
            </div>

            {/* Console Output */}
            <div className="flex-1 bg-black text-green-400 rounded-xl p-4 font-mono text-sm overflow-y-auto shadow-inner border border-gray-800">
                <div className="flex justify-between items-center mb-2 border-b border-gray-800 pb-2">
                    <span className="font-bold text-gray-400">CONSOLE OUTPUT</span>
                    {isRunning && <RefreshCw size={14} className="animate-spin" />}
                </div>
                <div className="space-y-1">
                    {logs.length === 0 && <span className="text-gray-600 italic">Waiting for execution...</span>}
                    {logs.map((line: string, i: number) => (
                        <div key={i} className="whitespace-pre-wrap">{`> ${line}`}</div>
                    ))}
                </div>
            </div>
        </div>
    );
}


import Editor from "@monaco-editor/react";
import MarkdownPreview from "../ui/MarkdownPreview";
import { Eye, Code as CodeIcon, Maximize2, Minimize2 } from "lucide-react";

// --- Tab 3: File Explorer with Preview (Refactored) ---

function FileManagerTab({ projectId }: { projectId: string }) {
    const [selectedFile, setSelectedFile] = useState<{ name: string, content: string, path: string } | null>(null);
    const [viewMode, setViewMode] = useState<"code" | "preview">("code");
    const [isFullScreen, setIsFullScreen] = useState(false);

    // Detect language for Monaco
    const getLanguage = (filename: string) => {
        const ext = filename.split('.').pop()?.toLowerCase();
        if (ext === 'py') return 'python';
        if (ext === 'sql') return 'sql';
        if (ext === 'json') return 'json';
        if (ext === 'md') return 'markdown';
        return 'text';
    };

    const isMD = selectedFile?.name.endsWith('.md');

    const content = (
        <div className={`flex-1 bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden flex flex-col shadow-sm ${isFullScreen ? "rounded-none border-none shadow-none" : ""}`}>
            {selectedFile ? (
                <>
                    <div className="p-3 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 text-xs font-mono text-gray-500 flex justify-between items-center shrink-0">
                        <span className="flex items-center gap-2 font-sans font-bold text-gray-700 dark:text-gray-300">
                            <FileCode size={14} className="text-primary" /> {selectedFile.name}
                        </span>

                        <div className="flex items-center gap-4">
                            {isMD && (
                                <div className="flex bg-white dark:bg-gray-800 p-1 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <button
                                        onClick={() => setViewMode("preview")}
                                        className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-[10px] font-bold transition-all ${viewMode === "preview"
                                            ? "bg-primary text-white shadow-sm"
                                            : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                                            }`}
                                    >
                                        <Eye size={12} /> VIEW
                                    </button>
                                    <button
                                        onClick={() => setViewMode("code")}
                                        className={`flex items-center gap-1.5 px-3 py-1 rounded-md text-[10px] font-bold transition-all ${viewMode === "code"
                                            ? "bg-primary text-white shadow-sm"
                                            : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                                            }`}
                                    >
                                        <CodeIcon size={12} /> CODE
                                    </button>
                                </div>
                            )}

                            <button
                                onClick={() => setIsFullScreen(!isFullScreen)}
                                className="p-1.5 text-gray-500 hover:text-primary transition-colors bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                                title={isFullScreen ? "Reducir" : "Aumentar"}
                            >
                                {isFullScreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
                            </button>

                            <span className="opacity-50 truncate max-w-[200px] hidden xl:block font-sans">{selectedFile.path}</span>
                        </div>
                    </div>
                    <div className="flex-1 overflow-hidden relative">
                        {viewMode === "code" ? (
                            <Editor
                                height="100%"
                                theme="vs-dark"
                                defaultLanguage={getLanguage(selectedFile.name)}
                                value={selectedFile.content}
                                options={{
                                    readOnly: true,
                                    minimap: { enabled: true },
                                    fontSize: isFullScreen ? 14 : 13,
                                    wordWrap: "on",
                                    automaticLayout: true,
                                    padding: { top: 20 },
                                    scrollBeyondLastLine: false
                                }}
                            />
                        ) : (
                            <div className={`h-full overflow-auto bg-white dark:bg-gray-950 custom-scrollbar ${isFullScreen ? "p-16 px-24" : "p-10"}`}>
                                <MarkdownPreview content={selectedFile.content} />
                            </div>
                        )}
                    </div>
                </>
            ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400 gap-4">
                    <FileCode size={48} className="mb-2 opacity-10" />
                    <p className="text-sm font-medium italic">Select a file from the explorer to preview</p>
                </div>
            )}
        </div>
    );

    return (
        <div className="h-full flex gap-4 overflow-hidden">
            {/* Left: Shared Tree Explorer */}
            <div className={`w-[30%] h-full transition-all duration-300 ${isFullScreen ? "w-0 opacity-0 overflow-hidden" : ""}`}>
                <SolutionExplorer
                    projectId={projectId}
                    onFileSelect={(content: string, name: string, path: string) => {
                        setSelectedFile({ content, name, path });
                        if (name.endsWith('.md')) setViewMode("preview");
                        else setViewMode("code");
                    }}
                />
            </div>

            {/* Right: Code Preview */}
            {isFullScreen ? (
                <div className="fixed inset-0 z-[9999] bg-white dark:bg-black p-4 md:p-10 animate-in fade-in zoom-in duration-300">
                    <div className="max-w-7xl mx-auto h-full shadow-2xl rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 flex flex-col">
                        {content}
                    </div>
                </div>
            ) : (
                content
            )}
        </div>
    );
}
