#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Generators
Reusable generation workflows for different product types.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger("maha-sales-engine.product-factory.generators")


class ProductGenerator(ABC):
    """Base class for all product generators"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    @abstractmethod
    def generate(self, product_id: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """Generate product package"""
        pass
    
    def _create_product_structure(self, product_id: str, title: str) -> Path:
        """Create standard product folder structure"""
        product_dir = self.output_dir / product_id
        product_dir.mkdir(exist_ok=True)
        
        # Create standard folders
        (product_dir / "product").mkdir(exist_ok=True)
        (product_dir / "preview").mkdir(exist_ok=True)
        (product_dir / "thumbnail").mkdir(exist_ok=True)
        
        return product_dir
    
    def _create_metadata(self, product_id: str, title: str, description: str, category: str, **kwargs) -> Dict[str, Any]:
        """Create product metadata"""
        return {
            "product_id": product_id,
            "title": title,
            "description": description,
            "category": category,
            "version": "1.0.0",
            "author": kwargs.get("author", "MAHA LAKSHMI"),
            "license": kwargs.get("license", "personal"),
            "language": kwargs.get("language", "en"),
            "tags": kwargs.get("tags", []),
            "target_market": kwargs.get("target_market", "global"),
            "price_usd": kwargs.get("price_usd", 0.0),
            "price_idr": kwargs.get("price_idr", 0.0),
            "created_at": kwargs.get("created_at", ""),
            "updated_at": kwargs.get("updated_at", ""),
            "file_count": kwargs.get("file_count", 0),
            "total_size_bytes": kwargs.get("total_size_bytes", 0)
        }
    
    def _save_metadata(self, product_dir: Path, metadata: Dict[str, Any]):
        """Save metadata.json"""
        with open(product_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _save_description(self, product_dir: Path, description: str):
        """Save description.md"""
        with open(product_dir / "description.md", "w", encoding="utf-8") as f:
            f.write(f"# {description}\n\n")
            f.write("## Product Description\n\n")
            f.write("This digital product is part of the MAHA LAKSHMI ecosystem.\n\n")
            f.write("## Features\n\n")
            f.write("- High-quality digital assets\n")
            f.write("- Ready for immediate use\n")
            f.write("- Commercial license available\n\n")
            f.write("## What's Included\n\n")
            f.write("- Digital download package\n")
            f.write("- Usage instructions\n")
            f.write("- License agreement\n")
    
    def _save_license(self, product_dir: Path, license_type: str = "personal"):
        """Save license.txt"""
        licenses = {
            "personal": "PERSONAL USE LICENSE\n\nThis product is licensed for personal use only. You may not resell, redistribute, or use this product for commercial purposes.",
            "commercial": "COMMERCIAL USE LICENSE\n\nThis product is licensed for commercial use. You may use this product in client work, commercial projects, and for revenue-generating activities.",
            "extended": "EXTENDED LICENSE\n\nThis product includes extended rights. You may resell, redistribute, and use this product in unlimited commercial projects.",
            "custom": "CUSTOM LICENSE\n\nPlease refer to the custom license agreement provided with this product."
        }
        
        with open(product_dir / "license.txt", "w", encoding="utf-8") as f:
            f.write(licenses.get(license_type, licenses["personal"]))
    
    def _save_keywords(self, product_dir: Path, keywords: List[str]):
        """Save keywords.json"""
        keywords_data = {
            "keywords": keywords,
            "primary_keywords": keywords[:5],
            "secondary_keywords": keywords[5:15] if len(keywords) > 5 else [],
            "long_tail_keywords": keywords[15:] if len(keywords) > 15 else []
        }
        
        with open(product_dir / "keywords.json", "w", encoding="utf-8") as f:
            json.dump(keywords_data, f, indent=2, ensure_ascii=False)
    
    def _save_pricing(self, product_dir: Path, price_usd: float, price_idr: float):
        """Save pricing.json"""
        pricing = {
            "price_usd": price_usd,
            "price_idr": price_idr,
            "currency": "USD",
            "alternate_currency": "IDR",
            "exchange_rate": 16000,
            "last_updated": "",
            "market_specific_pricing": {
                "id": {"price_idr": price_idr, "currency": "IDR"},
                "en": {"price_usd": price_usd, "currency": "USD"},
                "pt": {"price_usd": price_usd, "currency": "USD"},
                "zh": {"price_usd": price_usd, "currency": "USD"}
            }
        }
        pricing["last_updated"] = ""
        
        with open(product_dir / "pricing.json", "w", encoding="utf-8") as f:
            json.dump(pricing, f, indent=2)
    
    def _save_version(self, product_dir: Path, version: str = "1.0.0"):
        """Save version.json"""
        version_data = {
            "current_version": version,
            "version_history": [
                {
                    "version": version,
                    "created_at": "",
                    "changes": "Initial release",
                    "author": "MAHA LAKSHMI"
                }
            ]
        }
        version_data["version_history"][0]["created_at"] = ""
        
        with open(product_dir / "version.json", "w", encoding="utf-8") as f:
            json.dump(version_data, f, indent=2)
    
    def _save_history(self, product_dir: Path, title: str):
        """Save history.json"""
        history = {
            "product_title": title,
            "creation_date": "",
            "last_modified": "",
            "versions": [],
            "changes": [
                {
                    "date": "",
                    "version": "1.0.0",
                    "changes": "Initial product creation",
                    "author": "MAHA LAKSHMI"
                }
            ]
        }
        history["creation_date"] = ""
        history["last_modified"] = ""
        
        with open(product_dir / "history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)


class EbookGenerator(ProductGenerator):
    """Generate eBook products"""
    
    def generate(self, product_id: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        try:
            product_dir = self._create_product_structure(product_id, title)
            
            # Create PDF content structure
            pdf_dir = product_dir / "product" / "pdf"
            pdf_dir.mkdir(exist_ok=True)
            
            # Create markdown source
            md_content = f"""# {title}

