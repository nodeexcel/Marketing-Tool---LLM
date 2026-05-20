import React from 'react';
import { marked } from 'marked';
import {
    Telescope, Target, ListChecks, Sparkles, Layout, TrendingUp,
    AlertTriangle, CheckCircle2, Lightbulb, Mail, MessageSquare,
} from 'lucide-react';

type Analysis = {
    hook?: string;
    pain_points?: string[];
    persuasion_patterns?: string[];
    primary_cta?: string;
    tone_summary?: string;
    structural_notes?: string[];
    strengths?: string[];
    weaknesses?: string[];
};

type Variation = {
    variation_name?: string;
    subject_line?: string | null;
    content?: string;
    rationale?: string;
};

interface CompetitorIntelligenceOutputProps {
    data: {
        competitor_name?: string | null;
        content_type?: string;
        analysis?: Analysis;
        rewritten_variations?: Variation[];
        key_insights?: string[];
    };
    compact?: boolean;
}

const card: React.CSSProperties = {
    background: 'var(--bg-secondary)',
    border: '1px solid var(--border-default)',
    borderRadius: 16,
    padding: 20,
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
};

const sectionLabel: React.CSSProperties = {
    fontSize: 11,
    fontWeight: 900,
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
};

const bullet = (text: string, color = 'var(--primary)') => (
    <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
        <div style={{
            marginTop: 7, width: 6, height: 6, borderRadius: '50%',
            background: color, flexShrink: 0,
        }} />
        <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.55 }}>{text}</span>
    </div>
);

const labeledList = (label: string, items: string[] | undefined, color = 'var(--primary)') => {
    if (!items || items.length === 0) return null;
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <span style={sectionLabel}>{label}</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {items.map((s, i) => <React.Fragment key={i}>{bullet(s, color)}</React.Fragment>)}
            </div>
        </div>
    );
};

