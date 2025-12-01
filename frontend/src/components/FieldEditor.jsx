import React from 'react';

export default function FieldEditor({ data = {}, confidence = {}, onChange }) {
    const handleChange = (key, value) => {
        onChange({ ...data, [key]: value });
    };

    const getConfidenceClass = (conf) => {
        if (conf >= 0.8) return 'confidence-high';
        if (conf >= 0.5) return 'confidence-medium';
        return 'confidence-low';
    };

    const getConfidenceBadge = (conf) => {
        if (!conf || conf === 0) return null;
        return (
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getConfidenceClass(conf)}`}>
                {(conf * 100).toFixed(0)}%
            </span>
        );
    };

    // Group fields by section (simple heuristic)
    const groupedFields = {};
    Object.keys(data).forEach(key => {
        let section = '其他';
        if (key.includes('applicant') || key.includes('name') || key.includes('hkid') || key.includes('address')) {
            section = '申請人資料';
        } else if (key.includes('employ') || key.includes('income') || key.includes('occupation')) {
            section = '就業資料';
        } else if (key.includes('family') || key.includes('member') || key.includes('marital')) {
            section = '家庭資料';
        } else if (key.includes('rent') || key.includes('asset') || key.includes('debt')) {
            section = '財務資料';
        } else if (key.includes('application') || key.includes('purpose')) {
            section = '申請資料';
        }

        if (!groupedFields[section]) {
            groupedFields[section] = [];
        }
        groupedFields[section].push(key);
    });

    return (
        <div className="space-y-6">
            {Object.keys(groupedFields).map(section => (
                <div key={section} className="border-b border-gray-200 pb-6 last:border-0">
                    <h3 className="text-lg font-semibold mb-4 text-gray-800">
                        {section}
                    </h3>
                    <div className="space-y-4">
                        {groupedFields[section].map(key => (
                            <div key={key} className="grid grid-cols-1 sm:grid-cols-12 gap-3 sm:gap-4 items-start">
                                <div className="sm:col-span-4 pt-1 sm:pt-2">
                                    <label className="text-sm font-medium text-gray-700 break-words">
                                        {key}
                                    </label>
                                </div>
                                <div className="sm:col-span-6">
                                    <input
                                        type="text"
                                        value={data[key] || ''}
                                        onChange={(e) => handleChange(key, e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-sm sm:text-base"
                                        placeholder="未識別"
                                    />
                                </div>
                                <div className="sm:col-span-2 pt-1 sm:pt-2 flex sm:justify-end">
                                    <div className="min-w-[72px]">{getConfidenceBadge(confidence[key])}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}

            {Object.keys(data).length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    <p className="text-lg">暫無識別結果</p>
                    <p className="text-sm mt-2">請等待 OCR 處理完成</p>
                </div>
            )}
        </div>
    );
}
