import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function MarkdownPreview({ data = {}, confidence = {} }) {
    const generateMarkdown = () => {
        if (!data || Object.keys(data).length === 0) {
            return '# 暫無數據\n\n等待 OCR 處理完成...';
        }

        let md = '# 申請表識別結果\n\n';

        // Group fields
        const sections = {
            '申請人基本資料': [],
            '就業資料': [],
            '家庭資料': [],
            '財務資料': [],
            '申請資料': [],
            '其他資料': []
        };

        Object.keys(data).forEach(key => {
            const value = data[key];
            const conf = confidence[key] || 0;
            const confStr = conf > 0 ? `${(conf * 100).toFixed(0)}%` : 'N/A';

            if (key.includes('applicant') || key.includes('name') || key.includes('hkid') || key.includes('address')) {
                sections['申請人基本資料'].push({ key, value, confStr });
            } else if (key.includes('employ') || key.includes('income') || key.includes('occupation')) {
                sections['就業資料'].push({ key, value, confStr });
            } else if (key.includes('family') || key.includes('member') || key.includes('marital')) {
                sections['家庭資料'].push({ key, value, confStr });
            } else if (key.includes('rent') || key.includes('asset') || key.includes('debt')) {
                sections['財務資料'].push({ key, value, confStr });
            } else if (key.includes('application') || key.includes('purpose')) {
                sections['申請資料'].push({ key, value, confStr });
            } else {
                sections['其他資料'].push({ key, value, confStr });
            }
        });

        Object.keys(sections).forEach(section => {
            if (sections[section].length > 0) {
                md += `## ${section}\n\n`;
                md += '| 字段 | 內容 | 置信度 |\n';
                md += '|------|------|--------|\n';
                sections[section].forEach(({ key, value, confStr }) => {
                    const displayValue = value || 'N/A';
                    md += `| ${key} | ${displayValue} | ${confStr} |\n`;
                });
                md += '\n';
            }
        });

        return md;
    };

    return (
        <div className="prose dark:prose-invert max-w-none">
            <ReactMarkdown>{generateMarkdown()}</ReactMarkdown>
        </div>
    );
}
