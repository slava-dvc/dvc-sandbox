# Task Empty Title Deletion Smoke Tests

## Overview
Tests for the new delete-by-clearing-title feature. Users can delete tasks by clearing the task name field, which triggers a confirmation dialog.

## Prerequisites
1. Navigate to a company page in the Synapse dashboard
2. Go to the "Tasks" tab
3. Ensure you have at least 1 active task and 1 completed task for testing

---

## Test 1: Delete Active Task by Clearing Title

### Steps to Test:
1. Go to the Tasks tab on any company page
2. Find an active task in the table
3. Click on the task title field (in the "Task" column)
4. Select all text (Ctrl+A or Cmd+A) and delete it, OR backspace until the field is empty
5. Click outside the field or press Enter to trigger the edit

### Expected Results:
- Confirmation dialog appears: "⚠️ Delete task: '[original task text]'? (Title was cleared)"
- Two buttons appear: "Yes, Delete" (primary/blue) and "Cancel" (secondary)
- Dialog shows the original task text for clarity
- Clicking "Yes, Delete" removes the task from database and shows "Task deleted!" success message
- Clicking "Cancel" restores the original task title and hides the dialog
- Page refreshes after either action

---

## Test 2: Delete Completed Task by Clearing Title

### Steps to Test:
1. Scroll down to the "✅ Completed Tasks" expandable section
2. Expand the completed tasks section
3. Find a completed task in the table
4. Click on the task title field (in the "Task" column)
5. Select all text and delete it, OR backspace until the field is empty
6. Click outside the field or press Enter to trigger the edit

### Expected Results:
- Confirmation dialog appears: "⚠️ Delete completed task: '[original task text]'? (Title was cleared)"
- Two buttons appear: "Yes, Delete" (primary/blue) and "Cancel" (secondary)
- Dialog shows the original task text for clarity
- Clicking "Yes, Delete" removes the task from database and shows "Task deleted!" success message
- Clicking "Cancel" restores the original task title and hides the dialog
- Page refreshes after either action

---

## Test 3: Cancel Deletion

### Steps to Test:
1. Clear the title of any task (active or completed)
2. When confirmation dialog appears, click "Cancel"

### Expected Results:
- Dialog disappears immediately
- Original task title is restored in the field
- Task remains in the database unchanged
- No changes are made to the task

---

## Test 4: Multiple Tasks Deletion

### Steps to Test:
1. Clear the title of an active task and confirm deletion
2. Clear the title of a completed task and confirm deletion

### Expected Results:
- Each deletion shows its own confirmation dialog
- Both tasks are successfully deleted
- Task counts update correctly:
  - Active task count decreases
  - Completed task count decreases
- No conflicts between the two operations

---

## Test 5: Other Edits Still Work

### Steps to Test:
1. Edit a task title to new text (don't clear it completely)
2. Change the owner of a task
3. Add notes to a task
4. Check/uncheck the completed checkbox

### Expected Results:
- All normal editing functions work as expected
- No deletion confirmation dialogs appear
- Changes are saved normally
- Only clearing the title completely triggers deletion

---

## Edge Cases to Verify

### Edge Case 1: Already Empty Title
- Try to clear a task title that is already empty
- Expected: No deletion dialog appears (only triggers when going from non-empty to empty)

### Edge Case 2: Whitespace Only
- Replace task title with only spaces
- Expected: Deletion dialog appears (spaces are stripped, so it's considered empty)

### Edge Case 3: Rapid Operations
- Clear multiple task titles rapidly
- Expected: Each gets its own confirmation dialog, no conflicts

### Edge Case 4: Edit Other Fields While Dialog Open
- Clear a task title to trigger dialog
- Try to edit another task while dialog is open
- Expected: Dialog remains open, other edits are blocked until dialog is resolved

---

## Visual Behavior to Expect

### Before (No Delete Feature):
- Clearing task title would just leave it empty
- No way to delete tasks except through separate delete buttons

### After (New Delete Feature):
- **Clearing task title triggers immediate confirmation dialog**
- Dialog appears inline with clear messaging
- Shows original task name for context
- Clean two-button interface (Yes/Cancel)
- Task title is restored if cancelled

---

## Success Criteria

✅ Clearing active task title shows confirmation dialog
✅ Clearing completed task title shows confirmation dialog
✅ Dialog shows original task text for context
✅ "Yes, Delete" button permanently deletes the task
✅ "Cancel" button restores original title and hides dialog
✅ Success message appears after deletion
✅ Other editing functions work normally when title is not cleared
✅ No conflicts when clearing multiple task titles
✅ Already empty titles don't trigger deletion
✅ Whitespace-only titles trigger deletion (spaces are stripped)

---

## User Experience Benefits

1. **Intuitive**: Users naturally understand that clearing text means deletion
2. **Safe**: Confirmation dialog prevents accidental deletions
3. **Clear**: Shows exactly which task will be deleted
4. **Reversible**: Cancel button restores original text
5. **Discoverable**: Users will accidentally discover this feature while editing
6. **No Extra UI**: Uses existing task title field, no additional buttons needed

---

## Technical Implementation Notes

- Detection: `orig_title and not edited_title` (was not empty, now is empty)
- Session state flags: `confirm_delete_empty_{task_id}` and `confirm_delete_empty_completed_{task_id}`
- Early return: Prevents processing other edits until deletion is resolved
- Database deletion: Uses existing `delete_task(task_id)` function
- Page refresh: Automatic rerun after deletion or cancellation
- **Fix Applied**: Prevented session state update when deletion dialog is shown to avoid overwriting original title

## Debug Fix Applied

**Issue**: Deletion confirmation dialog wasn't appearing when clearing task titles.

**Root Cause**: The session state was being updated with the empty title before the deletion check, causing both DataFrames to have empty titles on subsequent runs.

**Solution**: 
1. Modified edit handlers to return `deletion_triggered` boolean
2. Only update session state if no deletion was triggered
3. This preserves the original title for comparison until deletion is resolved
