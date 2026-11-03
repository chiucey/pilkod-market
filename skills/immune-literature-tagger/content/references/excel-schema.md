# Excel Workbook Schema

## Sheet: Knowledge_Cards

One row per card. Use these columns in this order:

1. Card_ID
2. PDF_File
3. Paper_Title
4. Journal_or_Source
5. Year
6. DOI_PMID
7. Article_Type
8. Primary_Evidence_Object
9. Evidence_Level
10. Level1_Tag
11. Level2_Tag
12. Content_Use_Tag
13. Core_Knowledge_Card_CN
14. One_Sentence_Conclusion_CN
15. Source_Fact_CN
16. Interpretation_CN
17. Key_Data
18. Population_Model_Sample
19. Intervention_Exposure_Target
20. Comparator
21. Outcome_or_Mechanism
22. Product_or_Competitor_Mentioned
23. Source_Page
24. Source_Section
25. Source_Figure_Table
26. Source_Excerpt_or_Paraphrase
27. Original_Reference_if_Review
28. Needs_Source_Tracing
29. Needs_Medical_Review
30. Needs_Compliance_Review
31. Needs_Patient_Rewrite
32. Patient_Friendly_Version_CN
33. Overclaim_Risk
34. Limitation_CN
35. Suggested_Output_Form
36. Reviewer_Notes
37. Status

## Sheet: Tag_Summary

Include counts by:

- Level1_Tag
- Level2_Tag
- Article_Type
- Evidence_Level
- Needs_Source_Tracing
- Needs_Medical_Review
- Needs_Compliance_Review
- Needs_Patient_Rewrite
- Status

## Sheet: Source_Map

Use these columns:

1. Source_ID
2. PDF_File
3. Paper_Title
4. Page
5. Section
6. Figure_Table
7. Extracted_Source_Content
8. Linked_Card_IDs
9. Traceability_Status
10. Notes

## Sheet: Review_Checklist

Use these columns:

1. Check_Item
2. Rule
3. Applies_To
4. Pass_Fail_NA
5. Evidence_or_Reason
6. Owner
7. Notes

Mandatory checklist items:

- Every card has one core conclusion.
- Every card has page-level source traceability.
- Product or competitor claims are compliance flagged.
- Review-derived clinical/product/key data are source-tracing flagged.
- Patient-facing content is rewritten into plain language.
- Evidence level matches article design.
- No causal, clinical, or mechanistic overclaim.

## Sheet: Instructions

Include:

- Workbook purpose.
- How to filter cards.
- Meaning of review flags.
- Note that cards are draft medical content assets requiring appropriate review before external use.
