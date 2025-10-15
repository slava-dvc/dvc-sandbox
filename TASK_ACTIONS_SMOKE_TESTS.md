# Task Actions Smoke Tests

## Overview
Tests for the new Delete action (active tasks) and uncomplete checkbox (completed tasks) features.

## Prerequisites
1. Navigate to a company page in the Synapse dashboard
2. Go to the "Tasks" tab
3. Ensure you have at least 1 active task and 1 completed task for testing

---

## Test 1: Delete Action for Active Tasks

### Steps to Test:
1. Go to the Tasks tab on any company page
2. Look at the active tasks table - you should see tasks listed
3. Below the table, you should see "Actions" section with "🗑️ Delete" buttons for each task
4. Click the "🗑️ Delete" button for any task

### Expected Results:
- A confirmation message appears: "Delete '[task title]'?"
- Two buttons appear: "Yes" (primary) and "No"
- Clicking "No" cancels the deletion and hides the confirmation
- Clicking "Yes" deletes the task and shows "Task deleted!" success message
- The task is removed from the active tasks list
- The page refreshes to show updated task list

---

## Test 2: Uncomplete Checkbox for Completed Tasks

### Steps to Test:
1. Complete a task first (if needed): check the "Done" checkbox on any active task and add results
2. Scroll down to the "✅ Completed Tasks" expandable section
3. Expand the completed tasks section
4. You should see a "Done" checkbox column (first column) with all checkboxes checked
5. Uncheck the "Done" checkbox for any completed task

### Expected Results:
- The checkbox unchecks immediately (no confirmation dialog)
- The page refreshes automatically
- The task disappears from the completed tasks section
- The task reappears in the active tasks section at the top
- The task retains its title, owner, due date, and notes
- The task's outcome/results are cleared (reset to empty)
- The task's status is set back to "active"

---

## Test 3: Delete Confirmation Cancel Flow

### Steps to Test:
1. Click "🗑️ Delete" on an active task
2. Click "No" to cancel

### Expected Results:
- The confirmation dialog disappears
- The task remains in the active tasks list
- No changes are made

---

## Test 4: Multiple Task Operations

### Steps to Test:
1. Complete 2 tasks from active
2. Uncomplete 1 task from completed
3. Delete 1 active task

### Expected Results:
- All operations work independently
- Task counts update correctly:
  - Active task count decreases when completing or deleting
  - Active task count increases when uncompleting
  - Completed task count increases when completing
  - Completed task count decreases when uncompleting
- No conflicts or errors occur

---

## Edge Cases to Verify

### Edge Case 1: Last Active Task
- Delete or complete the last active task
- Expected: "No active tasks" message appears, completed tasks section still works

### Edge Case 2: Last Completed Task
- Uncomplete the last completed task
- Expected: Completed tasks section becomes empty or shows "No completed tasks"

### Edge Case 3: Rapid Operations
- Click delete multiple times rapidly
- Expected: Confirmation only shows for one task at a time, no duplicate dialogs

---

## Known Behavior

1. **Delete requires confirmation** - Two-step process to prevent accidental deletion
2. **Uncomplete is instant** - No confirmation needed since it's an undo operation
3. **Outcomes are cleared on uncomplete** - When returning a task to active, the outcome field is reset
4. **Session state persists** - Confirmation dialogs survive page reruns until dismissed

---

## Success Criteria

✅ Delete buttons appear for all active tasks
✅ Delete confirmation shows with Yes/No options
✅ Tasks can be deleted after confirmation
✅ Completed tasks show checkboxes in "Done" column
✅ Unchecking moves task back to active instantly
✅ No errors occur during any operation
✅ UI updates correctly after each operation
✅ Task counts are accurate

