import React from 'react';
import {
    Radar, TrendingUp, Sparkles, Layout, AlertTriangle, Lightbulb,
    Target, Clock, ListChecks,
} from 'lucide-react';

type Theme = {
    theme?: string;
    why_now?: string;
    evidence_count?: number;
    example_hooks?: string[];
};

type Hook = {
    hook_pattern?: string;
    examples?: string[];
    when_to_use?: string;
};

type Format = {
    format_name?: string;
    why_trending?: string;
    examples?: string[];
};

type Gap = {
    opportunity?: string;
    why_underserved?: string;
    angle_for_user?: string;
};

interface TrendScannerOutputProps {
    data: {
        niche?: string;
        time_horizon?: string;
        sources_analyzed?: number;
        summary?: string;
        trending_themes?: Theme[];
        recurring_hooks?: Hook[];
        content_formats?: Format[];
        saturated_angles?: string[];
        gaps_and_opportunities?: Gap[];
        recommended_actions?: string[];
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

const CompactView: React.FC<TrendScannerOutputProps['data']> = (data) => {
    const themes = (data.trending_themes || []).slice(0, 3);
    const formats = (data.content_formats || []).slice(0, 2);
    const opportunities = (data.gaps_and_opportunities || []).slice(0, 2);
    const actions = (data.recommended_actions || []).slice(0, 3);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {data.summary && (
                <div style={{
                    padding: '10px 12px',
                    background: 'rgba(124,92,255,0.08)',
                    borderRadius: 10,
                    borderLeft: '3px solid var(--primary)',
                    fontSize: 12.5, color: 'var(--text-primary)', lineHeight: 1.5,
                }}>
                    {data.summary}
                </div>
            )}

            {themes.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <span style={sectionLabel}>Top Themes</span>
                    {themes.map((t, i) => (
                        <div key={i} style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                            <span style={{ color: 'var(--primary)' }}>•</span> <strong style={{ color: 'var(--text-primary)' }}>{t.theme}</strong>
                            {t.evidence_count ? <span style={{ color: 'var(--text-muted)' }}> · {t.evidence_count} sources</span> : null}
                        </div>
                    ))}
                </div>
            )}

            {(formats.length > 0 || opportunities.length > 0) && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
                    {formats.length > 0 && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            <span style={sectionLabel}>Formats</span>
                            {formats.map((f, i) => (
                                <div key={i} style={{ fontSize: 11.5, color: 'var(--text-secondary)' }}>
                                    • {f.format_name}
                                </div>
                            ))}
                        </div>
                    )}
                    {opportunities.length > 0 && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                            <span style={sectionLabel}>Gaps</span>
                            {opportunities.map((g, i) => (
                                <div key={i} style={{ fontSize: 11.5, color: 'var(--text-secondary)' }}>
                                    • {g.opportunity}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {actions.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <span style={sectionLabel}>Next Moves</span>
                    {actions.map((a, i) => (
                        <div key={i} style={{ fontSize: 11.5, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                            <span style={{ color: '#22c55e' }}>→</span> {a}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export const TrendScannerOutput: React.FC<TrendScannerOutputProps> = ({ data, compact = false }) => {
    if (!data) return null;
    if (compact) return <CompactView {...data} />;

    const themes = data.trending_themes || [];
    const hooks = data.recurring_hooks || [];
    const formats = data.content_formats || [];
    const saturated = data.saturated_angles || [];
    const gaps = data.gaps_and_opportunities || [];
    const actions = data.recommended_actions || [];
    const insights = data.key_insights || [];

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
                        background: 'linear-gradient(135deg, #7c5cff, #22c55e)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 6px 16px rgba(124,92,255,0.35)',
                        flexShrink: 0,
                    }}>
                        <Radar size={22} color="#ffffff" strokeWidth={2.2} />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={sectionLabel}>Trend Scanner</span>
                        <span style={{ fontSize: 18, fontWeight: 800, color: 'var(--text-primary)' }}>
                            {data.niche || 'Niche Scan'}
                        </span>
                        {(data.sources_analyzed || data.time_horizon) && (
                            <span style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
                                {data.sources_analyzed ? <>{data.sources_analyzed} sources</> : null}
                                {data.time_horizon && (
                                    <>
                                        {data.sources_analyzed ? ' · ' : null}
                                        <Clock size={12} /> {data.time_horizon.replace('_', ' ')}
                                    </>
                                )}
                            </span>
                        )}
                    </div>
                </div>
                {data.summary && (
                    <p style={{ margin: 0, fontSize: 14, color: 'var(--text-primary)', lineHeight: 1.55 }}>
                        {data.summary}
                    </p>
                )}
            </div>

            {/* Trending Themes */}
            {themes.length > 0 && (
                <div style={card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <TrendingUp size={16} color="var(--primary)" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>
                            Trending Themes ({themes.length})
                        </span>
                    </div>
                    {themes.map((t, i) => (
                        <div key={i} style={{
                            padding: '12px 14px',
                            background: 'rgba(255,255,255,0.03)',
                            borderRadius: 10,
                            borderLeft: '3px solid var(--primary)',
                            display: 'flex', flexDirection: 'column', gap: 8,
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                                <span style={{ fontSize: 14, fontWeight: 800, color: 'var(--text-primary)' }}>{t.theme}</span>
                                {t.evidence_count ? (
                                    <span style={{
                                        padding: '2px 8px', borderRadius: 999,
                                        background: 'rgba(124,92,255,0.12)',
                                        color: 'var(--primary)',
                                        fontSize: 11, fontWeight: 700,
                                    }}>
                                        {t.evidence_count} source{t.evidence_count !== 1 ? 's' : ''}
                                    </span>
                                ) : null}
                            </div>
                            {t.why_now && (
                                <p style={{ margin: 0, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                                    {t.why_now}
                                </p>
                            )}
                            {t.example_hooks && t.example_hooks.length > 0 && (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                    <span style={sectionLabel}>Example Hooks</span>
                                    {t.example_hooks.map((h, j) => (
                                        <div key={j} style={{ fontSize: 12.5, color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                                            "{h}"
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Recurring Hooks */}
            {hooks.length > 0 && (
                <div style={card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Sparkles size={16} color="var(--primary)" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>
                            Recurring Hooks ({hooks.length})
                        </span>
                    </div>
                    {hooks.map((h, i) => (
                        <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 8, paddingTop: i > 0 ? 12 : 0, borderTop: i > 0 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                            <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{h.hook_pattern}</span>
                            {h.examples && h.examples.length > 0 && (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                    {h.examples.map((e, j) => (
                                        <div key={j} style={{ fontSize: 13, color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: 1.5 }}>
                                            • "{e}"
                                        </div>
                                    ))}
                                </div>
                            )}
                            {h.when_to_use && (
                                <span style={{ fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                                    When to use: {h.when_to_use}
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Content Formats */}
            {formats.length > 0 && (
                <div style={card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Layout size={16} color="var(--primary)" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>
                            Content Formats ({formats.length})
                        </span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>
                        {formats.map((f, i) => (
                            <div key={i} style={{
                                padding: 14,
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: 10,
                                display: 'flex', flexDirection: 'column', gap: 6,
                            }}>
                                <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{f.format_name}</span>
                                {f.why_trending && (
                                    <span style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{f.why_trending}</span>
                                )}
                                {f.examples && f.examples.length > 0 && (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 2, marginTop: 4 }}>
                                        {f.examples.map((e, j) => (
                                            <span key={j} style={{ fontSize: 12, color: 'var(--text-muted)' }}>• {e}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Saturated & Gaps side-by-side */}
            {(saturated.length > 0 || gaps.length > 0) && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                    {saturated.length > 0 && (
                        <div style={card}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                <AlertTriangle size={16} color="#f59e0b" />
                                <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>Saturated Angles</span>
                            </div>
                            {saturated.map((s, i) => <React.Fragment key={i}>{bullet(s, '#f59e0b')}</React.Fragment>)}
                        </div>
                    )}
                    {gaps.length > 0 && (
                        <div style={card}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                <Target size={16} color="#22c55e" />
                                <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>Gaps & Opportunities</span>
                            </div>
                            {gaps.map((g, i) => (
                                <div key={i} style={{
                                    padding: '10px 12px',
                                    background: 'rgba(34,197,94,0.04)',
                                    borderRadius: 8,
                                    borderLeft: '2px solid #22c55e',
                                    display: 'flex', flexDirection: 'column', gap: 4,
                                }}>
                                    <span style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)' }}>{g.opportunity}</span>
                                    {g.why_underserved && (
                                        <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>{g.why_underserved}</span>
                                    )}
                                    {g.angle_for_user && (
                                        <span style={{ fontSize: 12, color: '#22c55e', fontStyle: 'italic', marginTop: 4 }}>
                                            Your angle: {g.angle_for_user}
                                        </span>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Recommended Actions */}
            {actions.length > 0 && (
                <div style={{
                    ...card,
                    background: 'linear-gradient(135deg, rgba(34,197,94,0.06), rgba(124,92,255,0.04))',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <ListChecks size={16} color="#22c55e" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>Recommended Actions</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {actions.map((a, i) => (
                            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                                <div style={{
                                    background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                                    color: 'white',
                                    padding: '2px 8px', borderRadius: 6,
                                    fontSize: 11, fontWeight: 900, flexShrink: 0,
                                }}>{i + 1}</div>
                                <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.55 }}>{a}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Key Insights */}
            {insights.length > 0 && (
                <div style={card}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Lightbulb size={16} color="#7c5cff" />
                        <span style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)' }}>Key Insights</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {insights.map((s, i) => <React.Fragment key={i}>{bullet(s, '#7c5cff')}</React.Fragment>)}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TrendScannerOutput;
