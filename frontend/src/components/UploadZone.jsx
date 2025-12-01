import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { createBatch, getBatch } from '../api';

export default function UploadZone() {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');
    const [formType, setFormType] = useState('GCCF_10K');
    const navigate = useNavigate();

    const onDrop = useCallback(acceptedFiles => {
        setFiles(prev => [...prev, ...acceptedFiles.map(file => Object.assign(file, {
            preview: URL.createObjectURL(file)
        }))]);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'image/*': [] }
    });

    const handleUpload = async () => {
        if (files.length === 0) return;

        setUploading(true);
        try {
            const result = await createBatch(files, formType);
            if (!result || !result.id) {
                throw new Error('Upload succeeded but no batch id returned');
            }

            setUploadStatus('已上傳，正在識別...');

            // 等待處理完成再跳轉，避免 undefined/空白頁
            const batchId = result.id;
            const deadline = Date.now() + 120000; // 最長等 120s
            let latest = result;

            while (Date.now() < deadline) {
                latest = await getBatch(batchId);
                if (latest.status && !['pending', 'processing'].includes(latest.status)) {
                    break;
                }
                await new Promise(r => setTimeout(r, 1500));
            }

            navigate(`/results/${batchId}`);
        } catch (error) {
            console.error("Upload failed:", error);
            alert("上傳失敗，請重試");
        } finally {
            setUploading(false);
            setUploadStatus('');
        }
    };

    const removeFile = (index) => {
        setFiles(files.filter((_, i) => i !== index));
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background Grid */}
            <div className="absolute inset-0 cyber-grid-bg opacity-20 pointer-events-none" />

            <div className="w-full max-w-4xl z-10">
                <div className="text-center mb-12 space-y-4">
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyber-primary via-white to-cyber-secondary animate-float">
                        OCR <span className="font-mono text-cyber-primary">V5.0</span>
                    </h1>
                    <p className="text-cyber-muted text-lg font-light tracking-wide">
                        PP-STRUCTURE V2 INTELLIGENT DOCUMENT PROCESSING
                    </p>
                </div>

                <div className="glass-panel rounded-2xl p-8 md:p-12 relative group">
                    {/* Animated Border Gradient */}
                    <div className="absolute -inset-[1px] bg-gradient-to-r from-cyber-primary via-cyber-secondary to-cyber-primary rounded-2xl opacity-30 group-hover:opacity-100 blur transition duration-1000 animate-pulse-glow -z-10" />

                    {/* Form Type Selector */}
                    <div className="flex justify-center mb-8">
                        <div className="inline-flex bg-cyber-dark/50 p-1 rounded-xl border border-cyber-border/50 backdrop-blur-sm">
                            {['GCCF_10K', 'MGT_BOOK'].map((type) => (
                                <button
                                    key={type}
                                    onClick={() => setFormType(type)}
                                    className={`
                                        px-6 py-2 rounded-lg text-sm font-bold tracking-wider transition-all duration-300
                                        ${formType === type
                                            ? 'bg-cyber-primary text-cyber-black shadow-[0_0_15px_rgba(0,240,255,0.4)]'
                                            : 'text-cyber-muted hover:text-white hover:bg-white/5'}
                                    `}
                                >
                                    {type}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Dropzone */}
                    <div
                        {...getRootProps()}
                        className={`
                            relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300
                            ${isDragActive
                                ? 'border-cyber-primary bg-cyber-primary/10 scale-[1.02]'
                                : 'border-cyber-border hover:border-cyber-primary/50 hover:bg-cyber-card/50'}
                        `}
                    >
                        <input {...getInputProps()} />

                        {/* Scanning Line Animation */}
                        <div className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
                            <div className="w-full h-1 bg-cyber-primary/50 shadow-[0_0_15px_rgba(0,240,255,0.8)] animate-scan" />
                        </div>

                        <div className="space-y-4 relative z-10">
                            <div className="w-20 h-20 mx-auto rounded-full bg-cyber-dark border border-cyber-border flex items-center justify-center group-hover:border-cyber-primary/50 transition-colors">
                                <svg className="w-10 h-10 text-cyber-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                </svg>
                            </div>
                            <div>
                                <p className="text-xl font-medium text-cyber-text">
                                    {isDragActive ? 'Drop files here...' : 'Drag & Drop files'}
                                </p>
                                <p className="text-cyber-muted mt-2">
                                    or <span className="text-cyber-primary cursor-pointer hover:underline">browse</span> to upload
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Previews */}
                    {files.length > 0 && (
                        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                            {files.map((file, index) => (
                                <div key={index} className="relative group">
                                    <img
                                        src={file.preview}
                                        alt={file.name}
                                        className="w-full h-24 object-cover rounded-lg border border-cyber-border group-hover:border-cyber-primary/50 transition-all"
                                    />
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            removeFile(index);
                                        }}
                                        className="absolute -top-2 -right-2 bg-cyber-accent text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-all shadow-lg hover:scale-110"
                                    >
                                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Upload Button */}
                    <div className="mt-8 text-center">
                        <button
                            onClick={handleUpload}
                            disabled={uploading || files.length === 0}
                            className={`
                                px-8 py-3 rounded-lg font-bold tracking-wider uppercase transition-all duration-300
                                ${uploading || files.length === 0
                                    ? 'bg-cyber-dark text-cyber-muted cursor-not-allowed border border-cyber-border'
                                    : 'bg-cyber-primary text-cyber-black hover:shadow-[0_0_20px_rgba(0,240,255,0.6)] hover:scale-105'}
                            `}
                        >
                            {uploading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    {uploadStatus || 'Processing...'}
                                </span>
                            ) : (
                                'Start Processing'
                            )}
                        </button>
                        {uploadStatus && (
                            <p className="mt-3 text-sm text-cyber-muted">{uploadStatus}</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
