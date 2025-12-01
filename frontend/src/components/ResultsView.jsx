import React, { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getBatch, updateBatch, exportBatch } from '../api';
import FieldEditor from './FieldEditor';
import MarkdownPreview from './MarkdownPreview';
import ProcessingSteps from './ProcessingSteps';

const ResultsView = () => {
    const { id } = useParams();
    const [batch, setBatch] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedImageIndex, setSelectedImageIndex] = useState(0);
    const [activeTab, setActiveTab] = useState('fields'); // fields, markdown, csv
    const [saving, setSaving] = useState(false);

    const apiBaseUrl = useMemo(() => import.meta.env.VITE_API_URL || 'http://localhost:8000', []);

    useEffect(() => {
        const fetchBatch = async () => {
            try {
                const data = await getBatch(id);
                setBatch(data);

                // Poll if processing
                if (data.status === 'processing' || data.status === 'pending') {
                    setTimeout(fetchBatch, 2000);
                }
            } catch (error) {
                console.error("Failed to fetch batch:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchBatch();
    }, [id]);

    const handleUpdate = async () => {
        if (!batch || !batch.images[selectedImageIndex]) return;

        setSaving(true);
        try {
            const currentImage = batch.images[selectedImageIndex];
            // In a real app, you'd update the specific image's data
            // Here we assume the backend handles the update for the batch
            await updateBatch(id, { data: currentImage.ocr_data });
            alert("Saved successfully!");
        } catch (error) {
            console.error("Update failed:", error);
            alert("Failed to save");
        } finally {
            setSaving(false);
        }
    };

    const handleFieldChange = (newData) => {
        if (!batch) return;

        const newBatch = { ...batch };
        newBatch.images[selectedImageIndex].ocr_data = newData;
        setBatch(newBatch);
    };

    const handleExport = async (format) => {
        try {
            await exportBatch(id, format);
            alert(`Exported to ${format.toUpperCase()}`);
        } catch (error) {
            console.error("Export failed:", error);
            alert("Export failed");
        }
    };

    if (loading || !batch) {
        return (
            <div className="min-h-screen bg-cyber-black flex items-center justify-center">
                <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-cyber-primary"></div>
            </div>
        );
    }

    const currentImage = batch.images[selectedImageIndex];

    const getImageUrl = (filePath) => {
        if (!filePath) return '';
        if (filePath.startsWith('http')) return filePath;
        return `${apiBaseUrl}${filePath.startsWith('/') ? filePath : `/${filePath}`}`;
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'pending':
                return 'bg-cyber-muted/20 text-cyber-muted';
            case 'processing':
                return 'bg-cyber-primary/20 text-cyber-primary';
            case 'done':
                return 'bg-green-500/20 text-green-400';
            case 'error':
                return 'bg-red-500/20 text-red-400';
            default:
                return 'bg-cyber-muted/20 text-cyber-muted';
        }
    };

    const overallConfidence = (confidenceObj) => {
        if (!confidenceObj || typeof confidenceObj !== 'object') return null;
        const vals = Object.values(confidenceObj).filter(v => typeof v === 'number');
        if (!vals.length) return null;
        const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
        return (avg * 100).toFixed(1);
    };

    return (
        <div className="min-h-screen bg-cyber-black text-cyber-text p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <Link to="/" className="text-cyber-muted hover:text-cyber-primary transition-colors flex items-center gap-2">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        Back to Upload
                    </Link>
                    <div className="flex items-center gap-4">
                        <span className={`px-3 py-1 rounded-full text-sm font-mono ${getStatusBadge(batch.status)}`}>
                            {batch.status?.toUpperCase?.() || 'UNKNOWN'}
                        </span>
                        <button
                            onClick={() => handleExport('csv')}
                            className="px-4 py-2 bg-cyber-card border border-cyber-border rounded-lg hover:border-cyber-primary/50 transition-all"
                        >
                            Export CSV
                        </button>
                        <button
                            onClick={handleUpdate}
                            disabled={saving}
                            className="px-4 py-2 bg-cyber-primary text-cyber-black rounded-lg font-bold hover:shadow-[0_0_15px_rgba(0,240,255,0.4)] transition-all"
                        >
                            {saving ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </div>

                {/* Processing Steps Visualization */}
                <ProcessingSteps status={batch.status} />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
                    {/* Left Panel: Image Viewer */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="glass-panel rounded-xl p-4 sticky top-6">
                            <h2 className="text-xl font-bold mb-4 text-cyber-primary flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                Original Image
                            </h2>

                            {currentImage && (
                                <div className="relative group rounded-lg overflow-hidden border border-cyber-border">
                                    <img
                                        src={getImageUrl(currentImage.file_path)}
                                        alt={`Page ${selectedImageIndex + 1}`}
                                        className="w-full h-auto object-contain"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-cyber-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                                        <p className="text-sm font-mono text-cyber-primary">
                                            {overallConfidence(currentImage.confidence) ? `Confidence: ${overallConfidence(currentImage.confidence)}%` : 'Confidence: N/A'}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* Thumbnails */}
                            {batch.images.length > 1 && (
                                <div className="grid grid-cols-4 gap-2 mt-4">
                                    {batch.images.map((img, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setSelectedImageIndex(idx)}
                                            className={`relative aspect-square rounded-lg overflow-hidden border-2 transition-all ${selectedImageIndex === idx
                                                    ? 'border-cyber-primary shadow-[0_0_10px_rgba(0,240,255,0.3)]'
                                                    : 'border-cyber-border hover:border-cyber-muted'
                                                }`}
                                        >
                                            <img
                                                src={getImageUrl(img.file_path)}
                                                alt={`Page ${idx + 1}`}
                                                className="w-full h-full object-cover"
                                            />
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Panel: Data & Results */}
                    <div className="lg:col-span-2">
                        <div className="glass-panel rounded-xl overflow-hidden min-h-[600px] flex flex-col">
                            {/* Tabs */}
                            <div className="flex border-b border-cyber-border bg-cyber-dark/50">
                                {[
                                    { id: 'fields', label: 'Structured Data', icon: '📝' },
                                    { id: 'markdown', label: 'Markdown', icon: '📄' },
                                    { id: 'csv', label: 'Raw JSON', icon: '📊' }
                                ].map(tab => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`
                      flex-1 py-4 text-sm font-bold tracking-wider uppercase transition-all
                      flex items-center justify-center gap-2
                      ${activeTab === tab.id
                                                ? 'bg-cyber-primary/10 text-cyber-primary border-b-2 border-cyber-primary'
                                                : 'text-cyber-muted hover:text-cyber-text hover:bg-white/5'}
                    `}
                                    >
                                        <span>{tab.icon}</span>
                                        {tab.label}
                                    </button>
                                ))}
                            </div>

                            {/* Content */}
                            <div className="p-6 flex-1 bg-cyber-card/30">
                                {activeTab === 'fields' && currentImage && (
                                    <FieldEditor
                                        data={currentImage.ocr_data || {}}
                                        confidence={currentImage.confidence || {}}
                                        onChange={handleFieldChange}
                                    />
                                )}

                                {activeTab === 'markdown' && currentImage && (
                                    <MarkdownPreview data={currentImage.ocr_data || {}} confidence={currentImage.confidence || {}} />
                                )}

                                {activeTab === 'csv' && currentImage && (
                                    <div className="bg-cyber-black p-4 rounded-lg border border-cyber-border font-mono text-xs text-cyber-muted overflow-auto max-h-[500px]">
                                        <pre>{JSON.stringify(currentImage.ocr_data, null, 2)}</pre>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResultsView;
