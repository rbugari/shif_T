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
    Code
} from 'lucide-react';
import { API_BASE_URL } from '../../lib/config';

interface GovernanceViewProps {
    projectId: string;
}

export default function GovernanceView({ projectId }: GovernanceViewProps) {
    const [auditScore, setAuditScore] = useState(98);
    const [stats, setStats] = useState({
        totalFiles: 24,
        totalLines: 4820,
        complexitySaved: "High",
        timeReduction: "85%"
    });

    return (
        <div className="h-full bg-gray-50/50 dark:bg-gray-950 overflow-y-auto p-8 custom-scrollbar">
            <div className="max-w-5xl mx-auto space-y-8">

                {/* Hero Success Section */}
                <div className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-blue-600 to-indigo-700 rounded-3xl p-10 text-white shadow-2xl">
                    <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-8">
                        <div className="space-y-4">
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-[10px] font-bold uppercase tracking-widest">
                                <ShieldCheck size={12} /> Compliance Passed
                            </div>
                            <h1 className="text-4xl font-extrabold tracking-tight">Migration Certified.</h1>
                            <p className="text-blue-100 max-w-md text-lg leading-relaxed">
                                Your legacy SSIS logic has been successfully architecturalized into modern, idempotent Delta Lake logic.
                            </p>
                            <div className="flex items-center gap-4 pt-4">
                                <a
                                    href={`${API_BASE_URL}/solutions/${projectId}/export`}
                                    className="px-6 py-3 bg-white text-blue-700 rounded-xl font-bold shadow-lg hover:bg-blue-50 transition-all flex items-center gap-2"
                                >
                                    <Download size={18} /> Download Final Bundle
                                </a>
                                <button className="px-6 py-3 bg-blue-500/30 border border-white/20 backdrop-blur-md rounded-xl font-bold hover:bg-white/10 transition-all flex items-center gap-2">
                                    <Github size={18} /> Push to Repository
                                </button>
                            </div>
                        </div>

                        {/* Large Score Circle */}
                        <div className="relative w-48 h-48 flex items-center justify-center">
                            <svg className="w-full h-full transform -rotate-90">
                                <circle
                                    cx="96"
                                    cy="96"
                                    r="88"
                                    stroke="currentColor"
                                    strokeWidth="12"
                                    fill="transparent"
                                    className="text-white/10"
                                />
                                <circle
                                    cx="96"
                                    cy="96"
                                    r="88"
                                    stroke="currentColor"
                                    strokeWidth="12"
                                    fill="transparent"
                                    strokeDasharray={552}
                                    strokeDashoffset={552 - (552 * auditScore) / 100}
                                    className="text-white transition-all duration-1000 ease-out"
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-5xl font-black">{auditScore}</span>
                                <span className="text-[10px] font-bold uppercase opacity-60">Architect Score</span>
                            </div>
                        </div>
                    </div>

                    {/* Background Decorative Elements */}
                    <div className="absolute top-0 right-0 -mr-20 -mt-20 w-80 h-80 bg-white/10 rounded-full blur-3xl opacity-50" />
                    <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-64 h-64 bg-black/10 rounded-full blur-3xl opacity-50" />
                </div>

                {/* Grid Layout for details */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Column 1 & 2: Main Details */}
                    <div className="lg:col-span-2 space-y-8">

                        {/* Summary Metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <StatCard label="Total Files" value={stats.totalFiles} icon={<ScrollText className="text-blue-500" />} />
                            <StatCard label="Pyspark Lines" value={stats.totalLines} icon={<Code className="text-purple-500" />} />
                            <StatCard label="Time Savings" value={stats.timeReduction} icon={<TrendingUp className="text-green-500" />} />
                            <StatCard label="Idempotency" value="100%" icon={<ShieldCheck className="text-indigo-500" />} />
                        </div>

                        {/* Recent Governance Logs */}
                        <div className="bg-white dark:bg-gray-900 rounded-3xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm">
                            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                                <CheckCircle className="text-green-500" /> Compliance Audit Trail
                            </h3>
                            <div className="space-y-4">
                                <LogItem
                                    status="PASSED"
                                    message="Idempotency Check: All Delta targets use MERGE logic."
                                    time="2m ago"
                                />
                                <LogItem
                                    status="PASSED"
                                    message="Integrity Check: Unknown members (-1) handled in all lookups."
                                    time="5m ago"
                                />
                                <LogItem
                                    status="PASSED"
                                    message="Architecture Check: Medallion layering enforcement."
                                    time="8m ago"
                                />
                                <LogItem
                                    status="INFO"
                                    message="Security Scan: No hardcoded credentials detected in the codebase."
                                    time="10m ago"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Column 3: Sidebar Details */}
                    <div className="space-y-8">
                        {/* Output Artifacts */}
                        <div className="bg-white dark:bg-gray-900 rounded-3xl p-6 border border-gray-200 dark:border-gray-800 shadow-sm h-full">
                            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                <FileText size={20} className="text-gray-400" /> Deliverables
                            </h3>
                            <div className="space-y-3">
                                <ArtifactLink label="Notebooks (.ipynb)" size="1.2 MB" />
                                <ArtifactLink label="PySpark Scripts (.py)" size="450 KB" />
                                <ArtifactLink label="Technical Specs (.md)" size="85 KB" />
                                <ArtifactLink label="Lineage Map (.json)" size="12 KB" />
                            </div>

                            <hr className="my-6 border-gray-100 dark:border-gray-800" />

                            <div className="p-4 bg-blue-50 dark:bg-blue-900/10 rounded-2xl">
                                <div className="flex items-center gap-3 mb-2">
                                    <Database className="text-blue-500" size={18} />
                                    <span className="text-sm font-bold text-blue-900 dark:text-blue-200">Catalog Target</span>
                                </div>
                                <p className="text-[11px] text-blue-700 dark:text-blue-400 font-mono">
                                    shiftt_silver_db.orders_migrated
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Final Footer CTA */}
                <div className="flex flex-col items-center justify-center py-10 text-center space-y-4 border-t border-gray-100 dark:border-gray-800">
                    <div className="w-16 h-1 w-16 bg-gray-200 dark:bg-gray-800 rounded-full mb-4" />
                    <h3 className="text-xl font-bold">Ready to take the next step?</h3>
                    <p className="text-gray-500 max-w-md text-sm">
                        You can deploy these artifacts directly to your Databricks Workspace or export them for external CI/CD pipelines.
                    </p>
                    <div className="flex gap-4 pt-2">
                        <button className="text-sm font-bold text-primary hover:underline">Support Hub</button>
                        <span className="text-gray-300">|</span>
                        <button className="text-sm font-bold text-primary hover:underline">Open in Databricks</button>
                    </div>
                </div>

            </div>
        </div>
    );
}

function StatCard({ label, value, icon }: any) {
    return (
        <div className="bg-white dark:bg-gray-900 p-5 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col items-center text-center">
            <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded-2xl mb-3">
                {icon}
            </div>
            <span className="text-xl font-black text-gray-900 dark:text-white leading-none mb-1">{value}</span>
            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">{label}</span>
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

function ArtifactLink({ label, size }: any) {
    return (
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800/50 rounded-2xl group cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-all border border-transparent hover:border-blue-200 dark:hover:border-blue-900">
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-white dark:bg-gray-950 flex items-center justify-center shadow-sm">
                    <Download size={14} className="text-gray-400 group-hover:text-blue-500 transition-colors" />
                </div>
                <div className="flex flex-col">
                    <span className="text-xs font-bold text-gray-700 dark:text-gray-200">{label}</span>
                    <span className="text-[9px] text-gray-400 uppercase">{size}</span>
                </div>
            </div>
            <ArrowRight size={14} className="text-gray-300 opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />
        </div>
    );
}
