# Amazon Style Finder Reference

## Dimension Selection Deep Dive

### How to Verify Each Criterion

**Criterion 1: Search suggestion frequency >30%**
- Go to Amazon search bar, type `{category} ` (with trailing space)
- Record top 10 autocomplete suggestions
- Count how many relate to each candidate dimension
- A dimension needs >=4/10 suggestions to qualify

**Criterion 2: Function/price variance >50%**
- Check Amazon Best Sellers for the category
- Note price range for products in each dimension bucket
- If the highest-price bucket is <2x the lowest, the dimension is too weak

**Criterion 3: Active filtering (not passive browsing)**
- Check if Amazon's left sidebar has a filter for this dimension
- OR check if users type this as a search modifier (e.g., "for kids", "wireless")
- Passive = users see it in results and might notice; Active = users search for it deliberately

### Dimension Selection Fail-Safe

If no dimension satisfies all three criteria:
1. Try combining two dimensions (e.g., "Use Case + Core Function")
2. If still failing, the category may be too homogeneous — output 2-3 broad styles max
3. If the category is genuinely 0-1 stage (no stable mental models), refuse to generate styles and explain why

## Style Enumeration Rules

### MECE Verification Checklist

For any two styles A and B:
- [ ] Can a single product reasonably be described by both? If yes, merge or redefine
- [ ] Is there a Best Seller product that fits neither? If yes, add a style or broaden definitions

### Market Coverage Estimation

| Coverage | Best Seller Share | When to Use |
|----------|-------------------|-------------|
| 高 (High) | >25% | The dominant style, usually rank 1-2 |
| 中 (Medium) | 10-25% | Clear niche with sustained demand |
| 低 (Low) | 3-10% | Emerging or declining segment |

Never assign "高" to more than 2 styles. If 3+ styles seem "high", your segmentation is too granular.

### Exclusion List (Hard Rules)

| Type | Example | Why Excluded |
|------|---------|--------------|
| Standard feature | "快充" for power banks | No longer a differentiator |
| Pure aesthetic | "红色款" | Does not change user group or function |
| Micro-niche | "左撇子专用" | <3% share, not worth a top-level style |
| Brand | "Anker款" | Brands are not styles |
| Price tier | "高端款" | Price is an outcome, not a root cause |

## Term Standardization Guide

### Amazon Autocomplete Verification

Before finalizing `name_en`:
1. Go to amazon.com
2. Type the term in the search bar
3. If it appears in dropdown suggestions within 3 characters, it's valid
4. If not, try variations until one matches

### Common Term Corrections

| Incorrect | Correct | Why |
|-----------|---------|-----|
| Hand Held | Handheld | Amazon uses compound form |
| Air Pump | Tire Inflator | Amazon shoppers use "tire inflator" more |
| For Children | Kids | Shorter, matches search behavior |
| Wireless | Cordless | For tools/appliances, "cordless" dominates |

## Data Source Reliability Ranking

| Source | Reliability | Use For |
|--------|-------------|---------|
| Amazon autocomplete | Very High | Term validation, search behavior |
| Amazon Best Sellers | Very High | Market coverage, price bands |
| Amazon filter sidebar | High | Dimension validation |
| Google Trends | Medium | Temporal trends, geographic variance |
| Reddit/Quora | Medium | User decision criteria, pain points |
| Third-party reports | Low | Only use when primary sources exhausted |
