"use client";

import Link from "next/link";
import {
    Cpu,
    ShieldCheck,
    ArrowRight,
    Code2,
    Layers,
    CheckCircle2,
    HelpCircle,
    ChevronRight,
    Home,
    Bot,
    Database,
    FileJson,
    Terminal,
    Server
} from "lucide-react";

export default function DocsPage() {
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 font-sans selection:bg-primary/30">

            {/* Background Blobs */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 rounded-full blur-[120px] animate-pulse" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/10 rounded-full blur-[120px] animate-pulse delay-700" />
            </div>

            {/* Navigation */}
            <nav className="sticky top-0 z-50 backdrop-blur-md bg-white/70 dark:bg-gray-950/70 border-b border-gray-200 dark:border-gray-800">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2 font-bold text-xl tracking-tight text-primary">
                        <Cpu className="w-6 h-6" />
                        <span>Shift-T <span className="text-gray-400 font-normal">Docs</span></span>
                    </Link>
                    <div className="flex gap-4">
                        <Link href="/" className="text-sm font-medium hover:text-primary transition-colors flex items-center gap-1">
                            <Home className="w-4 h-4" /> Inicio
                        </Link>
                        <Link href="/dashboard" className="text-sm font-medium bg-primary text-white px-4 py-1.5 rounded-full hover:bg-secondary transition-all shadow-lg shadow-primary/20">
                            Dashboard
                        </Link>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-6 py-12 lg:py-20 flex flex-col lg:flex-row gap-12 relative z-10">

                {/* Sidebar / Quick Links */}
                <aside className="w-full lg:w-64 space-y-8 flex-shrink-0 sticky top-24 h-fit">
                    <div>
                        <h3 className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-4 px-2">Arquitectura</h3>
                        <nav className="space-y-1">
                            <a href="#agents" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white dark:hover:bg-gray-900 transition-all group">
                                <Bot className="w-4 h-4 text-gray-400 group-hover:text-primary" />
                                <span className="text-sm font-medium">Los Agentes</span>
                            </a>
                            <a href="#triage" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white dark:hover:bg-gray-900 transition-all group">
                                <span className="w-4 h-4 flex items-center justify-center text-[10px] font-bold border border-gray-400 group-hover:border-primary group-hover:text-primary rounded-full transition-colors">1</span>
                                <span className="text-sm font-medium">Fase 1: Triage</span>
                            </a>
                            <a href="#drafting" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white dark:hover:bg-gray-900 transition-all group">
                                <span className="w-4 h-4 flex items-center justify-center text-[10px] font-bold border border-gray-400 group-hover:border-primary group-hover:text-primary rounded-full transition-colors">2</span>
                                <span className="text-sm font-medium">Fase 2: Drafting</span>
                            </a>
                            <a href="#refinement" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white dark:hover:bg-gray-900 transition-all group">
                                <span className="w-4 h-4 flex items-center justify-center text-[10px] font-bold border border-gray-400 group-hover:border-primary group-hover:text-primary rounded-full transition-colors">3</span>
                                <span className="text-sm font-medium">Fase 3: Refinement</span>
                            </a>
                        </nav>
                    </div>
                </aside>

                {/* Content Area */}
                <div className="flex-1 max-w-4xl space-y-20">

                    {/* Intro Section */}
                    <section className="space-y-6">
                        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">Manual Técnico de Operaciones</h1>
                        <p className="text-lg text-gray-600 dark:text-gray-400 leading-relaxed max-w-3xl">
                            Shift-T opera como un **Orquestador Semántico**. Esta documentación detalla el funcionamiento interno de la plataforma, desglosando la arquitectura de agentes, el flujo de datos y las transformaciones específicas en cada etapa del pipeline.
                        </p>
                    </section>

                    {/* Agents Architecture */}
                    <section id="agents" className="space-y-8 scroll-mt-24">
                        <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-800">
                            <Cpu className="w-6 h-6 text-primary" />
                            <h2 className="text-2xl font-bold">1. Arquitectura de Agentes</h2>
                        </div>

                        <div className="grid gap-6 md:grid-cols-2">
                            <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg text-blue-600 dark:text-blue-400"><Bot className="w-5 h-5" /></div>
                                    <h3 className="font-bold text-lg">Agent A (Architect)</h3>
                                </div>
                                <p className="text-sm text-gray-500 mb-2"><strong>Rol:</strong> Comprensión & Clasificación.</p>
                                <p className="text-sm text-gray-500">Analiza las firmas de código extraídas por el Scanner. Clasifica activos (`CORE` vs `IGNORED`), infiere dependencias lógicas y construye el Grafo Dirigido Acíclico (DAG) inicial.</p>
                            </div>

                            <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg text-emerald-600 dark:text-emerald-400"><Code2 className="w-5 h-5" /></div>
                                    <h3 className="font-bold text-lg">Agent C (Creator)</h3>
                                </div>
                                <p className="text-sm text-gray-500 mb-2"><strong>Rol:</strong> Generación de Código.</p>
                                <p className="text-sm text-gray-500">Actúa como Senior PySpark Developer. Traduce la lógica de negocio (ej: Data Flow SSIS) a sintaxis PySpark, implementando SCD Type 2 y manejo de nulos.</p>
                            </div>

                            <div className="p-6 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm md:col-span-2">
                                <div className="flex items-center gap-3 mb-4">
                                    <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg text-purple-600 dark:text-purple-400"><ShieldCheck className="w-5 h-5" /></div>
                                    <h3 className="font-bold text-lg">Agent F (Fanatic)</h3>
                                </div>
                                <p className="text-sm text-gray-500 mb-2"><strong>Rol:</strong> Auditoría & Calidad.</p>
                                <p className="text-sm text-gray-500">Revisa el código de Agent C. Busca vulnerabilidades, asegura el cumplimiento de la Arquitectura Medallion y rechaza código que no cumpla con los estándares de producción.</p>
                            </div>
                        </div>
                    </section>

                    {/* Phase 1: Triage */}
                    <section id="triage" className="space-y-8 scroll-mt-24">
                        <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-800">
                            <Layers className="w-6 h-6 text-primary" />
                            <h2 className="text-2xl font-bold">2. Fase 1: Discovery & Triage</h2>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400">
                            El objetivo técnico de esta fase es reducir la superficie de ataque mediante un análisis estático profundo.
                        </p>

                        <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-gray-50 dark:bg-gray-900 text-xs uppercase font-bold text-gray-500">
                                    <tr>
                                        <th className="px-6 py-4">Componente</th>
                                        <th className="px-6 py-4">Detalle Técnico</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-800 bg-white dark:bg-gray-950/50">
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><Database className="w-4 h-4 text-blue-500" /> Input (Entrada)</td>
                                        <td className="px-6 py-4 text-gray-500">Código Fuente Legacy (`.dtsx`, `.sql`), Estructura de carpetas, Connection Strings.</td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><Cpu className="w-4 h-4 text-orange-500" /> Process (Proceso)</td>
                                        <td className="px-6 py-4 text-gray-500 space-y-1">
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Deep Scan (XML Parsing)</span></div>
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Agente A: Clasificación (CORE/SUPPORT)</span></div>
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Construcción de Grafo (Dagre Layout)</span></div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><FileJson className="w-4 h-4 text-green-500" /> Output (Salida)</td>
                                        <td className="px-6 py-4 text-gray-500">Manifest.json (Inventario Depurado), Grafo de Dependencias, Reporte PDF.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>

                    {/* Phase 2: Drafting */}
                    <section id="drafting" className="space-y-8 scroll-mt-24">
                        <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-800">
                            <Terminal className="w-6 h-6 text-primary" />
                            <h2 className="text-2xl font-bold">3. Fase 2: Drafting (Generación)</h2>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400">
                            Aquí ocurre la traducción semántica. No es regex; es una reimplementación de lógica basada en intenciones.
                        </p>

                        <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-gray-50 dark:bg-gray-900 text-xs uppercase font-bold text-gray-500">
                                    <tr>
                                        <th className="px-6 py-4">Componente</th>
                                        <th className="px-6 py-4">Detalle Técnico</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-800 bg-white dark:bg-gray-950/50">
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><FileJson className="w-4 h-4 text-blue-500" /> Input (Entrada)</td>
                                        <td className="px-6 py-4 text-gray-500">Manifiesto (Scope), SQL extraído del origen, Metadatos de columnas.</td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><Cpu className="w-4 h-4 text-orange-500" /> Process (Proceso)</td>
                                        <td className="px-6 py-4 text-gray-500 space-y-1">
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Task Definition (Context Injection)</span></div>
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Agente C: Escritura PySpark (SCD Type 2)</span></div>
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Validación de Sintaxis</span></div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><Code2 className="w-4 h-4 text-green-500" /> Output (Salida)</td>
                                        <td className="px-6 py-4 text-gray-500">Scripts ejecutables (.py) en `Drafting/`, Logs Técnicos de decisión.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>

                    {/* Phase 3: Refinement */}
                    <section id="refinement" className="space-y-8 scroll-mt-24">
                        <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-800">
                            <ShieldCheck className="w-6 h-6 text-primary" />
                            <h2 className="text-2xl font-bold">4. Fase 3: Refinement & Governance</h2>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400">
                            Elevación del código a estándares "Enterprise-Grade" mediante reorganización y limpieza (Medallion Architecture).
                        </p>

                        <div className="overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-gray-50 dark:bg-gray-900 text-xs uppercase font-bold text-gray-500">
                                    <tr>
                                        <th className="px-6 py-4">Componente</th>
                                        <th className="px-6 py-4">Detalle Técnico</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-800 bg-white dark:bg-gray-950/50">
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><Code2 className="w-4 h-4 text-blue-500" /> Input (Entrada)</td>
                                        <td className="px-6 py-4 text-gray-500">Notebooks Draft (V1), Design Registry (Reglas).</td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><Cpu className="w-4 h-4 text-orange-500" /> Process (Proceso)</td>
                                        <td className="px-6 py-4 text-gray-500 space-y-1">
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Agente F: Static Analysis (Vulnerabilities)</span></div>
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Layering (Bronze/Silver/Gold separation)</span></div>
                                            <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-gray-400" /> <span>Inyección de Secretos (dbutils)</span></div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 font-medium flex items-center gap-2"><Server className="w-4 h-4 text-green-500" /> Output (Salida)</td>
                                        <td className="px-6 py-4 text-gray-500">Solution Bundle (.zip) final, Certificado de Migración, Docs API.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </section>

                    {/* Footer CTA */}
                    <div className="pt-12 text-center">
                        <p className="text-gray-500 text-sm mb-4">¿Dudas sobre la implementación específica?</p>
                        <Link href="/dashboard" className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 text-white">
                            Ir a la Consola Técnica
                        </Link>
                    </div>

                </div>
            </main>

            <footer className="border-t border-gray-200 dark:border-gray-800 py-12 px-6 bg-white dark:bg-gray-950/50">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-2 font-bold text-gray-400">
                        <Cpu className="w-5 h-5" />
                        <span>Shift-T Technical Docs &copy; {new Date().getFullYear()}</span>
                    </div>
                </div>
            </footer>
        </div>
    );
}
