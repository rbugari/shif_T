"use client";
import React from 'react';
import { BarChart3, Database, AlertCircle, Cpu } from 'lucide-react';

interface DiscoveryDashboardProps {
    assets: any[];
    nodes: any[];
}

export default function DiscoveryDashboard({ assets, nodes }: DiscoveryDashboardProps) {
    const total = assets.length;
    const coreCount = assets.filter(a => a.type === 'CORE' || a.category === 'CORE').length;
    const highComplexity = assets.filter(a => a.complexity === 'HIGH').length;

    // Tech Stack (Extracted from extensions if available, or names)
    const ssissCount = assets.filter(a => a.name?.toLowerCase().endsWith('.dtsx')).length;
    const sqlCount = assets.filter(a => a.name?.toLowerCase().endsWith('.sql')).length;

    return (
        <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-100 dark:border-gray-800">
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                <BarChart3 size={12} /> Discovery Metrics
            </h3>

            <div className="grid grid-cols-2 gap-3">
                <MetricCard
                    label="Total Assets"
                    value={total}
                    icon={<Database size={14} className="text-blue-500" />}
                />
                <MetricCard
                    label="Core Logic"
                    value={coreCount}
                    icon={<Cpu size={14} className="text-purple-500" />}
                />
            </div>

            <div className="space-y-2 pt-2">
                <div className="flex justify-between items-center text-[11px]">
                    <span className="text-gray-500 flex items-center gap-1">
                        <AlertCircle size={12} className="text-orange-500" /> High Complexity
                    </span>
                    <span className="font-bold text-orange-600 dark:text-orange-400">{highComplexity}</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-800 h-1.5 rounded-full overflow-hidden">
                    <div
                        className="bg-orange-500 h-full transition-all duration-1000"
                        style={{ width: `${total > 0 ? (highComplexity / total) * 100 : 0}%` }}
                    />
                </div>
            </div>

            <div className="pt-2 border-t border-gray-200 dark:border-gray-800 space-y-1.5">
                <StackItem label="SSIS Packages" count={ssissCount} color="bg-blue-500" />
                <StackItem label="SQL Scripts" count={sqlCount} color="bg-orange-500" />
            </div>
        </div>
    );
}

function MetricCard({ label, value, icon }: any) {
    return (
        <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-100 dark:border-gray-700 shadow-sm">
            <div className="flex items-center justify-between mb-1">
                {icon}
                <span className="text-lg font-bold text-gray-900 dark:text-white leading-none">{value}</span>
            </div>
            <p className="text-[9px] text-gray-500 font-medium uppercase">{label}</p>
        </div>
    );
}

function StackItem({ label, count, color }: any) {
    return (
        <div className="flex justify-between items-center text-[10px]">
            <div className="flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full ${color}`} />
                <span className="text-gray-600 dark:text-gray-400">{label}</span>
            </div>
            <span className="font-mono text-gray-400">{count}</span>
        </div>
    );
}
