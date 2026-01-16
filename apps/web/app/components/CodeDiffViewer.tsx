"use client";
import React from 'react';
import { DiffEditor } from '@monaco-editor/react';

interface CodeDiffViewerProps {
    originalCode: string;
    modifiedCode: string;
    language?: string;
    theme?: string;
}

export default function CodeDiffViewer({
    originalCode,
    modifiedCode,
    language = "python",
    theme = "vs-dark"
}: CodeDiffViewerProps) {
    return (
        <div className="h-full w-full border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
            <DiffEditor
                height="100%"
                language={language}
                original={originalCode}
                modified={modifiedCode}
                theme={theme}
                options={{
                    readOnly: true,
                    renderSideBySide: true,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false
                }}
            />
        </div>
    );
}
