import {
    Compass, Database,
    Fingerprint, Type, Quote, Users, Shield,
    Lightbulb,
    PenTool, Image as ImageIcon, Camera, Layout, Crop, MonitorSmartphone,
    Video, FileVideo, Mic, Tv,
    Pen, MessageCircle, Mail, FileText, Search,
    MessageSquare, Sparkles,
    Telescope, Radar
} from 'lucide-react';

export const AGENT_CATEGORIES = [
    {
        title: 'Brand Identity',
        description: 'Establish and protect brand DNA.',
        color: '#ff6b6b',
        agents: [
            { name: 'Brand Identity Builder', id: 'brand_identity', icon: Fingerprint, desc: 'Defines core brand values, visual style, and voice.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Brand Naming', id: 'brand_naming', icon: Type, desc: 'Generates creative brand name options.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Tagline & Slogan', id: 'tagline_slogan', icon: Quote, desc: 'Crafts catchy brand slogans.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Target Audience', id: 'target_audience', icon: Users, desc: 'Analyzes consumer demographics and personas.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Brand Voice Analyzer', id: 'brand_voice', icon: Mic, desc: 'Extracts brand tone and personality from content.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Brand Guardian', id: 'brand_guardian', icon: Shield, desc: 'Ensures content matches brand guidelines.', badge: undefined, outputMode: 'structured-text' }
        ]
    },
    {
        title: 'Creative Strategy',
        description: 'High-level campaign ideation.',
        color: '#feca57',
        agents: [
            { name: 'Creative Direction', id: 'creative_direction', icon: Compass, desc: 'Sets visual and mood direction for campaigns.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Campaign Concept', id: 'campaign_concept', icon: Lightbulb, desc: 'Develops specific marketing themes.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Content Calendar', id: 'content_calendar', icon: Database, desc: 'Plans a strategic content schedule.', badge: undefined, outputMode: 'structured-text' }
        ]
    },
    {
        title: 'Visual Design',
        description: 'Graphics and imagery.',
        color: 'var(--accent-2)',
        agents: [
            { name: 'Logo Designer', id: 'logo_designer', icon: PenTool, desc: 'Creates professional logo variations.', badge: undefined, outputMode: 'image' },
            { name: 'Image Generator', id: 'hero_image', icon: ImageIcon, desc: 'Creates high-impact banner visuals.', badge: undefined, outputMode: 'image' },
            { name: 'Product Photoshoot', id: 'product_photoshoot', icon: Camera, desc: 'High-end product photography.', badge: undefined, outputMode: 'image' },
            { name: 'Ad Creative Designer', id: 'ad_creative', icon: Layout, desc: 'Designs platform-specific visuals.', badge: undefined, outputMode: 'image' },
            { name: 'Image Editor', id: 'image_editor', icon: Crop, desc: 'Sophisticated AI image editing.', badge: undefined, outputMode: 'image' },
            { name: 'Mockup Generator', id: 'mockup_generator', icon: MonitorSmartphone, desc: 'Device and product mockups.', badge: undefined, outputMode: 'image' },
            { name: 'Infographic Generator', id: 'infographic', icon: Database, desc: 'Visualizes data and concepts.', badge: undefined, outputMode: 'image' },
        ]
    },
    {
        title: 'Social Media',
        description: 'Engagement-focused platform content.',
        color: '#ff9ff3',
        agents: [
            { name: 'IG Post', id: 'instagram_post', icon: ImageIcon, desc: 'Optimized Instagram grid posts.', badge: undefined, outputMode: 'text+image+video' },
            { name: 'IG Story', id: 'instagram_story', icon: Sparkles, desc: 'Interactive Instagram stories.', badge: undefined, outputMode: 'text+image+video' },
            { name: 'IG Reel', id: 'instagram_reel', icon: Video, desc: 'Short-form Instagram video scripts.', badge: undefined, outputMode: 'text+video' },
            { name: 'IG Carousel', id: 'instagram_carousel', icon: Layout, desc: 'Multi-slide Instagram content.', badge: undefined, outputMode: 'text+image' },
            { name: 'IG Bio', id: 'instagram_bio', icon: Pen, desc: 'SEO-optimized profile bio.', badge: undefined, outputMode: 'text' },
            { name: 'FB Post', id: 'facebook_post', icon: MessageSquare, desc: 'Engagement Facebook posts.', badge: undefined, outputMode: 'text+image+video' },
            { name: 'FB Ad Copy', id: 'facebook_ad_copy', icon: Pen, desc: 'High-converting Facebook ads.', badge: undefined, outputMode: 'text+image' },
        ]
    },
    {
        title: 'Video & Motion',
        description: 'Dynamic visual storytelling.',
        color: '#ff9ff3',
        agents: [
            { name: 'Video Ad Script', id: 'video_ad_script', icon: Tv, desc: 'Commercial video scripting.', badge: undefined, outputMode: 'text+video' },
            { name: 'YouTube Script', id: 'youtube_script', icon: FileVideo, desc: 'Long-form video content.', badge: undefined, outputMode: 'text' },
            { name: 'AI Video Creator', id: 'ai_video_gen', icon: Video, desc: 'Text-to-video generation.', badge: undefined, outputMode: 'video' },
            { name: 'Thumbnail Idea', id: 'thumbnail_idea', icon: ImageIcon, desc: 'CTR-optimized visuals.', badge: undefined, outputMode: 'text+image' },
        ]
    },
    {
        title: 'Content & Copy',
        description: 'Expert writing services.',
        color: '#48dbfb',
        agents: [
            { name: 'Blog Post', id: 'blog_post', icon: FileText, desc: 'SEO-rich long-form articles.', badge: undefined, outputMode: 'text' },
            { name: 'Email Campaign', id: 'email_campaign', icon: Mail, desc: 'Personalized sequences.', badge: undefined, outputMode: 'text' },
            { name: 'Newsletter', id: 'newsletter', icon: MessageCircle, desc: 'Engaging weekly updates.', badge: undefined, outputMode: 'text' },
            { name: 'Landing Page', id: 'landing_page', icon: Layout, desc: 'Conversion-focused web copy.', badge: undefined, outputMode: 'text' },
            { name: 'Product Description', id: 'product_description', icon: Pen, desc: 'E-commerce copy.', badge: undefined, outputMode: 'text' },
            { name: 'FAQ Generator', id: 'faq_generator', icon: MessageSquare, desc: 'Customer support content.', badge: undefined, outputMode: 'structured-text' },
            { name: 'SMS Marketing', id: 'sms_marketing', icon: MessageSquare, desc: 'Concise mobile copy.', badge: undefined, outputMode: 'text' },
        ]
    },
    {
        title: 'Advertising Copy',
        description: 'Multi-platform ad expert.',
        color: '#ff6b6b',
        agents: [
            { name: 'Meta Ads', id: 'meta_ads', icon: Pen, desc: 'FB/IG marketing specialist.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Google Search Ads', id: 'google_search_ads', icon: Search, desc: 'PPC search specialist.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Google Display Ads', id: 'google_display_ads', icon: ImageIcon, desc: 'Visual ad copy.', badge: undefined, outputMode: 'structured-text' },
            { name: 'YouTube Ads', id: 'youtube_ads', icon: Tv, desc: 'Pre-roll and in-feed ads.', badge: undefined, outputMode: 'structured-text' },
        ]
    },
    {
        title: 'SEO & AEO',
        description: 'Search and Answer engine optimization.',
        color: '#1dd1a1',
        agents: [
            { name: 'Keyword Researcher', id: 'keyword_researcher', icon: Search, desc: 'Strategic keyword analysis.', badge: undefined, outputMode: 'structured-text' },
            { name: 'On-page SEO', id: 'on_page_seo', icon: FileText, desc: 'HTML and content optimization.', badge: undefined, outputMode: 'structured-text' },
            { name: 'Technical SEO', id: 'technical_seo', icon: Database, desc: 'Site structure and speed fixes.', badge: undefined, outputMode: 'structured-text' },
            { name: 'AEO Optimizer', id: 'aeo_optimizer', icon: Sparkles, desc: 'Optimized for LLMs and Voice.', badge: undefined, outputMode: 'structured-text' }
        ]
    },
    {
        title: 'Intelligence',
        description: 'Competitive and trend analysis.',
        color: '#00d2d3',
        agents: [
            { name: 'Competitor Intelligence', id: 'competitor_intelligence', icon: Telescope, desc: 'Analyzes competitor copy and rewrites it in your brand voice.', badge: 'New', outputMode: 'structured-text' },
            { name: 'Trend Scanner', id: 'trend_scanner', icon: Radar, desc: 'Scans a niche for trending themes, hooks, and content formats.', badge: 'New', outputMode: 'structured-text' },
        ]
    }
];
