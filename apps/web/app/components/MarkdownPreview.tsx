import React from 'react';
import ReactMarkdown from 'react-markdown';

interface MarkdownPreviewProps {
    content: string;
}

export default function MarkdownPreview({ content }: MarkdownPreviewProps) {
    return (
        <div className="prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown
                components={{
                    // Override basic elements to match our Tailwind / Dark mode theme better if needed
                    // But 'prose' (if available) or manual styles work. 
                    // Since @tailwindcss/typography might not be installed, we add manual fallbacks.
                    h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-gray-100" {...props} />,
                    h2: ({ node, ...props }) => <h2 className="text-xl font-bold mt-6 mb-3 text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 pb-1" {...props} />,
                    h3: ({ node, ...props }) => <h3 className="text-lg font-bold mt-4 mb-2 text-gray-800 dark:text-gray-200" {...props} />,
                    p: ({ node, ...props }) => <p className="mb-4 leading-relaxed text-gray-700 dark:text-gray-300" {...props} />,
                    ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-4 space-y-1 text-gray-700 dark:text-gray-300" {...props} />,
                    ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-4 space-y-1 text-gray-700 dark:text-gray-300" {...props} />,
                    li: ({ node, ...props }) => <li className="" {...props} />,
                    a: ({ node, ...props }) => <a className="text-blue-500 hover:underline" {...props} />,
                    blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-600 dark:text-gray-400 my-4" {...props} />,
                    code: ({ node, className, children, ...props }: any) => {
                        const match = /language-(\w+)/.exec(className || '')
                        const isInline = !match && !String(children).includes('\n')
                        return isInline
                            ? <code className="bg-gray-100 dark:bg-gray-800 rounded px-1 py-0.5 text-sm font-mono text-red-500 dark:text-red-400" {...props}>{children}</code>
                            : <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-xs font-mono my-4"><code className={className} {...props}>{children}</code></pre>
                    }
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
}
