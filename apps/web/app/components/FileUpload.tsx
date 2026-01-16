"use client";

import React, { useState } from 'react';
import { Upload, FileCode, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface UploadProps {
    onSuccess: (data: any) => void;
}

export default function FileUpload({ onSuccess }: UploadProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        if (!file.name.endsWith('.dtsx')) {
            setError('Please upload a valid .dtsx (SSIS) file.');
            return;
        }

        setIsUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/ingest/dtsx', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Failed to process package.');

            const data = await response.json();
            onSuccess(data);
        } catch (err: any) {
            setError(err.message || 'An error occurred during ingestion.');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="card-premium h-full flex flex-col justify-center items-center text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-primary/5 flex items-center justify-center mb-2">
                {isUploading ? (
                    <Loader2 className="w-8 h-8 text-primary animate-spin" />
                ) : (
                    <Upload className="w-8 h-8 text-primary" />
                )}
            </div>

            <div>
                <h3 className="font-bold text-lg dark:text-white">Ingest Legacy Asset</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 max-w-[200px]">
                    Upload a .dtsx package to start the discovery mesh.
                </p>
            </div>

            <label className="cursor-pointer group">
                <span className="bg-primary group-hover:bg-secondary text-white px-6 py-2 rounded-lg text-sm font-bold transition-all inline-block">
                    Select File
                </span>
                <input
                    type="file"
                    className="hidden"
                    accept=".dtsx"
                    onChange={handleFileUpload}
                    disabled={isUploading}
                />
            </label>

            {error && (
                <div className="flex items-center gap-2 text-error text-xs font-medium animate-in slide-in-from-top-2">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                </div>
            )}
        </div>
    );
}
