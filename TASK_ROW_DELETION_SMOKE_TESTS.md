# Task Row Deletion Smoke Tests

## Overview
Tests for the new native row deletion feature using `st.data_editor` with `num_rows="dynamic"`. This provides built-in trash icons for each row.

## Prerequisites
1. Navigate to a company page in the Synapse dashboard
2. Go to the "Tasks" tab
3. Ensure you have at least 1 active task and 1 completed task for testing

---

## Test 1: Active Tasks Row Deletion

### Steps to Test:
1. Go to the Tasks tab on any company page
2. Look at the active tasks table
3. **You should see trash icons (🗑️) on the right side of each active task row**
4. Click the trash icon for any active task

### Expected Results:
- The row is removed from the table immediately (Streamlit's native behavior)
- A confirmation dialog appears: "⚠️ Delete task: '[task title]'?"
- Two buttons appear: "Yes, Delete" (primary) and "Cancel" (secondary)
- Clicking "Cancel" restores the row and hides the confirmation
- Clicking "Yes, Delete" permanently deletes the task and shows "Task deleted!" success message
- The task is removed from the database and the page refreshes

---

## Test 2: Completed Tasks Row Deletion

### Steps to Test:
1. Scroll down to the "✅ Completed Tasks" expandable section
2. Expand the completed tasks section
3. **You should see trash icons (🗑️) on the right side of each completed task row**
4. Click the trash icon for any completed task

### Expected Results:
- The row is removed from the table immediately (Streamlit's native behavior)
- A confirmation dialog appears: "⚠️ Delete completed task: '[task title]'?"
- Two buttons appear: "Yes, Delete" (primary) and "Cancel" (secondary)
- Clicking "Cancel" restores the row and hides the confirmation
- Clicking "Yes, Delete" permanently deletes the task and shows "Task deleted!" success message
- The task is removed from the database and the page refreshes

---

## Test 3: Uncomplete Checkbox (Still Works)

### Steps to Test:
1. In the completed tasks section, find the "Done" checkbox column
2. Uncheck the checkbox for any completed task

### Expected Results:
- The checkbox unchecks immediately
- The page refreshes automatically
- The task disappears from the completed tasks section
- The task reappears in the active tasks section
- The task retains its title, owner, due date, and notes
- The task's outcome/results are cleared (reset to empty)
- **This functionality remains unchanged from before**

---

## Test 4: Multiple Operations

### Steps to Test:
1. Delete 1 active task using trash icon
2. Uncomplete 1 task using checkbox in completed section
3. Delete 1 completed task using trash icon

### Expected Results:
- All operations work independently
- Each deletion shows its own confirmation dialog
- Task counts update correctly:
  - Active task count decreases when deleting or uncompleting
  - Completed task count decreases when deleting
  - Completed task count increases when completing tasks

---

## Test 5: Prevent Adding New Rows

### Steps to Test:
1. Try to add a new row using the "+" button at the bottom of the active tasks table
2. Try to add a new row using the "+" button at the bottom of the completed tasks table

### Expected Results:
- Warning message appears: "Adding new tasks is not allowed here. Use the 'Add new task' form above."
- The new row is removed and table returns to original state
- Users must use the "Add new task" form at the top to create new tasks

---

## Test 6: Cancel Operations

### Steps to Test:
1. Click trash icon on an active task, then click "Cancel"
2. Click trash icon on a completed task, then click "Cancel"

### Expected Results:
- Both cancel operations restore the deleted rows
- No changes are made to the database
- The confirmation dialogs disappear
- Tasks remain in their original state

---

## Visual Changes to Expect

### Before (Old Implementation):
- Separate "Actions" section with delete buttons below the table
- Delete buttons were positioned outside the table

### After (New Implementation):
- **Trash icons (🗑️) appear directly on each row** - this is the key visual change
- **No separate actions section** - everything is inline with the table
- **Cleaner, more professional appearance** - follows standard data editing patterns
- **Consistent with other data editing apps** - users will immediately understand how to delete rows

---

## Edge Cases to Verify

### Edge Case 1: Last Active Task
- Delete the last active task using trash icon
- Expected: "No active tasks" message appears, completed tasks section still works

### Edge Case 2: Last Completed Task
- Delete the last completed task using trash icon
- Expected: Completed tasks section becomes empty

### Edge Case 3: Rapid Operations
- Try to delete multiple tasks rapidly
- Expected: Each deletion shows its own confirmation dialog, no conflicts

### Edge Case 4: Adding New Rows
- Try to add new rows using the + button
- Expected: Warning message appears and rows are removed, directing users to use the form above

---

## Success Criteria

✅ Trash icons appear on the right side of each table row
✅ Clicking trash icon removes row and shows confirmation dialog
✅ Confirmation shows task title for clarity
✅ Cancel button restores the row
✅ Yes, Delete button permanently deletes the task
✅ Uncomplete checkbox still works for returning tasks to active
✅ No separate "Actions" section needed
✅ Clean, professional appearance
✅ No errors occur during any operation
✅ Task counts are accurate

---

## Technical Implementation Notes

- Uses `num_rows="dynamic"` in `st.data_editor`
- Row deletion detection: compares `len(edited_df) < len(df)`
- Deleted task identification: `original_ids - remaining_ids`
- Confirmation using session state flags
- Database deletion via `delete_task(task_id)`
- Automatic page refresh after operations
