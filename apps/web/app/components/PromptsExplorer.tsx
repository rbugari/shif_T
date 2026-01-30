"use client";
import { useState, useEffect } from "react";
import { Terminal, Eye, Code as CodeIcon, Maximize2, Minimize2 } from "lucide-react";
import { API_BASE_URL } from "../lib/config";
import Editor from "@monaco-editor/react";
import MarkdownPreview from "./ui/MarkdownPreview";

interface PromptsExplorerProps {
    className?: string;
    projectId?: string;
}

export default function PromptsExplorer({ className, projectId }: PromptsExplorerProps) {
    const [prompts, setPrompts] = useState<{ [key: string]: string }>({});
    const [loading, setLoading] = useState(true);
    const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState<"template" | "compiled">("template");
    const [contentViewMode, setContentViewMode] = useState<"preview" | "code">("preview");
    const [isFullScreen, setIsFullScreen] = useState(false);

    useEffect(() => {
        const fetchPrompts = async () => {
            setLoading(true);
            try {
                const params = projectId && viewMode === "compiled" ? `?project_id=${projectId}&compiled=true` : "";

                const [a, c, f, g] = await Promise.all([
                    fetch(`${API_BASE_URL}/prompts/agent-a${params}`).then(r => r.json()),
                    fetch(`${API_BASE_URL}/prompts/agent-c${params}`).then(r => r.json()),
                    fetch(`${API_BASE_URL}/prompts/agent-f${params}`).then(r => r.json()),
                    fetch(`${API_BASE_URL}/prompts/agent-g${params}`).then(r => r.json())
                ]);
                const loadedPrompts = {
                    "Agent A (Detective)": a.prompt,
                    "Agent C (Developer)": c.prompt,
                    "Agent F (Compliance)": f.prompt,
                    "Agent G (Governance)": g.prompt
                };
                setPrompts(loadedPrompts);
                if (!selectedAgent) setSelectedAgent(Object.keys(loadedPrompts)[0]);
            } catch (e) {
                console.error("Failed to load prompts", e);
            } finally {
                setLoading(false);
            }
        };
        fetchPrompts();
    }, [projectId, viewMode]);

    if (loading) return (
        <div className="h-full flex items-center justify-center p-10 text-gray-500 bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800">
            <div className="flex flex-col items-center gap-3">
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm font-medium">Loading Intelligence Hub...</span>
            </div>
        </div>
    );

    const content = (
        <div className={`flex flex-col gap-4 h-full ${isFullScreen ? "p-6 bg-gray-50 dark:bg-black overflow-hidden" : ""}`}>
            {/* Mode Toggle Header */}
            <div className="flex items-center justify-between bg-white dark:bg-gray-900 p-2 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm shrink-0">
                <div className="flex items-center gap-2 px-3">
                    <Terminal className="w-4 h-4 text-primary" />
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">Intelligence Hub</span>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex bg-gray-100 dark:bg-gray-800 p-1 rounded-lg">
                        <button
                            onClick={() => setViewMode("template")}
                            className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${viewMode === "template"
                                ? "bg-white dark:bg-gray-700 text-primary shadow-sm ring-1 ring-black/5"
                                : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                                }`}
                        >
                            Template
                        </button>
                        <button
                            onClick={() => setViewMode("compiled")}
                            className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${viewMode === "compiled"
                                ? "bg-white dark:bg-gray-700 text-primary shadow-sm ring-1 ring-black/5"
                                : projectId
                                    ? "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                                    : "text-gray-300 dark:text-gray-600 cursor-not-allowed opacity-50"
                                }`}
                            disabled={!projectId}
                            title={!projectId ? "Selecciona un proyecto para ver los prompts compilados" : "Ver prompts con contexto real del proyecto"}
                        >
                            {projectId ? "Compiled" : "Compiled (Select Project)"}
                        </button>
                    </div>

                    <button
                        onClick={() => setIsFullScreen(!isFullScreen)}
                        className="p-2 text-gray-500 hover:text-primary transition-colors bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 mx-1"
                        title={isFullScreen ? "Minimizar" : "Maximizar"}
                    >
                        {isFullScreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 flex-1 overflow-hidden">
                <div className="col-span-1 space-y-2 border-r border-gray-200 dark:border-gray-800 pr-4 overflow-y-auto custom-scrollbar leading-none font-sans">
                    {Object.keys(prompts).map(key => (
                        <div
                            key={key}
                            onClick={() => setSelectedAgent(key)}
                            className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedAgent === key
                                ? "bg-blue-50 dark:bg-blue-900/20 border-primary shadow-sm"
                                : "bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-600"
                                }`}
                        >
                            <h3 className={`font-bold text-sm ${selectedAgent === key ? "text-primary" : ""}`}>{key}</h3>
                            <p className="text-[10px] text-gray-500 capitalize">{viewMode} Prompt</p>
                        </div>
                    ))}
                </div>
                <div className="col-span-3 bg-gray-50 dark:bg-gray-950 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 relative flex flex-col">
                    {selectedAgent ? (
                        <>
                            <div className="p-2 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex justify-between items-center shrink-0">
                                <span className="text-[10px] font-bold text-gray-400 px-2 uppercase tracking-widest">{selectedAgent}</span>

                                <div className="flex items-center gap-2">
                                    <div className="flex bg-gray-100 dark:bg-gray-800 p-1 rounded-lg border border-gray-200 dark:border-gray-700">
                                        <button
                                            onClick={() => setContentViewMode("preview")}
                                            className={`flex items-center gap-1 px-3 py-1 rounded-md text-[10px] font-bold transition-all ${contentViewMode === "preview"
                                                ? "bg-primary text-white"
                                                : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                                                }`}
                                        >
                                            <Eye size={12} /> VIEW
                                        </button>
                                        <button
                                            onClick={() => setContentViewMode("code")}
                                            className={`flex items-center gap-1 px-3 py-1 rounded-md text-[10px] font-bold transition-all ${contentViewMode === "code"
                                                ? "bg-primary text-white"
                                                : "text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                                                }`}
                                        >
                                            <CodeIcon size={12} /> CODE
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div className="flex-1 overflow-hidden relative">
                                {contentViewMode === "code" ? (
                                    <div className="h-full bg-[#1e1e1e]">
                                        <Editor
                                            height="100%"
                                            defaultLanguage="markdown"
                                            theme="vs-dark"
                                            value={prompts[selectedAgent]}
                                            options={{
                                                readOnly: true,
                                                minimap: { enabled: isFullScreen },
                                                fontSize: isFullScreen ? 14 : 12,
                                                wordWrap: "on",
                                                scrollBeyondLastLine: false,
                                                padding: { top: 16 },
                                                lineNumbers: "off",
                                                folding: isFullScreen,
                                                glyphMargin: false,
                                                lineDecorationsWidth: 0,
                                                lineNumbersMinChars: 0,
                                                automaticLayout: true
                                            }}
                                        />
                                    </div>
                                ) : (
                                    <div className={`h-full overflow-auto bg-white dark:bg-gray-950 custom-scrollbar ${isFullScreen ? "p-12" : "p-8"}`}>
                                        <MarkdownPreview content={prompts[selectedAgent]} />
                                    </div>
                                )}
                            </div>
                        </>
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-400 italic text-sm italic">Select an agent to view its prompt</div>
                    )}
                </div>
            </div>
        </div>
    );

    if (isFullScreen) {
        return (
            <div className="fixed inset-0 z-[9999] bg-white dark:bg-black p-4 md:p-10 animate-in fade-in zoom-in duration-300">
                <div className="max-w-7xl mx-auto h-full shadow-2xl rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
                    {content}
                </div>
            </div>
        );
    }

    return (
        <div className={`h-full ${className}`}>
            {content}
        </div>
    );
}
