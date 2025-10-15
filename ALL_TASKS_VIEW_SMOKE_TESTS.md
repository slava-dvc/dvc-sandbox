# All Tasks View - Smoke Tests

## Overview
The new "All Tasks" view shows tasks from all companies with a company name column, "My tasks" default filter, and inline editing capabilities. Tasks sync automatically between the All Tasks page and company-specific Tasks tabs.

## User Selector for Testing
A new "Testing as:" dropdown in the sidebar allows switching between team member identities:
- Default user: **Nick** (Managing Partner)
- Available users: Marina, Nick, Mel, Charles, Alexey, Tony, Elena, Vlad, Slava
- Tasks created without @mention auto-assign to current selected user
- "My tasks" filter shows tasks for the currently selected user

## Mock Data Setup
The system now includes realistic mock tasks assigned to actual team members:
- **Marina**: Managing Partner tasks (IC memos, pitch reviews, due diligence)
- **Nick**: Managing Partner tasks (founder calls, competitive analysis, references)
- **Mel**: GP tasks (MRR validation, health partnerships, compliance review)
- **Charles**: GP tasks (demo scheduling, FDA review, enterprise sales)
- **Alexey**: Venture Partner tasks (technical architecture, AI metrics, security audit)
- **Tony**: Head of Product tasks (platform automation, product roadmap, analytics)
- **Elena**: Head of IR tasks (investor updates, community events, LP reports)
- **Vlad**: Head of Engineering tasks (technical assessments, AI agents, scalability)
- **Slava**: Mixed tasks for testing (board preparation, technical reviews)

Tasks are distributed across 6 companies with various due dates (overdue, today, tomorrow, future) and include both active and completed tasks with realistic outcomes.

## Smoke Test Steps

### 1. Navigation Test
**Test**: Verify the Tasks page appears in navigation
**Steps**:
1. Open the application
2. Check that "Tasks" appears in the sidebar navigation between "Pipeline" and "Jobs"
3. Click on "Tasks" to navigate to the All Tasks page

**Expected Result**: Tasks page loads successfully with "Active Tasks" header

### 2. User Selector Test
**Test**: Verify user selector works and defaults to Nick
**Steps**:
1. Check the sidebar for "Testing as:" dropdown
2. Verify it shows "Nick" as selected by default
3. Change to different user (e.g., "Marina")
4. Navigate to Tasks page

**Expected Result**: 
- Dropdown shows "Nick" as default
- Can select different team members
- Selection persists across page navigation

### 3. Default Filter Test  
**Test**: Verify default filter is set to "My tasks"
**Steps**:
1. Navigate to the Tasks page
2. Check the "View" dropdown filter

**Expected Result**: Filter dropdown shows "My tasks" as the selected option (not "All tasks")

### 4. Company Column Test
**Test**: Verify company name column is displayed
**Steps**:
1. Navigate to the Tasks page
2. Look at the task table columns

**Expected Result**: Table shows columns in order: Done, Task, **Company**, Owner, Due, Notes

### 4. Task Display Test
**Test**: Verify tasks from different companies are shown
**Steps**:
1. Change filter from "My tasks" to "All tasks"
2. Look at the Company column values

**Expected Result**: Company column shows different company names for different tasks

### 5. Inline Editing Test
**Test**: Verify task editing works the same as company Tasks tab
**Steps**:
1. Click on a task title to edit it
2. Change the task text and click Save
3. Navigate to the company page and check the Tasks tab

**Expected Result**: 
- Task can be edited inline on All Tasks page
- Changes appear immediately in the company Tasks tab
- Same editing behavior as company-specific view

### 6. Task Completion Test
**Test**: Verify task completion syncs between views
**Steps**:
1. On All Tasks page, check the "Done" checkbox for a task
2. Fill in results when prompted
3. Navigate to the company page and check Tasks tab

**Expected Result**:
- Task is marked as completed on All Tasks page
- Results dialog appears for completion
- Task appears as completed in company Tasks tab
- Results are visible in both views

### 7. No Add Task Form Test
**Test**: Verify no task creation form is present
**Steps**:
1. Navigate to the All Tasks page
2. Look for any "Add Task" form or button

**Expected Result**: No task creation form or "Add Task" button is visible

### 8. Filter Functionality Test
**Test**: Verify all filters work correctly
**Steps**:
1. Change filter to "Active" - should show only active tasks
2. Change filter to "Completed" - should show only completed tasks  
3. Change filter to "Overdue" - should show only overdue active tasks
4. Change filter to "All tasks" - should show all tasks

**Expected Result**: Each filter correctly shows the appropriate subset of tasks

### 9. Data Synchronization Test
**Test**: Verify edits sync between All Tasks and company Tasks tabs
**Steps**:
1. On All Tasks page, edit a task (title, assignee, due date, notes)
2. Navigate to the company page and check Tasks tab
3. On company Tasks tab, edit the same task
4. Return to All Tasks page

**Expected Result**: All changes are immediately reflected in both views

### 10. Completed Tasks Section Test
**Test**: Verify completed tasks section shows tasks from all companies
**Steps**:
1. Complete a task from All Tasks page
2. Complete a different task from a company Tasks tab
3. Check the "Completed Tasks" expander on All Tasks page

**Expected Result**: Both completed tasks appear in the completed section with correct company names

### 11. Auto-Assignment Test
**Test**: Verify tasks auto-assign to current selected user
**Steps**:
1. Select "Marina" from "Testing as:" dropdown
2. Go to any company page and navigate to Tasks tab
3. Create a task without @mention (e.g., "Review financial projections")
4. Check the task owner in the table

**Expected Result**: Task owner shows "Marina" automatically

### 12. User Switch Test
**Test**: Verify switching users updates "My tasks" filter
**Steps**:
1. Select "Nick" from "Testing as:" dropdown
2. Go to Tasks page, verify "My tasks" shows Nick's tasks
3. Switch to "Marina" from dropdown
4. Go back to Tasks page, verify "My tasks" now shows Marina's tasks

**Expected Result**: "My tasks" filter shows different tasks based on selected user

## Key Features Verified
- ✅ Tasks page in navigation between Pipeline and Jobs
- ✅ User selector dropdown in sidebar with Nick as default
- ✅ "My tasks" default filter (index 4)
- ✅ Company name column in task table
- ✅ Inline editing with same functionality as company Tasks tab
- ✅ No add task form on All Tasks page
- ✅ Real-time synchronization between All Tasks and company Tasks tabs
- ✅ All task properties sync: status, outcome, notes, title, assignee, due_date
- ✅ Completed tasks section shows tasks from all companies
- ✅ Auto-assignment of tasks to current selected user
- ✅ User switching updates "My tasks" filter dynamically

## Notes
- All task operations use the same underlying data source (MongoDB in production, `st.session_state.tasks` in LOCAL_DEV)
- Both views call the same `update_task()` function ensuring perfect synchronization
- Session state keys use different prefixes to avoid conflicts between views
