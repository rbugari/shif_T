"use client";
import ReactMarkdown from 'react-markdown';

interface MarkdownPreviewProps {
    content: string;
    className?: string;
}

export default function MarkdownPreview({ content, className = "" }: MarkdownPreviewProps) {
    return (
        <div className={`prose prose-sm dark:prose-invert max-w-none ${className}`}>
            <ReactMarkdown>
                {content}
            </ReactMarkdown>
        </div>
    );
}
