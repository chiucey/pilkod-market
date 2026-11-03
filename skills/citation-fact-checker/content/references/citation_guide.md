# Citation Verification Reference Guide

## Common Academic Database APIs

### CrossRef API (Preferred for DOI Verification)
```
Base URL: https://api.crossref.org/works/{DOI}
Example: https://api.crossref.org/works/10.1038/nature12373
```

### OpenAlex API
```
Base URL: https://api.openalex.org/works?filter=doi:{DOI}
Example: https://api.openalex.org/works?filter=doi:10.1038/nature12373
```

### Semantic Scholar API
```
Base URL: https://api.semanticscholar.org/graph/v1/paper/{DOI}?fields=all
Example: https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/nature12373?fields=all
```

### PubMed E-utilities
```
Base URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={DOI}[aid]
```

## DOI Format Standards

### Standard DOI Format
```
10. + Publisher ID + "/" + Unique Suffix
```

### Common Prefixes
- **10.1038**: Nature Publishing Group
- **10.1126**: American Association for the Advancement of Science (AAAS)
- **10.1016**: Elsevier
- **10.1007**: Springer
- **10.48550**: arXiv
- **10.1109**: IEEE
- **10.1145**: ACM

## Common Journal/Conference Abbreviations

### Computer Science
| Full Name | Abbreviation |
|------|------|
| Association for Computing Machinery | ACM |
| Institute of Electrical and Electronics Engineers | IEEE |
| Conference on Computer Vision and Pattern Recognition | CVPR |
| International Conference on Machine Learning | ICML |
| Neural Information Processing Systems | NeurIPS |
| International World Wide Web Conference | WWW |
| SIGCHI Conference on Human Factors in Computing Systems | CHI |

### Natural Sciences
| Full Name | Abbreviation |
|------|------|
| Nature | Nature |
| Science | Science |
| Cell | Cell |
| Proceedings of the National Academy of Sciences | PNAS |
| Nature Communications | Nat Commun |
| Physical Review Letters | Phys Rev Lett |

## Citation Format Standards

### APA 7th Edition
```
Author, A. A., & Author, B. B. (Year). Title of article. Title of Periodical, volume(issue), pages. https://doi.org/xxxxx
```

### IEEE
```
[1] A. A. Author, "Title of article," Title of Periodical, vol. X, no. X, pp. X-X, Month Year.
```

### Chicago
```
Author Last Name, First Name. "Article Title." Journal Name Volume, no. Issue (Year): Pages. https://doi.org/xxxxx.
```

### MLA 9th Edition
```
Author Last Name, First Name. "Article Title." Journal Name, vol. X, no. X, Year, pp. X-X.
```

## Common Citation Problem Checklist

### DOI Related
- [ ] DOI format correct (10.XXXX/)
- [ ] DOI verifiable via CrossRef
- [ ] DOI points to correct paper

### Author Information
- [ ] Author count matches original
- [ ] Author names spelled correctly
- [ ] Corresponding author marked correctly

### Publication Information
- [ ] Journal/conference name accurate
- [ ] Volume/issue number correct
- [ ] Page range reasonable
- [ ] Publication year matches original
- [ ] DOI/URL valid

### Format Compliance
- [ ] Meets target journal format requirements
- [ ] Punctuation used correctly
- [ ] Case conventions followed
- [ ] Indentation consistent

## Suspicious Citation Warning Signs

1. **DOI invalid or unresolvable**
2. **Journal name doesn't exist or appears fabricated**
3. **Publication year predates journal's founding**
4. **Citation count abnormally high (e.g., thousands of citations within months)**
5. **Author affiliation doesn't match journal location**
6. **Preprint passed off as formally published**
7. **Citations from predatory journals**
8. **Citation format obviously non-compliant**
9. **Year contradicts DOI registration date**
10. **Page numbers exceed actual journal page range**

## Predatory Journal Identification

### Warning Features
- Promise of rapid publication
- High article processing charges without transparency
- Journal name similar to established journals
- Lack of rigorous peer review
- Website contains grammatical errors
- Claimed indexing in major databases that doesn't exist

### Verification Resources
- [Beall's List](https://beallslist.kaust.edu.sa/) - Predatory publisher list
- [DOAJ](https://www.doaj.org/) - Open access journal directory
- [Cabell's](https://www.cabells.com/) - Journal blacklist/whitelist

## Special Literature Verification

### Preprints
- arXiv: https://arxiv.org/abs/{paper_id}
- bioRxiv: https://www.biorxiv.org/content/{doi}
- SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id={id}

### Conference Papers
- IEEE Xplore: https://ieeexplore.ieee.org/document/{id}
- ACM Digital Library: https://dl.acm.org/doi/{doi}
- Springer LNCS: https://link.springer.com/chapter/{doi}

### Book Chapters
- Google Books: https://books.google.com/books?isbn={isbn}
- WorldCat: https://www.worldcat.org/oclc/{oclc}
