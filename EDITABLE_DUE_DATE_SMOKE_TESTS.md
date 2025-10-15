# Editable Due Date Column - Smoke Tests

## Implementation Summary

The "Due" column in the Active Tasks table is now directly editable using `st.column_config.DateColumn`. Users can click on any due date cell to open a native date picker, select dates from the calendar, or type dates manually. Changes are persisted immediately.

### Changes Made

1. **tasks.py**: Modified `show_tasks_data_editor` column configuration to use `DateColumn` for `due_date`
2. **all_tasks.py**: Applied same `DateColumn` configuration for consistency
3. **Column Layout**: 
   - `due_date`: Editable date picker (DateColumn)
   - `due_display`: Hidden (no status column visible)

## Smoke Test Instructions

### Test 1: Date Picker Appearance
1. Navigate to any company's Tasks tab
2. Look for the "Due" column in the task table
3. **Expected**: Clicking on any due date cell should open a date picker calendar
4. **Expected**: Date picker should show current due date pre-selected

### Test 2: Calendar Selection
1. Click on a due date cell to open the date picker
2. Select a different date from the calendar
3. **Expected**: Date should update immediately in the table
4. **Expected**: Date should be displayed in the format "MMM DD, YYYY" (e.g., "Dec 25, 2024")

### Test 3: Manual Date Entry
1. Click on a due date cell
2. Type a date manually (e.g., "Dec 25, 2024")
3. **Expected**: Date should update immediately
4. **Expected**: Date should be displayed in the format "MMM DD, YYYY"

### Test 4: Past Date Prevention
1. Click on a due date cell
2. Try to select a date in the past
3. **Expected**: Past dates should be disabled/unselectable in the calendar
4. **Expected**: If typing manually, validation should prevent past dates

### Test 5: All Tasks View
1. Navigate to the main "Tasks" page (All Tasks view)
2. Repeat tests 1-4
3. **Expected**: Same functionality should work in the All Tasks view

### Test 6: Persistence
1. Edit a due date in the Tasks tab
2. Navigate away and back to the same company
3. **Expected**: Due date change should be persisted

### Test 7: Date Display Format
1. Set a due date to today
2. **Expected**: Should show today's date in "MMM DD, YYYY" format
3. Set due date to tomorrow
4. **Expected**: Should show tomorrow's date in "MMM DD, YYYY" format
5. Set due date to next week
6. **Expected**: Should show the date in "MMM DD, YYYY" format (e.g., "Dec 25, 2024")

## Test Data for Manual Testing

Use these sample inputs to test various scenarios:

### Valid Date Formats to Type:
- "Dec 25, 2024"
- "12/25/2024"
- "2024-12-25"
- "25 Dec 2024"

### Test Scenarios:
1. **Today's date**: Should show today's date in "MMM DD, YYYY" format
2. **Tomorrow**: Should show tomorrow's date in "MMM DD, YYYY" format
3. **This week**: Should show date in "MMM DD, YYYY" format
4. **Next month**: Should show full date in "MMM DD, YYYY" format
5. **Past date**: Should be prevented/rejected

## Expected Behavior

✅ **Working Correctly:**
- Date picker opens when clicking due date cells
- Calendar selection updates immediately
- Manual typing works with various date formats
- Past dates are prevented
- Dates display in "MMM DD, YYYY" format
- Changes persist across navigation
- Works in both company Tasks and All Tasks views

❌ **Issues to Report:**
- Date picker doesn't open
- Changes don't persist
- Past dates can be selected
- Date format is incorrect
- Different behavior between Tasks and All Tasks views

## Technical Notes

- Uses `st.column_config.DateColumn` with `min_value=date.today()`
- Format: "MMM DD, YYYY" (e.g., "Dec 25, 2024")
- Immediate persistence via existing `handle_task_edits` logic
- No separate save button required - auto-saves on change
