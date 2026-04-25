# extract_from_html.py
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
import json
import csv

@dataclass
class AntiPattern:
    name: str
    category: str
    description: str
    anti_pattern_description: str
    best_practice_description: str
    bad_example: str
    good_example: str
    references: str
    
class AntiPatternHTMLParser(HTMLParser):
    """Custom HTML parser to extract anti-pattern content"""
    
    def __init__(self):
        super().__init__()
        self.reset_data()
        
    def reset_data(self):
        self.current_section = None
        self.current_content = []
        self.anti_pattern = {}
        
        # State flags
        self.in_anti_pattern_section = False
        self.in_best_practice_section = False
        self.in_code_block = False
        self.current_code = []
        
        # Storage
        self.anti_patterns = []
    
    def handle_starttag(self, tag, attrs):
        # Check for section headers
        if tag == 'div' and ('class', 'section') in attrs:
            self.current_section = self.get_attr(attrs, 'id')
        
        # Anti-pattern section
        if tag == 'div' and ('id', 'anti-pattern') in attrs:
            self.in_anti_pattern_section = True
            
        # Best practice section
        if tag == 'div' and ('id', 'best-practice') in attrs:
            self.in_best_practice_section = True
            
        # Code blocks
        if tag == 'div' and ('class', 'highlight-python') in attrs:
            self.in_code_block = True
            self.current_code = []
            
    def handle_endtag(self, tag):
        if tag == 'div' and self.in_anti_pattern_section:
            self.in_anti_pattern_section = False
            
        if tag == 'div' and self.in_best_practice_section:
            self.in_best_practice_section = False
            
        if tag == 'div' and self.in_code_block:
            self.in_code_block = False
            if self.in_anti_pattern_section:
                self.anti_pattern['bad_example'] = ''.join(self.current_code).strip()
            elif self.in_best_practice_section:
                self.anti_pattern['good_example'] = ''.join(self.current_code).strip()
            self.current_code = []
    
    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
            
        # Capture content in sections
        if self.in_anti_pattern_section and not self.in_code_block:
            self.anti_pattern['anti_pattern_description'] = data
        elif self.in_best_practice_section and not self.in_code_block:
            self.anti_pattern['best_practice_description'] = data
            
        # Capture code
        if self.in_code_block:
            self.current_code.append(data)
    
    def get_attr(self, attrs, name):
        for attr, value in attrs:
            if attr == name:
                return value
        return None

