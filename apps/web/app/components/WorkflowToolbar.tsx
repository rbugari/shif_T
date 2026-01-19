"use client";

import { Map, FileEdit, Code, CheckCircle, ArrowRight } from "lucide-react";

interface WorkflowToolbarProps {
    currentStage: number;
    onSetStage: (stage: number) => void;
    actionLabel?: string;
    onAction?: () => void;
    actionDisabled?: boolean;
}

const WorkflowToolbar: React.FC<WorkflowToolbarProps> = ({
    currentStage,
    onSetStage,
    actionLabel,
    onAction,
    actionDisabled
}) => {
    const stages = [
        { id: 1, label: "Triaje", icon: Map },
        { id: 2, label: "Drafting", icon: FileEdit },
        { id: 3, label: "Refinamiento", icon: Code },
        { id: 4, label: "Output", icon: CheckCircle },
    ];

    return (
        <div className="w-full max-w-2xl mx-auto my-2 select-none flex items-center gap-4">
            <div className="flex-1 flex items-center justify-between bg-white dark:bg-gray-900 rounded-full border border-gray-200 dark:border-gray-800 p-1.5 shadow-sm">
                {stages.map((stage, idx) => {
                    const isActive = currentStage === stage.id;
                    const isPast = currentStage > stage.id;
                    const Icon = stage.icon;

                    return (
                        <div key={stage.id} className="flex items-center">
                            <button
                                onClick={() => onSetStage(stage.id)}
                                className={`
                                    flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all
                                    ${isActive
                                        ? "bg-primary text-white shadow-md"
                                        : isPast
                                            ? "text-primary hover:bg-primary/5"
                                            : "text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                                    }
                                `}
                            >
                                <Icon size={14} className={isActive ? "animate-pulse" : ""} />
                                <span className="hidden sm:inline">{stage.label}</span>
                            </button>

                            {/* Connector Line (except for last item) */}
                            {idx < stages.length - 1 && (
                                <div className="mx-1 text-gray-300 dark:text-gray-700">
                                    <ArrowRight size={12} />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Action Button */}
            {actionLabel && onAction && (
                <button
                    onClick={onAction}
                    disabled={actionDisabled}
                    className={`
                        flex items-center gap-2 px-5 py-2.5 rounded-full font-bold text-xs shadow-lg transition-all
                        ${actionDisabled
                            ? "bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600 cursor-not-allowed"
                            : "bg-primary text-white hover:bg-secondary hover:scale-105"
                        }
                    `}
                >
                    {actionLabel} <ArrowRight size={14} />
                </button>
            )}
        </div>
    );
};

export default WorkflowToolbar;