{description}

## Table of Contents

1. Introduction
2. Chapter 1: Getting Started
3. Chapter 2: Core Concepts
4. Chapter 3: Advanced Techniques
5. Chapter 4: Case Studies
6. Chapter 5: Best Practices
7. Conclusion
8. Resources

## Introduction

Welcome to {title}. This eBook will guide you through...

## Chapter 1: Getting Started

In this chapter, we will cover...

## Chapter 2: Core Concepts

Understanding the fundamentals...

## Chapter 3: Advanced Techniques

Take your skills to the next level...

## Chapter 4: Case Studies

Real-world examples and applications...

## Chapter 5: Best Practices

Industry-standard approaches...

## Conclusion

Summary and next steps...

## Resources

- Additional reading
- Tools and software
- Community links
"""
            
            with open(pdf_dir / f"{title.replace(' ', '_')}.md", "w", encoding="utf-8") as f:
                f.write(md_content)
            
            # Create metadata files
            self._save_metadata(product_dir, self._create_metadata(product_id, title, description, "ebook", **kwargs))
            self._save_description(product_dir, description)
            self._save_license(product_dir, kwargs.get("license", "personal"))
            self._save_keywords(product_dir, kwargs.get("keywords", [title]))
            self._save_pricing(product_dir, kwargs.get("price_usd", 19.0), kwargs.get("price_idr", 285000))
            self._save_version(product_dir, "1.0.0")
            self._save_history(product_dir, title)
            
            # Create empty quality report
            with open(product_dir / "quality_report.json", "w") as f:
                json.dump({"status": "pending", "checks": [], "score": 0}, f)
            
            logger.info(f"eBook generated: {product_id}")
            return {
                "product_id": product_id,
                "product_dir": str(product_dir),
                "files_created": 8,
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate eBook: {e}")
            return {"error": str(e)}


class TemplateGenerator(ProductGenerator):
    """Generate template products"""
    
    def generate(self, product_id: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        try:
            product_dir = self._create_product_structure(product_id, title)
            
            template_type = kwargs.get("template_type", "html")
            templates_dir = product_dir / "product" / "templates"
            templates_dir.mkdir(exist_ok=True)
            
            # Create template files
            if template_type == "html":
                self._generate_html_templates(templates_dir, title, description)
            elif template_type == "excel":
                self._generate_excel_templates(templates_dir, title, description)
            elif template_type == "canva":
                self._generate_canva_templates(templates_dir, title, description)
            
            # Create metadata files
            self._save_metadata(product_dir, self._create_metadata(product_id, title, description, "template", **kwargs))
            self._save_description(product_dir, description)
            self._save_license(product_dir, kwargs.get("license", "commercial"))
            self._save_keywords(product_dir, kwargs.get("keywords", [title, "template"]))
            self._save_pricing(product_dir, kwargs.get("price_usd", 29.0), kwargs.get("price_idr", 435000))
            self._save_version(product_dir, "1.0.0")
            self._save_history(product_dir, title)
            
            with open(product_dir / "quality_report.json", "w") as f:
                json.dump({"status": "pending", "checks": [], "score": 0}, f)
            
            logger.info(f"Template generated: {product_id}")
            return {
                "product_id": product_id,
                "product_dir": str(product_dir),
                "files_created": 8,
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate template: {e}")
            return {"error": str(e)}
    
    def _generate_html_templates(self, templates_dir: Path, title: str, description: str):
        """Generate HTML templates"""
        templates = [
            "index.html",
            "about.html",
            "contact.html",
            "pricing.html",
            "blog.html"
        ]
        
        for template in templates:
            with open(templates_dir / template, "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: #f4f4f4; padding: 20px; border-radius: 8px; }}
        nav {{ margin-top: 10px; }}
        nav a {{ margin-right: 15px; text-decoration: none; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p>{description}</p>
            <nav>
                <a href="index.html">Home</a>
                <a href="about.html">About</a>
                <a href="pricing.html">Pricing</a>
                <a href="contact.html">Contact</a>
            </nav>
        </header>
        <main>
            <h2>Welcome</h2>
            <p>This is a professionally designed template ready for customization.</p>
        </main>
        <footer>
            <p> 2026 MAHA LAKSHMI HOLDINGS. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>""")
    
    def _generate_excel_templates(self, templates_dir: Path, title: str, description: str):
        """Generate Excel template placeholders"""
        template_info = {
            "title": title,
            "description": description,
            "sheets": ["Dashboard", "Data Entry", "Reports", "Settings"],
            "features": [
                "Automated calculations",
                "Data validation",
                "Conditional formatting",
                "Charts and graphs",
                "Export functionality"
            ],
            "instructions": "Open in Microsoft Excel or Google Sheets"
        }
        
        with open(templates_dir / "excel_template.json", "w", encoding="utf-8") as f:
            json.dump(template_info, f, indent=2)
    
    def _generate_canva_templates(self, templates_dir: Path, title: str, description: str):
        """Generate Canva template placeholders"""
        canva_info = {
            "title": title,
            "description": description,
            "formats": ["Instagram Post", "Instagram Story", "Facebook Post", "Twitter Post"],
            "dimensions": {
                "instagram_post": "1080x1080",
                "instagram_story": "1080x1920",
                "facebook_post": "1200x630",
                "twitter_post": "1200x675"
            },
            "instructions": "Import into Canva and customize"
        }
        
        with open(templates_dir / "canva_template.json", "w", encoding="utf-8") as f:
            json.dump(canva_info, f, indent=2)


