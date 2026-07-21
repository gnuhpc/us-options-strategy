# Book-to-Skill Integration Pattern

This reference documents the workflow used to integrate the investment philosophy from "Investment Lessons from Darwin" (《我从达尔文那里学到的投资知识》) by Pulak Prasad into this skill.

## Workflow Used

### 1. Extract Source Text
The EPUB was extracted using `ebooklib` + `BeautifulSoup`:
```python
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
book = epub.read_epub(path)
docs = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
# ... extract text from each document
```

### 2. Read in Sections
The 300K+ char book was read in 400-line sections. First read the table of contents to understand the structure (10 chapters + conclusion in 3 parts), then each chapter systematically.

### 3. Extract Core Principles
From the book's 10 chapters + conclusion, 5 core Darwinian investment principles were identified:
1. Type I Error Avoidance (Ch 1)
2. Quality Matters / ROCE as Filter (Ch 2)
3. Multi-layered Robustness (Ch 3)
4. Proximate vs Ultimate Causes (Ch 4)
5. Historical Analysis over Predictions (Ch 5)
6. Convergent Patterns (Ch 6)
7. Costly Signals (Ch 7)
8. Punctuated Equilibrium (Ch 8-9)
9. Compound Interest / Patience (Ch 10)
10. Simple Repeatable Process (Conclusion)

### 4. Map to Domain
Each principle was mapped to an equivalent concept in options trading, producing a mapping table used in the strategy engine.

### 5. Rewrite
- Added `assess_darwinian_quality()` — quality assessment of underlying stock
- Added `detect_punctuated_equilibrium()` — market dislocation detector
- Modified all strategy recommendations to include `darwinian_rationale`
- Added "DON'T TRADE" as a legitimate recommendation type
- Rewrote SKILL.md with philosophy section
- Added Darwinian perspective to references/strategies.md

### 6. Verify
Live test with AAPL confirmed all new fields appear correctly.

## Reusing This Pattern

To integrate another book into any skill:
1. Extract → 2. Read → 3. Extract principles → 4. Map to domain → 5. Rewrite → 6. Verify