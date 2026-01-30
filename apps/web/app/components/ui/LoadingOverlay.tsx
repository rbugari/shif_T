import React from 'react';

interface LoadingOverlayProps {
    isVisible: boolean;
    message?: string;
    isBlocking?: boolean;
    onClose?: () => void;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ isVisible, message = "Procesando...", isBlocking = true, onClose }) => {
    if (!isVisible) return null;

    return (
        <div className={`fixed inset-0 z-50 flex items-center justify-center transition-all duration-500 ease-in-out ${isBlocking ? 'bg-black/40 backdrop-blur-md' : 'bg-transparent pointer-events-none'}`}>
            <style>
                {`
                @keyframes spin-gradient {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                @keyframes pulse-glow {
                    0%, 100% { box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); border-color: rgba(59, 130, 246, 0.6); }
                    50% { box-shadow: 0 0 30px rgba(59, 130, 246, 0.7); border-color: rgba(59, 130, 246, 0.9); }
                }
                .premium-loader {
                    width: 70px;
                    height: 70px;
                    border: 3px solid transparent;
                    border-top: 3px solid #3b82f6;
                    border-right: 3px solid #60a5fa;
                    border-bottom: 3px solid transparent;
                    border-radius: 50%;
                    animation: spin-gradient 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite, pulse-glow 2s ease-in-out infinite;
                    position: relative;
                }
                .premium-loader::after {
                    content: '';
                    position: absolute;
                    inset: 4px;
                    border: 2px solid transparent;
                    border-top: 2px solid #93c5fd;
                    border-radius: 50%;
                    animation: spin-gradient 2s linear infinite reverse;
                    opacity: 0.6;
                }
                `}
            </style>

            <div className={`bg-white/10 dark:bg-gray-900/40 backdrop-blur-xl rounded-2xl shadow-2xl p-10 flex flex-col items-center space-y-6 max-w-sm w-full mx-4 border border-white/20 dark:border-white/10 ring-1 ring-black/5 relative pointer-events-auto ${!isBlocking ? 'mt-auto mb-10 mr-10 ml-auto scale-90' : ''}`}>

                {onClose && (
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-white/50 hover:text-white transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}

                <div className="premium-loader"></div>
                <div className="text-xl font-light tracking-wide text-gray-800 dark:text-gray-100 text-center drop-shadow-sm">
                    {message}
                </div>
                <div className="w-full bg-gray-200/30 dark:bg-gray-700/30 h-1 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500/80 animate-[loading-bar_2s_ease-in-out_infinite]"></div>
                    <style>{`
                        @keyframes loading-bar {
                            0% { transform: translateX(-100%); }
                            100% { transform: translateX(100%); }
                        }
                    `}</style>
                </div>
            </div>
        </div>
    );
};

export default LoadingOverlay;
