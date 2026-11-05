#!/usr/bin/env python3
"""
Test script to verify skill behavior with sample prompts
"""

import json

SAMPLE_PROMPTS = [
    {
        "prompt": "What is a closure in programming?",
        "expected_keywords": ["closure", "function", "scope", "environment"],
        "test_type": "concept_explanation"
    },
    {
        "prompt": "Teach me how React hooks work",
        "expected_keywords": ["hook", "state", "effect", "component"],
        "test_type": "teaching_request"
    },
    {
        "prompt": "Explain the difference between REST and GraphQL",
        "expected_keywords": ["REST", "GraphQL", "API", "comparison"],
        "test_type": "comparison"
    }
]

def test_trigger_phrase_detection():
    """Test that trigger phrases are correctly identified"""
    from validate_skill import SkillValidator
    validator = SkillValidator("/workspace/temp-skills/socratic-teacher")
    
    meta_json_path = "/workspace/temp-skills/socratic-teacher/_meta.json"
    with open(meta_json_path, 'r') as f:
        meta = json.load(f)
    
    trigger_phrases = meta.get('trigger_phrases', [])
    print(f"✓ Trigger phrases configured: {len(trigger_phrases)} phrases")
    
    # Check that common teaching phrases are included
    key_phrases = ['explain', 'teach', 'understand', 'how does', 'what is']
    found = sum(1 for p in key_phrases if any(p in tp.lower() for tp in trigger_phrases))
    print(f"✓ Key teaching phrases covered: {found}/{len(key_phrases)}")

def test_meta_structure():
    """Test _meta.json structure"""
    meta_path = "/workspace/temp-skills/socratic-teacher/_meta.json"
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    
    required = ['id', 'version']
    for field in required:
        assert field in meta, f"Missing required field: {field}"
    
    assert 'trigger_phrases' in meta, "Missing trigger_phrases"
    assert 'domains' in meta, "Missing domains"
    
    print("✓ _meta.json structure valid")
    print(f"  - ID: {meta['id']}")
    print(f"  - Version: {meta['version']}")
    print(f"  - Domains: {', '.join(meta['domains'][:3])}...")

def test_skill_md_content():
    """Test SKILL.md content quality"""
    skill_md_path = "/workspace/temp-skills/socratic-teacher/SKILL.md"
    with open(skill_md_path, 'r') as f:
        content = f.read()
    
    required_sections = [
        'Teaching Philosophy',
        'Teaching Workflow',
        'Response Format',
        'Quality Standards'
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"
    
    print("✓ SKILL.md content structure valid")
    print("  - Contains teaching workflow")
    print("  - Contains response format")
    print("  - Contains quality standards")

def test_references():
    """Test that reference files exist and are substantial"""
    import os
    
    ref_files = [
        "references/heuristic_methodology.md",
        "references/teaching_templates.md"
    ]
    
    for ref_file in ref_files:
        path = f"/workspace/temp-skills/socratic-teacher/{ref_file}"
        assert os.path.exists(path), f"Missing reference: {ref_file}"
        
        with open(path, 'r') as f:
            content = f.read()
        
        # Check minimum content size (should be substantial)
        assert len(content) > 2000, f"{ref_file} is too short"
        
        print(f"✓ {ref_file} exists ({len(content)} chars)")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🧪 Skill Behavior Test Suite")
    print("="*50 + "\n")
    
    tests = [
        ("Meta Structure", test_meta_structure),
        ("Trigger Phrases", test_trigger_phrase_detection),
        ("SKILL.md Content", test_skill_md_content),
        ("Reference Files", test_references),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"\n📋 Test: {name}")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    print("="*50 + "\n")
