import React, { useEffect, useState } from 'react';

const ProcessingSteps = ({ status }) => {
    const steps = [
        { id: 'upload', label: '文件上傳', icon: '📤' },
        { id: 'layout', label: '版面分析', icon: '🔍' },
        { id: 'structure', label: '結構提取', icon: '🏗️' },
        { id: 'ocr', label: '文字識別', icon: '🔤' },
        { id: 'finalize', label: '結果生成', icon: '✨' }
    ];

    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        if (status === 'pending') setCurrentStep(0);
        else if (status === 'processing') {
            // Simulate progress through steps
            const interval = setInterval(() => {
                setCurrentStep(prev => (prev < 3 ? prev + 1 : prev));
            }, 1500);
            return () => clearInterval(interval);
        } else if (status === 'done') {
            setCurrentStep(4);
        }
    }, [status]);

    return (
        <div className="w-full max-w-3xl mx-auto mb-8">
            <div className="relative flex justify-between items-center">
                {/* Connecting Line */}
                <div className="absolute top-1/2 left-0 w-full h-1 bg-cyber-border -z-10 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-cyber-primary transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(0,240,255,0.5)]"
                        style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
                    />
                </div>

                {steps.map((step, index) => {
                    const isActive = index === currentStep;
                    const isCompleted = index < currentStep;
                    const isPending = index > currentStep;

                    return (
                        <div key={step.id} className="flex flex-col items-center gap-2 relative group">
                            <div
                                className={`
                  w-12 h-12 rounded-full flex items-center justify-center text-xl
                  transition-all duration-500 border-2
                  ${isActive
                                        ? 'bg-cyber-primary/20 border-cyber-primary text-cyber-primary scale-110 shadow-[0_0_20px_rgba(0,240,255,0.4)] animate-pulse'
                                        : isCompleted
                                            ? 'bg-cyber-primary border-cyber-primary text-white'
                                            : 'bg-cyber-card border-cyber-border text-cyber-muted'
                                    }
                `}
                            >
                                {isCompleted ? '✓' : step.icon}
                            </div>

                            <span
                                className={`
                  text-xs font-mono font-bold tracking-wider uppercase
                  transition-colors duration-300
                  ${isActive || isCompleted ? 'text-cyber-primary' : 'text-cyber-muted'}
                `}
                            >
                                {step.label}
                            </span>

                            {/* Active Step Glow */}
                            {isActive && (
                                <div className="absolute inset-0 bg-cyber-primary/20 blur-xl rounded-full -z-10 animate-pulse" />
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default ProcessingSteps;
