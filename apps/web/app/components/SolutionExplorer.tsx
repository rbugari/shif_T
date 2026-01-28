"use client";
import { useState, useEffect } from "react";
import { Folder, FolderOpen, FileCode, RefreshCw, ChevronRight, ChevronDown } from "lucide-react";
import { API_BASE_URL } from "../lib/config";

interface FileNode {
    name: string;
    path: string;
    type: "file" | "folder";
    children?: FileNode[];
    last_modified?: number;
}

interface SolutionExplorerProps {
    projectId: string;
    filterDir?: string; // Optional: filter tree to a specific root directory (e.g. "Drafting")
    onFileSelect?: (content: string, filename: string, path: string) => void;
}

export default function SolutionExplorer({ projectId, filterDir, onFileSelect }: SolutionExplorerProps) {
    const [tree, setTree] = useState<FileNode | null>(null);
    const [selectedPath, setSelectedPath] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const loadFiles = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/projects/${projectId}/files`);
            const data = await res.json();

            // data is now always an object { name, path, type, children }
            setTree(data);
        } catch (e) {
            console.error("Failed to load files", e);
        } finally {
            setLoading(false);
        }
    };

    const handleNodeClick = async (node: FileNode) => {
        if (node.type === "file") {
            setSelectedPath(node.path);
            if (onFileSelect) {
                try {
                    const res = await fetch(`${API_BASE_URL}/projects/${projectId}/files/content?path=${encodeURIComponent(node.path)}`);
                    const data = await res.json();
                    onFileSelect(data.content || "", node.name, node.path);
                } catch (e) {
                    console.error("Failed to load file content", e);
                }
            }
        }
    };

    useEffect(() => {
        loadFiles();
    }, [projectId, filterDir]);

    return (
        <div className="h-full flex flex-col bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
            <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900 shrink-0">
                <span className="font-bold text-xs uppercase tracking-wider text-gray-500 flex items-center gap-2">
                    <Folder size={14} className="text-primary" /> {filterDir || "Solution Output"}
                </span>
                <button onClick={loadFiles} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-400">
                    <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
                {tree ? (
                    <FileTree
                        node={tree}
                        level={0}
                        onSelect={handleNodeClick}
                        selectedPath={selectedPath}
                        isRoot={true}
                    />
                ) : (
                    <div className="text-center p-8 text-gray-400 text-sm">
                        {loading ? "Loading files..." : "No files found"}
                    </div>
                )}
            </div>
        </div>
    );
}

function FileTree({ node, level, onSelect, selectedPath, isRoot }: { node: FileNode, level: number, onSelect: (n: FileNode) => void, selectedPath: string | null, isRoot?: boolean }) {
    const [isOpen, setIsOpen] = useState(isRoot || level < 1);
    const isFolder = node.type === "folder";
    const isSelected = node.path === selectedPath;

    if (isRoot && isFolder) {
        return (
            <div className="space-y-1">
                {node.children?.map((child, i) => (
                    <FileTree
                        key={i}
                        node={child}
                        level={level}
                        onSelect={onSelect}
                        selectedPath={selectedPath}
                    />
                ))}
            </div>
        );
    }

    return (
        <div className="ml-2">
            <div
                className={`flex items-center gap-2 py-1.5 px-2 rounded cursor-pointer text-sm transition-colors group justify-between ${isSelected
                    ? "bg-primary/10 text-primary font-bold shadow-sm"
                    : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                    }`}
                onClick={(e) => {
                    e.stopPropagation();
                    if (isFolder) setIsOpen(!isOpen);
                    else onSelect(node);
                }}
            >
                <div className="flex items-center gap-2 truncate">
                    <span className="text-gray-400 shrink-0">
                        {isFolder ? (isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />) : <span className="w-3.5" />}
                    </span>
                    {isFolder
                        ? (isOpen ? <FolderOpen size={14} className="text-blue-500 shrink-0" /> : <Folder size={14} className="text-blue-500 shrink-0" />)
                        : <FileCode size={14} className="text-orange-500 shrink-0" />
                    }
                    <span className="truncate">{node.name}</span>
                </div>

                {/* Date Display (Compact) */}
                {!isFolder && node.last_modified && (
                    <span className="text-[10px] text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap hidden xl:block">
                        {new Date(node.last_modified * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                )}
            </div>

            {isFolder && isOpen && node.children && (
                <div className="border-l border-gray-200 dark:border-gray-700 ml-3 pl-1 mt-1">
                    {node.children.map((child, i) => (
                        <FileTree
                            key={i}
                            node={child}
                            level={level + 1}
                            onSelect={onSelect}
                            selectedPath={selectedPath}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
