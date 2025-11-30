"""
Unit tests for Focus Buddy tools
"""

from src.tools import parse_tasks, prioritize_tasks, create_focus_schedule


def test_parse_tasks():
    """Test task parsing from messy input"""
    print("Test 1: Parsing tasks...")
    
    raw_text = """
    - Review 3 pull requests
    - Fix authentication bug (15 min)
    - Write API documentation
    - Reply to Sarah about Q4 planning
    """
    
    tasks = parse_tasks(raw_text)
    
    assert len(tasks) == 4, f"Expected 4 tasks, got {len(tasks)}"
    assert any("bug" in t.title.lower() for t in tasks), "Bug task not found"
    assert any(t.estimated_minutes == 15 for t in tasks), "15-minute estimate not parsed"
    
    print(f"✓ Parsed {len(tasks)} tasks")
    for task in tasks:
        print(f"  - {task.title} ({task.estimated_minutes} min)")
    
    return tasks


def test_prioritize_tasks(tasks):
    """Test task prioritization"""
    print("\nTest 2: Prioritizing tasks...")
    
    prioritized = prioritize_tasks(tasks)
    
    assert len(prioritized) == len(tasks), "Task count changed during prioritization"
    assert prioritized[0].priority_score > 0, "No priority scores assigned"
    
    # Bug fixes should be high priority
    top_task = prioritized[0]
    print(f"✓ Top priority: {top_task.title} (score: {top_task.priority_score:.2f})")
    
    print("\nFull priority order:")
    for i, task in enumerate(prioritized, 1):
        print(f"  {i}. {task.title} (score: {task.priority_score:.2f})")
    
    return prioritized


def test_create_schedule(tasks):
    """Test schedule creation"""
    print("\nTest 3: Creating schedule...")
    
    schedule = create_focus_schedule(tasks, available_minutes=25)
    
    assert len(schedule) > 0, "No schedule blocks created"
    
    # Verify schedule fits in time
    total_time = max(block.end_minute for block in schedule)
    assert total_time <= 25, f"Schedule exceeds 25 minutes: {total_time}"
    
    print(f"✓ Created {len(schedule)} time blocks:")
    for block in schedule:
        duration = block.end_minute - block.start_minute
        print(f"  {block.start_minute:2d}-{block.end_minute:2d} min ({duration:2d} min): {block.task_title}")
    
    return schedule


def main():
    """Run all tests"""
    print("=" * 60)
    print("FOCUS BUDDY TOOL TESTS")
    print("=" * 60 + "\n")
    
    try:
        # Test 1
        tasks = test_parse_tasks()
        
        # Test 2
        prioritized = test_prioritize_tasks(tasks)
        
        # Test 3
        schedule = test_create_schedule(prioritized)
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())