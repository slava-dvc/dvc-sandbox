# Tasks Tab - Core Feature Smoke Tests

## Test Environment Setup

**Prerequisites:**
1. Start the Streamlit app: `cd /Users/viachealavrudenko/dvc-agent/synapse && streamlit run streamlit_app.py`
2. Navigate to a company page (e.g., select any company from the pipeline)
3. Click the "Tasks" tab

---

## Core Feature Tests

### Test 1: Add New Task
**Objective:** Verify the "Add Task" form works with natural language parsing

**Steps:**
1. In the Tasks tab, locate the "Add new task" input field at the top
2. Enter: `"Review financials on Friday @Marina"`
3. Click the "➕ Add" button

**Expected Results:**
- ✅ Success message: "✅ Task added: 'Review financials' → @Marina (Due: [date])"
- ✅ New task appears in the Active Tasks list
- ✅ Task shows: Title="Review financials", Assignee="Marina", Due date=Friday
- ✅ Form clears after submission

**Pass Criteria:** Task created with parsed assignee and due date

---

### Test 2: Task Completion Workflow
**Objective:** Verify the complete task flow from active to completed

**Steps:**
1. Find an active task in the list
2. Click the checkbox (☐) next to the task
3. In the completion form that appears:
   - Enter outcome: "Financial review completed. All metrics look good."
   - Click "✅ Complete"

**Expected Results:**
- ✅ Success message: "✅ Task completed!"
- ✅ Task disappears from Active Tasks list
- ✅ Task appears in "✅ Completed Tasks" expandable section
- ✅ Completed task shows strikethrough text and outcome

**Pass Criteria:** Task moves from active to completed with outcome saved

---

### Test 3: Task Editing (Inline Form)
**Objective:** Verify the inline edit form functionality

**Steps:**
1. Click on any active task card (the text area, not the checkbox)
2. In the edit form that appears:
   - Change task text to "Updated: Review marketing strategy"
   - Change assignee to "Nick"
   - Add notes: "Focus on Q4 campaign metrics"
   - Click "Save"

**Expected Results:**
- ✅ Success message: "✅ Task updated!"
- ✅ Form closes and returns to task card view
- ✅ Task card shows updated text and assignee
- ✅ When clicked again, form shows all updated values

**Pass Criteria:** All fields editable and changes persist

---

### Test 4: Task Filtering
**Objective:** Verify the task filter dropdown works correctly

**Steps:**
1. Ensure there are both active and completed tasks
2. Click the "Filter" dropdown (top right of tasks section)
3. Select "Active" from the dropdown
4. Observe the task list
5. Change filter to "Completed"
6. Observe the task list
7. Change filter back to "All tasks"

**Expected Results:**
- ✅ "Active" filter shows only active tasks
- ✅ "Completed" filter shows only completed tasks in expandable section
- ✅ "All tasks" shows both active and completed tasks
- ✅ Task counts update appropriately

**Pass Criteria:** Filters correctly show/hide tasks by status

---

### Test 5: Task Deletion
**Objective:** Verify task deletion works from edit form

**Steps:**
1. Click on any active task card to open edit form
2. Click the "Delete" button in the edit form
3. Confirm the deletion

**Expected Results:**
- ✅ Success message: "✅ Task deleted!"
- ✅ Task disappears from the task list immediately
- ✅ Task count decreases
- ✅ No trace of the deleted task remains

**Pass Criteria:** Task completely removed from system

---

## Test Execution Summary

**Total Tests:** 5
**Core Features Covered:**
- ✅ Task Creation (natural language parsing)
- ✅ Task Completion (workflow + outcomes)
- ✅ Task Editing (inline form)
- ✅ Task Filtering (status-based)
- ✅ Task Deletion (permanent removal)

**Success Criteria:** All 5 core features work without errors

---

## Quick Verification Checklist

After running all tests, verify:
- [ ] Can add tasks with natural language (assignee + date parsing)
- [ ] Can complete tasks with outcome tracking
- [ ] Can edit tasks inline with all fields
- [ ] Can filter tasks by status
- [ ] Can delete tasks permanently

**If all 5 tests pass, the Tasks tab core functionality is working correctly.**
