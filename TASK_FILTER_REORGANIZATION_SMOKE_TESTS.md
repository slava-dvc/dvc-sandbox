# Task Filter Reorganization Smoke Tests

## Overview
Verify the reorganized task filter dropdown works correctly with the new user-centered order.

## New Filter Order

### Company Tasks View (tasks.py)
1. **All tasks** (default) - full list view
2. **My active tasks** - tasks assigned to current user and not completed
3. **Created by me** - tasks the current user created  
4. **Overdue** - tasks with due dates in the past
5. **Due today** - tasks due today
6. **Due this week** - tasks due within the next 7 days

### All Tasks View (all_tasks.py)
1. **Assigned to me** (default) - tasks assigned to current user (any status)
2. **All tasks** - full list view
3. **My active tasks** - tasks assigned to current user and not completed
4. **Created by me** - tasks the current user created  
5. **Overdue** - tasks with due dates in the past
6. **Due today** - tasks due today
7. **Due this week** - tasks due within the next 7 days

## Test Steps

### 1. Company Tasks View (tasks.py)
1. Navigate to any company page → Tasks tab
2. Verify filter dropdown shows new order with "All tasks" as default
3. Test each filter option:
   - **All tasks**: Should show all tasks regardless of status
   - **My active tasks**: Should show only active tasks assigned to current user
   - **Created by me**: Should show only tasks created by current user
   - **Overdue**: Should show only active tasks with past due dates
   - **Due today**: Should show only active tasks due today
   - **Due this week**: Should show only active tasks due within next 7 days

### 2. All Tasks View (all_tasks.py)
1. Navigate to main Tasks page (all companies)
2. Verify filter dropdown shows new order with "Assigned to me" as default
3. Test each filter option:
   - **Assigned to me**: Should show all tasks assigned to current user (any status)
   - **All tasks**: Should show all tasks regardless of status
   - **My active tasks**: Should show only active tasks assigned to current user
   - **Created by me**: Should show only tasks created by current user
   - **Overdue**: Should show only active tasks with past due dates
   - **Due today**: Should show only active tasks due today
   - **Due this week**: Should show only active tasks due within next 7 days

### 3. Filter Persistence
1. Select any filter option
2. Navigate away and back to the page
3. Verify the selected filter persists (Streamlit session state)

### 4. Edge Cases
1. **No current user**: Filter should show empty results for user-specific filters
2. **No tasks matching filter**: Should show appropriate "No tasks found" message
3. **Date boundaries**: Verify "Due today" and "Due this week" handle date boundaries correctly

## Expected Results

### ✅ Success Criteria
- Company tasks view shows "All tasks" as default
- Main tasks screen shows "Assigned to me" as default
- Each filter option works correctly and shows appropriate tasks
- Filter state persists between page navigations
- "Completed" filter has been removed from both views
- Appropriate messages shown when no tasks match filter criteria

### 🎯 Key Improvements
- Company view defaults to comprehensive "All tasks" for full context
- Main screen defaults to personal "Assigned to me" for focused workflow
- Removed "Completed" filter to reduce clutter (completed tasks still accessible via segmented controls)
- Logical grouping: personal filters → time-based filters → comprehensive view
- Better mental model with context-appropriate defaults

## Files Modified
- `synapse/app/dashboard/tasks.py` (lines 287-331)
- `synapse/app/dashboard/all_tasks.py` (lines 632-666)

## Implementation Details
- Uses `st.selectbox()` with human-readable labels and internal filter keys
- "My active tasks" is the default option (index=0) for both views
- Filter state persists via `st.session_state` using unique keys
- All new date-based filters include proper boundary handling