const CompactView: React.FC<{
    analysis: Analysis;
    variations: Variation[];
    insights: string[];
    isEmailLike: boolean;
}> = ({ analysis, variations, insights, isEmailLike }) => {
    const topPain = (analysis.pain_points || []).slice(0, 3);
    const topPersuasion = (analysis.persuasion_patterns || []).slice(0, 3);
    const topInsights = insights.slice(0, 2);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {analysis.hook && (
                <div style={{
                    padding: '10px 12px',
                    background: 'rgba(124,92,255,0.08)',
                    borderRadius: 10,
                    borderLeft: '3px solid var(--primary)',
                }}>
                    <span style={sectionLabel}>Hook</span>
                    <p style={{ margin: '4px 0 0', fontSize: 12.5, color: 'var(--text-primary)', lineHeight: 1.45 }}>
                        {analysis.hook}
                    </p>
                </div>
            )}

            {(topPain.length > 0 || topPersuasion.length > 0) && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
                    {topPain.length > 0 && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            <span style={sectionLabel}>Pain Points</span>
                            {topPain.map((s, i) => (
                                <div key={i} style={{ display: 'flex', gap: 6, fontSize: 11.5, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                                    <span style={{ color: '#ef4444' }}>•</span>
                                    <span>{s}</span>
                                </div>
                            ))}
                        </div>
                    )}
                    {topPersuasion.length > 0 && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            <span style={sectionLabel}>Persuasion</span>
                            {topPersuasion.map((s, i) => (
                                <div key={i} style={{ display: 'flex', gap: 6, fontSize: 11.5, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                                    <span style={{ color: 'var(--primary)' }}>•</span>
                                    <span>{s.length > 90 ? s.slice(0, 90) + '…' : s}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {variations.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <span style={sectionLabel}>Rewrites ({variations.length})</span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {variations.map((v, i) => (
                            <span key={i} style={{
                                padding: '3px 8px',
                                borderRadius: 999,
                                background: 'rgba(124,92,255,0.12)',
                                color: 'var(--primary)',
                                fontSize: 11,
                                fontWeight: 700,
                            }}>
                                {v.variation_name || `Variation ${i + 1}`}
                                {isEmailLike && v.subject_line ? ` · ${v.subject_line.slice(0, 40)}${v.subject_line.length > 40 ? '…' : ''}` : ''}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {topInsights.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <span style={sectionLabel}>Key Insights</span>
                    {topInsights.map((s, i) => (
                        <div key={i} style={{ display: 'flex', gap: 6, fontSize: 11.5, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                            <span style={{ color: '#22c55e' }}>•</span>
                            <span>{s.length > 140 ? s.slice(0, 140) + '…' : s}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export const CompetitorIntelligenceOutput: React.FC<CompetitorIntelligenceOutputProps> = ({ data, compact = false }) => {
    if (!data) return null;
    const analysis: Analysis = data.analysis || {};
    const variations: Variation[] = data.rewritten_variations || [];
    const insights: string[] = data.key_insights || [];
    const competitorName = data.competitor_name && data.competitor_name !== 'Unknown' ? data.competitor_name : null;
    const isEmailLike = (data.content_type || 'email') === 'email' || data.content_type === 'sms';

    if (compact) {
        return <CompactView analysis={analysis} variations={variations} insights={insights} isEmailLike={isEmailLike} />;
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Header */}
            <div style={{
                ...card,
                background: 'linear-gradient(135deg, rgba(124,92,255,0.08), rgba(34,197,94,0.06))',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                        width: 44, height: 44, borderRadius: 12,
                        background: 'linear-gradient(135deg, #7c5cff, #5b8cff)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 6px 16px rgba(124,92,255,0.35)',
                        flexShrink: 0,
                    }}>
                        <Telescope size={22} color="#ffffff" strokeWidth={2.2} />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={sectionLabel}>Competitor Intelligence</span>
                        <span style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)' }}>
                            {competitorName ? `Analyzing ${competitorName}` : 'Analysis & Rewrites'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Analysis */}
            {(analysis.hook || analysis.primary_cta || analysis.tone_summary ||
              analysis.pain_points?.length || analysis.persuasion_patterns?.length ||
              analysis.structural_notes?.length || analysis.strengths?.length || analysis.weaknesses?.length) ? (
                <div style={card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <ListChecks size={16} color="var(--primary)" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>Analysis</span>
                    </div>

                    {analysis.hook && (
                        <div style={{
                            padding: '12px 16px',
                            background: 'rgba(124,92,255,0.06)',
                            borderRadius: 10,
                            borderLeft: '3px solid var(--primary)',
                        }}>
                            <span style={sectionLabel}>Hook</span>
                            <p style={{ margin: '6px 0 0', fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.55 }}>
                                {analysis.hook}
                            </p>
                        </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
                        {analysis.primary_cta && (
                            <div>
                                <span style={sectionLabel}>Primary CTA</span>
                                <p style={{ margin: '6px 0 0', fontSize: 14, color: 'var(--text-primary)', fontWeight: 700 }}>
                                    {analysis.primary_cta}
                                </p>
                            </div>
                        )}
                        {analysis.tone_summary && (
                            <div>
                                <span style={sectionLabel}>Tone</span>
                                <p style={{ margin: '6px 0 0', fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                                    {analysis.tone_summary}
                                </p>
                            </div>
                        )}
                    </div>

                    {labeledList('Pain Points Targeted', analysis.pain_points, '#ef4444')}
                    {labeledList('Persuasion Patterns', analysis.persuasion_patterns, '#7c5cff')}
                    {labeledList('Structural Notes', analysis.structural_notes, '#22c55e')}

                    {(analysis.strengths?.length || analysis.weaknesses?.length) ? (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
                            {analysis.strengths?.length ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <CheckCircle2 size={14} color="#22c55e" />
                                        <span style={sectionLabel}>Strengths</span>
                                    </div>
                                    {analysis.strengths.map((s, i) => <React.Fragment key={i}>{bullet(s, '#22c55e')}</React.Fragment>)}
                                </div>
                            ) : null}
                            {analysis.weaknesses?.length ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <AlertTriangle size={14} color="#f59e0b" />
                                        <span style={sectionLabel}>Weaknesses</span>
                                    </div>
                                    {analysis.weaknesses.map((s, i) => <React.Fragment key={i}>{bullet(s, '#f59e0b')}</React.Fragment>)}
                                </div>
                            ) : null}
                        </div>
                    ) : null}
                </div>
            ) : null}

            {/* Rewritten Variations */}
            {variations.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, paddingLeft: 4 }}>
                        <Sparkles size={16} color="var(--primary)" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>
                            Rewritten for Your Brand ({variations.length})
                        </span>
                    </div>
                    {variations.map((v, idx) => (
                        <div key={idx} style={card}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                                <span style={{
                                    padding: '4px 10px', borderRadius: 999,
                                    background: 'rgba(124,92,255,0.15)',
                                    color: 'var(--primary)',
                                    fontSize: 11, fontWeight: 900,
                                    textTransform: 'uppercase', letterSpacing: '0.05em',
                                }}>
                                    {idx + 1}. {v.variation_name || `Variation ${idx + 1}`}
                                </span>
                                {isEmailLike && v.subject_line && (
                                    <span style={{
                                        display: 'inline-flex', alignItems: 'center', gap: 6,
                                        fontSize: 13, color: 'var(--text-secondary)',
                                    }}>
                                        {data.content_type === 'sms'
                                            ? <MessageSquare size={12} />
                                            : <Mail size={12} />}
                                        <strong style={{ color: 'var(--text-primary)' }}>Subject:</strong> {v.subject_line}
                                    </span>
                                )}
                            </div>
                            {v.content && (
                                <div
                                    style={{ fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.65 }}
                                    dangerouslySetInnerHTML={{ __html: marked.parse(v.content, { breaks: true }) as string }}
                                />
                            )}
                            {v.rationale && (
                                <div style={{
                                    marginTop: 4,
                                    padding: '10px 14px',
                                    background: 'rgba(255,255,255,0.03)',
                                    borderRadius: 10,
                                    fontSize: 12.5,
                                    color: 'var(--text-muted)',
                                    fontStyle: 'italic',
                                    lineHeight: 1.55,
                                }}>
                                    <strong style={{ color: 'var(--text-secondary)', fontStyle: 'normal' }}>Why this works: </strong>
                                    {v.rationale}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Key Insights */}
            {insights.length > 0 && (
                <div style={{
                    ...card,
                    background: 'linear-gradient(135deg, rgba(34,197,94,0.06), rgba(124,92,255,0.04))',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Lightbulb size={16} color="#22c55e" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>Key Insights</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {insights.map((s, i) => <React.Fragment key={i}>{bullet(s, '#22c55e')}</React.Fragment>)}
                    </div>
                </div>
            )}
        </div>
    );
};

export default CompetitorIntelligenceOutput;
