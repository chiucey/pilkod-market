# Implementation Patterns

## Pattern 1: Cache-First Execution

```python
def execute_with_cache(skill_name, query):
    """
    Check cache before executing skill.
    Returns (result, from_cache).
    """
    cache_key = generate_cache_key(query)
    cache_path = get_cache_path(skill_name, cache_key)
    
    # Check cache
    if cache_path.exists() and not is_expired(cache_path):
        return load_cached_result(cache_path), True
    
    # Execute skill
    result = invoke_skill(skill_name, query)
    
    # Cache result
    save_to_cache(cache_path, result)
    return result, False
```

## Pattern 2: Batched Invocation

```python
def batch_invoke(tasks):
    """
    Group similar tasks and invoke once.
    tasks: [{"skill": "pdf", "query": "...", "id": 1}, ...]
    """
    # Group by skill
    by_skill = defaultdict(list)
    for task in tasks:
        by_skill[task["skill"]].append(task)
    
    results = {}
    for skill_name, group in by_skill.items():
        # Combine queries
        combined = combine_queries([t["query"] for t in group])
        
        # Single invocation
        combined_result = invoke_skill(skill_name, combined)
        
        # Split results
        results.update(split_results(combined_result, group))
    
    return results
```

## Pattern 3: Self-Execution Decision

```python
def should_delegate(task, available_skills):
    """
    Decide whether to execute directly or delegate.
    """
    # Check if any skill matches
    matching_skill = find_best_skill(task, available_skills)
    
    if not matching_skill:
        return True  # No skill, must do it ourselves
    
    # Check complexity
    if is_simple_task(task):
        return False  # Direct execution cheaper
    
    # Check if skill would significantly help
    if not skill_provides_help(task, matching_skill):
        return False
    
    # Check cache potential (reusable results?)
    if has_cache_potential(task):
        return True  # Caching makes delegation worthwhile
    
    return True
```

## Pattern 4: Context Trimming

```python
def trim_context(full_result, keep_keys):
    """
    Keep only essential parts from skill result.
    """
    if isinstance(full_result, dict):
        return {k: full_result[k] for k in keep_keys if k in full_result}
    elif isinstance(full_result, str):
        # Keep first N characters
        return full_result[:keep_chars]
    else:
        return full_result


def summarize_result(result):
    """
    Create brief summary for future reference.
    """
    if isinstance(result, dict):
        # Extract key metrics
        return f"Success: {result.get('success')}, Files: {result.get('file_count')}"
    elif "error" in result.lower():
        return f"Error: {extract_error(result)}"
    else:
        return f"Completed in {estimate_time}"
```

## Token Cost Estimation

```python
def estimate_cost(task):
    """
    Estimate tokens for different approaches.
    """
    # Direct execution
    direct_cost = estimate_tokens(task)
    
    # Skill loading + execution
    skill_load_cost = 1000  # Average
    skill_exec_cost = estimate_tokens(task)
    delegate_cost = skill_load_cost + skill_exec_cost
    
    return {
        "direct": direct_cost,
        "delegate": delegate_cost,
        "savings": delegate_cost - direct_cost
    }
```