class AntiPatternExtractor:
    def __init__(self, docs_path: str = "python-anti-patterns/docs"):
        self.docs_path = Path(docs_path)
        
        # Category mapping from folder names
        self.category_map = {
            'correctness': 'Correctness',
            'maintainability': 'Maintainability', 
            'readability': 'Readability',
            'security': 'Security',
            'performance': 'Performance'
        }
        
    def extract_all(self) -> List[AntiPattern]:
        """Extract all anti-patterns from all category folders"""
        all_patterns = []
        
        for category_folder, category_name in self.category_map.items():
            folder_path = self.docs_path / category_folder
            if not folder_path.exists():
                print(f"⚠️ Folder not found: {folder_path}")
                continue
                
            patterns = self.extract_from_category(folder_path, category_name)
            all_patterns.extend(patterns)
            print(f"✅ Extracted {len(patterns)} patterns from {category_name}")
            
        return all_patterns
    
    def extract_from_category(self, folder_path: Path, category: str) -> List[AntiPattern]:
        """Extract all anti-patterns from a category folder"""
        patterns = []
        
        # Find all HTML files in the category folder (excluding index.html)
        html_files = [f for f in folder_path.glob("*.html") if f.name != "index.html"]
        
        for html_file in html_files:
            pattern = self.parse_html_file(html_file, category)
            if pattern:
                patterns.append(pattern)
                
        return patterns
    
    def parse_html_file(self, filepath: Path, category: str) -> Optional[AntiPattern]:
        """Parse a single HTML file to extract anti-pattern data"""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract name from title or main header
        name_match = re.search(r'<title>(.*?)</title>', content)
        name = name_match.group(1).replace(' — Python Anti-Patterns documentation', '').strip() if name_match else filepath.stem
        
        # Extract sections using regex (simpler than full HTML parsing for this structure)
        
        # Anti-pattern section
        anti_pattern_section = self._extract_section(content, 'Anti-pattern')
        
        # Best practice section
        best_practice_section = self._extract_section(content, 'Best practice')
        
        # Extract code examples
        bad_example = self._extract_code_block(content, 'Anti-pattern')
        good_example = self._extract_code_block(content, 'Best practice')
        
        # Extract description text (first paragraph after section header)
        anti_desc = self._extract_description(anti_pattern_section)
        best_desc = self._extract_description(best_practice_section)
        
        # Extract main description (first paragraph after main title)
        main_desc_match = re.search(r'<div class="section"[^>]*>\s*<h1[^>]*>(.*?)</h1>\s*<p>(.*?)</p>', content, re.DOTALL)
        main_description = main_desc_match.group(2).strip() if main_desc_match else ""
        
        # Extract references
        references_section = self._extract_section(content, 'References')
        references = self._extract_list_items(references_section)
        
        return AntiPattern(
            name=name,
            category=category,
            description=main_description,
            anti_pattern_description=anti_desc,
            best_practice_description=best_desc,
            bad_example=bad_example,
            good_example=good_example,
            references=references
        )
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a named section from HTML content"""
        # Pattern for finding section by header
        pattern = rf'<div class="section" id="{section_name.lower().replace(" ", "-")}">(.*?)(?=<div class="section"|$)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            section_content = match.group(1)
            # Remove nested sections
            section_content = re.sub(r'<div class="section".*?</div>', '', section_content, flags=re.DOTALL)
            return section_content.strip()
        
        # Alternative: find by header text
        pattern2 = rf'<h[23]>{section_name}</h[23]>(.*?)(?=<h[23]|</div><div|<div class="section"|$)'
        match2 = re.search(pattern2, content, re.DOTALL | re.IGNORECASE)
        return match2.group(1).strip() if match2 else ""
    
    def _extract_code_block(self, content: str, section_name: str) -> str:
        """Extract code block from a specific section"""
        # Look for code blocks within or near the specified section
        pattern = rf'{section_name}.*?<div class="highlight-python[^"]*"><div class="highlight"><pre><span></span>(.*?)</pre>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            code = match.group(1)
            # Clean up HTML entities and formatting
            code = code.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            code = code.replace('&quot;', '"').replace('&#39;', "'")
            # Remove span tags and line markers
            code = re.sub(r'<span[^>]*>', '', code)
            code = re.sub(r'</span>', '', code)
            code = code.replace('\\n', '\n')
            return code.strip()
        
        return ""
    
    def _extract_description(self, section_content: str) -> str:
        """Extract description text from section (first paragraph)"""
        if not section_content:
            return ""
        
        # Find first paragraph
        p_match = re.search(r'<p>(.*?)</p>', section_content, re.DOTALL)
        if p_match:
            text = p_match.group(1)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            return text.strip()
        
        return section_content[:200]  # Fallback
    
    def _extract_list_items(self, section_content: str) -> str:
        """Extract list items as a string"""
        if not section_content:
            return ""
        
        items = re.findall(r'<li><p>(.*?)</p></li>', section_content, re.DOTALL)
        if items:
            # Clean HTML from each item
            items = [re.sub(r'<[^>]+>', '', item).strip() for item in items]
            return '\n'.join(items)
        
        return ""

# Alternative: Use BeautifulSoup for easier parsing (if you can install it)
try:
    from bs4 import BeautifulSoup
    
    class BeautifulSoupExtractor:
        """Extractor using BeautifulSoup (easier but requires external lib)"""
        
        def __init__(self, docs_path: str = "python-anti-patterns/docs"):
            self.docs_path = Path(docs_path)
            self.category_map = {
                'correctness': 'Correctness',
                'maintainability': 'Maintainability',
                'readability': 'Readability', 
                'security': 'Security',
                'performance': 'Performance'
            }
        
        def extract_all(self) -> List[AntiPattern]:
            patterns = []
            for cat_folder, category in self.category_map.items():
                folder = self.docs_path / cat_folder
                if not folder.exists():
                    continue
                    
                for html_file in folder.glob("*.html"):
                    if html_file.name == "index.html":
                        continue
                    
                    pattern = self.parse_html(html_file, category)
                    if pattern:
                        patterns.append(pattern)
                        print(f"  📄 {pattern.name}")
            
            return patterns
        
        def parse_html(self, filepath: Path, category: str) -> Optional[AntiPattern]:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Get title
            title_elem = soup.find('title')
            name = title_elem.text.replace(' — Python Anti-Patterns documentation', '').strip() if title_elem else filepath.stem
            
            # Get main description
            main_content = soup.find('div', class_='section')
            first_p = main_content.find('p') if main_content else None
            description = first_p.text.strip() if first_p else ""
            
            # Find anti-pattern section
            anti_section = soup.find('div', id='anti-pattern')
            anti_desc = ""
            bad_example = ""
            
            if anti_section:
                # Get description
                anti_p = anti_section.find('p')
                if anti_p:
                    anti_desc = anti_p.text.strip()
                
                # Get code example
                code_block = anti_section.find('div', class_='highlight-python')
                if code_block:
                    code = code_block.find('pre')
                    if code:
                        bad_example = code.text.strip()
            
            # Find best practice section
            best_section = soup.find('div', id='best-practice')
            best_desc = ""
            good_example = ""
            
            if best_section:
                best_p = best_section.find('p')
                if best_p:
                    best_desc = best_p.text.strip()
                
                code_block = best_section.find('div', class_='highlight-python')
                if code_block:
                    code = code_block.find('pre')
                    if code:
                        good_example = code.text.strip()
            
            # Get references
            refs = []
            ref_section = soup.find('div', id='references')
            if ref_section:
                for li in ref_section.find_all('li'):
                    refs.append(li.text.strip())
            
            return AntiPattern(
                name=name,
                category=category,
                description=description,
                anti_pattern_description=anti_desc,
                best_practice_description=best_desc,
                bad_example=bad_example,
                good_example=good_example,
                references='\n'.join(refs)
            )
            
except ImportError:
    print("BeautifulSoup not available. Install with: pip install beautifulsoup4")
    BeautifulSoupExtractor = None

# ============================================
# MAIN EXTRACTION AND EXPORT
# ============================================

def main():
    # Path to your cloned repo
    repo_path = "python-anti-patterns/docs"
    
    # Try BeautifulSoup first (better parsing)
    if BeautifulSoupExtractor:
        print("🔍 Using BeautifulSoup extractor...")
        extractor = BeautifulSoupExtractor(repo_path)
        patterns = extractor.extract_all()
    else:
        print("🔍 Using regex extractor (limited)...")
        extractor = AntiPatternExtractor(repo_path)
        patterns = extractor.extract_all()
    
    print(f"\n📊 Total anti-patterns extracted: {len(patterns)}")
    
    # Count by category
    categories = {}
    for p in patterns:
        categories[p.category] = categories.get(p.category, 0) + 1
    
    print("\n📁 By category:")
    for cat, count in categories.items():
        print(f"   {cat}: {count}")
    
    # Export to CSV
    csv_file = "antipatterns.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'name', 'category', 'description', 
            'anti_pattern_description', 'best_practice_description',
            'bad_example', 'good_example', 'references'
        ])
        writer.writeheader()
        for p in patterns:
            writer.writerow(asdict(p))
    print(f"\n💾 Saved to {csv_file}")
    
    # Export to JSON
    json_file = "antipatterns.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(p) for p in patterns], f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to {json_file}")
    
    # Show sample
    if patterns:
        print(f"\n📝 Sample pattern:")
        sample = patterns[0]
        print(f"   Name: {sample.name}")
        print(f"   Category: {sample.category}")
        print(f"   Bad code: {sample.bad_example[:100]}...")
    
    return patterns

if __name__ == "__main__":
    patterns = main()