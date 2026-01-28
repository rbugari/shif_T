import React from 'react';

interface LoadingOverlayProps {
    isVisible: boolean;
    message?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ isVisible, message = "Procesando..." }) => {
    if (!isVisible) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity duration-300">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 flex flex-col items-center space-y-4 max-w-sm w-full mx-4 border border-gray-200 dark:border-gray-700">
                <div className="relative w-16 h-16">
                    <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-200 dark:border-blue-900 rounded-full"></div>
                    <div className="absolute top-0 left-0 w-full h-full border-4 border-blue-600 dark:border-blue-500 rounded-full animate-spin border-t-transparent"></div>
                </div>
                <div className="text-lg font-medium text-gray-900 dark:text-gray-100 text-center animate-pulse">
                    {message}
                </div>
            </div>
        </div>
    );
};

export default LoadingOverlay;
