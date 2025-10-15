# Main Tasks Dashboard Filter Update

## Overview
Updated the main tasks dashboard to default to "My active tasks" (assigned to me) instead of "All tasks".

## Changes Made

### File: `/Users/viachealavrudenko/dvc-agent/synapse/app/dashboard/tasks_dashboard.py`

**Lines 66-67**: Changed filter dropdown default:
```python
# Before:
index=0  # Default to "All tasks"

# After:
index=1  # Default to "My active tasks" (assigned to me)
```

**Lines 51-53**: Added session state initialization:
```python
# Initialize default filter to "My active tasks"
if "task_filter_view_dashboard" not in st.session_state:
    st.session_state["task_filter_view_dashboard"] = "My active tasks"
```

## Impact

### Main Tasks Dashboard Navigation
- **Location**: Main navigation → "Tasks (X)" page
- **Default Filter**: Now defaults to "My active tasks" instead of "All tasks"
- **User Experience**: Users will see only their assigned tasks by default, making the dashboard more focused and relevant

### Filter Options Available
1. "All tasks" (index 0)
2. **"My active tasks" (index 1) - NEW DEFAULT** ✅
3. "Created by me" (index 2)
4. "Overdue" (index 3)
5. "Due today" (index 4)
6. "Due this week" (index 5)

## Verification

### Expected Behavior:
1. **Fresh Load**: Main Tasks dashboard opens with "My active tasks" filter active
2. **Task Count**: Navigation title shows count of user's active tasks (e.g., "Tasks (5)")
3. **Filtered View**: Only tasks assigned to the current user are displayed
4. **Session Persistence**: Filter setting persists across page refreshes

### Test Steps:
1. Navigate to main dashboard
2. Click on "Tasks (X)" in the navigation
3. Verify filter dropdown shows "My active tasks" as selected
4. Verify only tasks assigned to current user are displayed
5. Refresh page and confirm filter setting is maintained

## Related Files Updated

### Previously Updated (from earlier refactor):
- `tasks.py` - Company-specific tasks tab: defaults to "My active tasks"
- `all_tasks.py` - All tasks page: defaults to "Assigned to me"

### Just Updated:
- `tasks_dashboard.py` - Main tasks dashboard: defaults to "My active tasks"

## Consistency Across All Task Views

All task views now default to showing user's assigned tasks:

1. **Company Tasks Tab**: "My active tasks" (index 1)
2. **All Tasks Page**: "Assigned to me" (index 1) 
3. **Main Tasks Dashboard**: "My active tasks" (index 1) ✅

This provides a consistent, user-focused experience across all task management interfaces.

## Technical Details

- **Session State Key**: `task_filter_view_dashboard`
- **Default Value**: `"My active tasks"`
- **Filter Index**: `1` (second option in dropdown)
- **Backward Compatibility**: Existing users will see the new default on next page load
