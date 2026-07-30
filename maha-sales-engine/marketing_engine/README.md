# MAHA SALES ENGINE V1 - AI Marketing Engine

## Overview

The AI Marketing Engine automatically generates high-converting marketing assets for every digital product.

## Supported Content Types

- SEO Titles
- SEO Descriptions
- Product Titles
- Subtitles
- Product Descriptions
- Short Descriptions
- Long Sales Pages
- Feature Lists
- Benefits
- Call To Action
- Keywords
- Tags
- Hashtags
- Meta Description
- OpenGraph Metadata
- Twitter Card Metadata
- Schema.org JSON-LD
- FAQ
- Release Notes
- Email Campaign Copy
- Blog Articles
- Landing Page Copy
- Social Media Posts
- Video Scripts
- YouTube Description
- Pinterest Description
- Reddit Summary
- LinkedIn Post
- Facebook Post
- Instagram Caption
- TikTok Caption
- X (Twitter) Thread
- Newsletter Copy
- Product Comparison
- Customer Persona
- Pain Points
- Value Proposition
- USP
- Objection Handling
- Frequently Asked Questions

## Architecture

```
Marketing Engine
├── AI Provider Abstraction (OpenAI, Claude, Gemini, etc.)
├── Prompt Library (Versioned templates)
├── Content Pipeline (State machine)
├── SEO Engine
├── Keyword Engine
├── Content Quality Engine
├── Brand Engine
├── Localization Engine
├── A/B Testing Engine
├── Asset Generation Engine
├── Event Bus
├── Job Queue
└── REST API
```

## Content Pipeline

```
Product
    ↓
Research
    ↓
Keyword Discovery
    ↓
Audience Analysis
    ↓
Competitor Analysis
    ↓
Content Planning
    ↓
Generation
    ↓
Quality Review
    ↓
SEO Optimization
    ↓
Compliance Review
    ↓
Ready
```

## Content Status Lifecycle

```
Draft → Researching → Generating → Reviewing → Optimizing → Approved
                    ↓                                    ↓
                  Failed ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
                    ↓
                  Retrying
```

## AI Providers

- OpenAI
- Claude
- Gemini
- DeepSeek
- Qwen
- Ollama
- Custom Provider

## Supported Languages

10 languages:
- English
- Indonesian
- Chinese
- Spanish
- Arabic
- Hindi
- Thai
- Vietnamese
- Portuguese
- Russian

## API Endpoints

### Generation
- `POST /api/v1/generate` - Generate marketing package
- `POST /api/v1/generate/seo` - Generate SEO assets
- `POST /api/v1/generate/keywords` - Generate keywords
- `POST /api/v1/generate/faq` - Generate FAQ
- `POST /api/v1/generate/landing-page` - Generate landing page
- `POST /api/v1/generate/email` - Generate email campaign
- `POST /api/v1/generate/social` - Generate social media content
- `POST /api/v1/generate/metadata` - Generate marketing metadata
- `POST /api/v1/generate/blog` - Generate blog article
- `POST /api/v1/generate/release-notes` - Generate release notes
- `POST /api/v1/generate/persona` - Generate customer persona
- `POST /api/v1/generate/competitor-analysis` - Generate competitor analysis

### Content Management
- `GET /api/v1/assets` - List marketing assets
- `GET /api/v1/assets/{id}` - Get asset details
- `POST /api/v1/assets/{id}/approve` - Approve/reject content
- `GET /api/v1/assets/{id}/versions` - Get version history

### Brand Management
- `POST /api/v1/brand` - Create brand rules
- `GET /api/v1/brand/{name}` - Get brand rules

### A/B Testing
- `POST /api/v1/ab-tests` - Create A/B test
- `GET /api/v1/ab-tests/{id}` - Get A/B test

### Localization
- `POST /api/v1/localize` - Localize content
- `GET /api/v1/localize/{id}` - Get localized content

### Assets
- `POST /api/v1/assets/generate` - Generate asset specification

### Prompts
- `GET /api/v1/prompts` - List prompt templates

### Jobs
- `GET /api/v1/jobs/{id}` - Get job status
- `GET /api/v1/jobs/queue/stats` - Queue statistics

## Documentation

- [MARKETING_ENGINE.md](MARKETING_ENGINE.md) - Main documentation
- [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md) - Prompt library guide
- [SEO_ENGINE.md](SEO_ENGINE.md) - SEO engine guide
- [CONTENT_PIPELINE.md](CONTENT_PIPELINE.md) - Pipeline guide
- [BRAND_ENGINE.md](BRAND_ENGINE.md) - Brand engine guide
- [LOCALIZATION.md](LOCALIZATION.md) - Localization guide
- [AB_TESTING.md](AB_TESTING.md) - A/B testing guide

## Next Steps

- Phase 6: Sales Analytics
- Phase 7: Payment Settlement
- Phase 8: Customer Support AI