class PromptPackGenerator(ProductGenerator):
    """Generate prompt pack products"""
    
    def generate(self, product_id: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        try:
            product_dir = self._create_product_structure(product_id, title)
            
            prompts_dir = product_dir / "product" / "prompts"
            prompts_dir.mkdir(exist_ok=True)
            
            # Generate prompt pack
            prompts = kwargs.get("prompts", [])
            if not prompts:
                prompts = [
                    {"name": "Content Writer", "prompt": "You are a professional content writer...", "category": "writing"},
                    {"name": "SEO Specialist", "prompt": "You are an SEO expert...", "category": "marketing"},
                    {"name": "Social Media Manager", "prompt": "You are a social media manager...", "category": "social"},
                    {"name": "Email Marketer", "prompt": "You are an email marketing expert...", "category": "email"},
                    {"name": "Copywriter", "prompt": "You are a direct-response copywriter...", "category": "copywriting"}
                ]
            
            with open(prompts_dir / "prompts.json", "w", encoding="utf-8") as f:
                json.dump(prompts, f, indent=2)
            
            # Create README
            with open(prompts_dir / "README.md", "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write("## Installation\n\n")
                f.write("1. Copy prompts.json to your AI tool\n")
                f.write("2. Import prompts into your favorite LLM\n")
                f.write("3. Start using immediately\n\n")
                f.write("## Prompts Included\n\n")
                for i, prompt in enumerate(prompts, 1):
                    f.write(f"{i}. {prompt['name']}\n")
            
            # Create metadata files
            self._save_metadata(product_dir, self._create_metadata(product_id, title, description, "prompt_pack", **kwargs))
            self._save_description(product_dir, description)
            self._save_license(product_dir, kwargs.get("license", "commercial"))
            self._save_keywords(product_dir, kwargs.get("keywords", [title, "prompts", "AI"]))
            self._save_pricing(product_dir, kwargs.get("price_usd", 29.0), kwargs.get("price_idr", 435000))
            self._save_version(product_dir, "1.0.0")
            self._save_history(product_dir, title)
            
            with open(product_dir / "quality_report.json", "w") as f:
                json.dump({"status": "pending", "checks": [], "score": 0}, f)
            
            logger.info(f"Prompt pack generated: {product_id}")
            return {
                "product_id": product_id,
                "product_dir": str(product_dir),
                "files_created": 8,
                "prompts_count": len(prompts),
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate prompt pack: {e}")
            return {"error": str(e)}


class ChecklistGenerator(ProductGenerator):
    """Generate checklist products"""
    
    def generate(self, product_id: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        try:
            product_dir = self._create_product_structure(product_id, title)
            
            checklist_dir = product_dir / "product" / "checklist"
            checklist_dir.mkdir(exist_ok=True)
            
            # Generate checklist
            checklist_items = kwargs.get("checklist_items", [
                "Item 1: Complete setup",
                "Item 2: Configure settings",
                "Item 3: Test functionality",
                "Item 4: Deploy to production",
                "Item 5: Monitor performance"
            ])
            
            checklist = {
                "title": title,
                "description": description,
                "items": [
                    {"id": i+1, "task": item, "completed": False, "notes": ""}
                    for i, item in enumerate(checklist_items)
                ],
                "total_items": len(checklist_items),
                "estimated_time": f"{len(checklist_items) * 5} minutes"
            }
            
            with open(checklist_dir / "checklist.json", "w", encoding="utf-8") as f:
                json.dump(checklist, f, indent=2)
            
            # Create markdown version
            with open(checklist_dir / "checklist.md", "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                for item in checklist["items"]:
                    f.write(f"- [ ] {item['task']}\n")
            
            # Create metadata files
            self._save_metadata(product_dir, self._create_metadata(product_id, title, description, "checklist", **kwargs))
            self._save_description(product_dir, description)
            self._save_license(product_dir, kwargs.get("license", "personal"))
            self._save_keywords(product_dir, kwargs.get("keywords", [title, "checklist"]))
            self._save_pricing(product_dir, kwargs.get("price_usd", 9.0), kwargs.get("price_idr", 135000))
            self._save_version(product_dir, "1.0.0")
            self._save_history(product_dir, title)
            
            with open(product_dir / "quality_report.json", "w") as f:
                json.dump({"status": "pending", "checks": [], "score": 0}, f)
            
            logger.info(f"Checklist generated: {product_id}")
            return {
                "product_id": product_id,
                "product_dir": str(product_dir),
                "files_created": 8,
                "items_count": len(checklist_items),
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate checklist: {e}")
            return {"error": str(e)}


class MiniCourseGenerator(ProductGenerator):
    """Generate mini course products"""
    
    def generate(self, product_id: str, title: str, description: str, **kwargs) -> Dict[str, Any]:
        try:
            product_dir = self._create_product_structure(product_id, title)
            
            course_dir = product_dir / "product" / "course"
            course_dir.mkdir(exist_ok=True)
            
            # Generate course structure
            modules = kwargs.get("modules", [
                {"module": 1, "title": "Introduction", "lessons": ["Welcome", "Overview", "Prerequisites"]},
                {"module": 2, "title": "Core Concepts", "lessons": ["Concept 1", "Concept 2", "Concept 3"]},
                {"module": 3, "title": "Practical Application", "lessons": ["Example 1", "Example 2", "Exercise"]},
                {"module": 4, "title": "Advanced Topics", "lessons": ["Advanced 1", "Advanced 2", "Case Study"]},
                {"module": 5, "title": "Conclusion", "lessons": ["Summary", "Next Steps", "Resources"]}
            ])
            
            # Create course structure
            course_structure = {
                "title": title,
                "description": description,
                "modules": modules,
                "total_modules": len(modules),
                "total_lessons": sum(len(m["lessons"]) for m in modules),
                "estimated_duration": f"{sum(len(m['lessons']) for m in modules) * 10} minutes"
            }
            
            with open(course_dir / "course_structure.json", "w", encoding="utf-8") as f:
                json.dump(course_structure, f, indent=2)
            
            # Create module markdown files
            for module in modules:
                module_dir = course_dir / f"module_{module['module']:02d}_{module['title'].replace(' ', '_')}"
                module_dir.mkdir(exist_ok=True)
                
                with open(module_dir / "README.md", "w", encoding="utf-8") as f:
                    f.write(f"# Module {module['module']}: {module['title']}\n\n")
                    f.write(f"{description}\n\n")
                    f.write("## Lessons\n\n")
                    for lesson in module["lessons"]:
                        f.write(f"- {lesson}\n")
            
            # Create metadata files
            self._save_metadata(product_dir, self._create_metadata(product_id, title, description, "mini_course", **kwargs))
            self._save_description(product_dir, description)
            self._save_license(product_dir, kwargs.get("license", "personal"))
            self._save_keywords(product_dir, kwargs.get("keywords", [title, "course", "tutorial"]))
            self._save_pricing(product_dir, kwargs.get("price_usd", 49.0), kwargs.get("price_idr", 735000))
            self._save_version(product_dir, "1.0.0")
            self._save_history(product_dir, title)
            
            with open(product_dir / "quality_report.json", "w") as f:
                json.dump({"status": "pending", "checks": [], "score": 0}, f)
            
            logger.info(f"Mini course generated: {product_id}")
            return {
                "product_id": product_id,
                "product_dir": str(product_dir),
                "files_created": 8,
                "modules_count": len(modules),
                "lessons_count": course_structure["total_lessons"],
                "status": "generated"
            }
            
        except Exception as e:
            logger.error(f"Failed to generate mini course: {e}")
            return {"error": str(e)}


class ProductGeneratorFactory:
    """Factory for creating product generators"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.generators = {
            "ebook": EbookGenerator,
            "template": TemplateGenerator,
            "prompt_pack": PromptPackGenerator,
            "checklist": ChecklistGenerator,
            "mini_course": MiniCourseGenerator
        }
    
    def get_generator(self, category: str) -> Optional[ProductGenerator]:
        """Get generator for category"""
        generator_class = self.generators.get(category)
        if generator_class:
            return generator_class(self.output_dir)
        return None
    
    def get_supported_categories(self) -> List[str]:
        """Get list of supported categories"""
        return list(self.generators.keys())


def main():
    """Test generators"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    factory = ProductFactory(db, config)
    generator_factory = ProductGeneratorFactory(OUTPUT_DIR)
    
    # Test eBook generation
    ebook_gen = generator_factory.get_generator("ebook")
    if ebook_gen:
        result = ebook_gen.generate(
            product_id="ML-20260727-TEST001",
            title="Digital Marketing Mastery",
            description="Complete guide to digital marketing in 2026",
            price_usd=19.0,
            price_idr=285000,
            keywords=["digital marketing", "SEO", "social media"]
        )
        print(f"eBook: {result}")
    
    # Test template generation
    template_gen = generator_factory.get_generator("template")
    if template_gen:
        result = template_gen.generate(
            product_id="ML-20260727-TEST002",
            title="Landing Page Template",
            description="High-converting landing page template",
            template_type="html",
            price_usd=49.0,
            price_idr=735000
        )
        print(f"Template: {result}")
    
    db.close()


if __name__ == "__main__":
    main()
