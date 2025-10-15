# Acceptance Criteria: Tasks Feature & Pipeline Summary

## Based on Conversation History Analysis

### 1. TASKS TAB - Requirements

#### Current Working State (commit d5a1a1d):
- **Data Layer**: Uses `app.dashboard.data.py` module with functions:
  - `get_tasks(company_id)` - Returns List[Task]
  - `add_task(company_id, title, due_date, assignee)` - Creates new task
  - `update_task(task_id, **kwargs)` - Updates existing task  
  - `delete_task(task_id)` - Deletes task

- **Task Model Fields** (from `app.shared.task.Task`):
  - `id`: str
  - `company_id`: str
  - `title`: str (NOT `text`)
  - `due_date`: date
  - `assignee`: str
  - `status`: "active" | "completed"
  - `created_at`: datetime

- **UI Components** (tasks.py):
  1. **Header**: "📋 Tasks"
  2. **Metrics Row** (3 columns):
     - Active Tasks count
     - Completed Tasks count
     - Total Tasks count
  3. **Add Task Form** (in st.form, clears on submit):
     - Task Title (text_input)
     - Assignee (text_input)
     - Due Date (date_input, default: today)
     - Submit button: "Add Task" (primary)
  4. **Active Tasks Section**:
     - Subheader: "🔄 Active Tasks"
     - List of active tasks (if any)
     - Else: "No active tasks" info message
  5. **Completed Tasks Section**:
     - Collapsible expander: "✅ Completed Tasks (N)"
     - List of completed tasks (show_actions=False)
     - Default: collapsed

- **Task List Display**:
  - Each task shows:
    - Status emoji (🟢 active / ✅ completed)
    - Title (clickable button to edit)
    - Assignee
    - Due date + color indicator
    - Action buttons (if show_actions=True):
      - ✓ Mark complete
      - 🗑 Delete (requires confirmation)
  
- **Due Date Colors**:
  - 🔴 Overdue (< 0 days)
  - 🟡 Due today (0 days)
  - 🟠 Due soon (1-3 days)
  - 🟢 Not urgent (4+ days)

- **Task Edit Form** (appears inline when title clicked):
  - Edit title, assignee, due date, status
  - Buttons: 💾 Save Changes | ❌ Cancel | 🗑 Delete Task
  - On save/cancel/delete → clear editing state + rerun

- **Mock Data** (data_mock.py):
  - Company "68e69a2dc32b590896149739" (Generous): 3 tasks
  - Company "68e69a2dc32b590896149740" (TechFlow): 2 tasks
  - Company "68e69a2dc32b590896149741" (HealthSync): 1 task

---

### 2. PIPELINE SUMMARY - Requirements

#### Current State (commit d5a1a1d):
**ISSUE**: The Pipeline Summary is using **hardcoded HTML mock data** instead of reading from real tasks!

**Location**: `app/dashboard/company.py` → `show_pipeline_summary(company)`

**What It Should Do**:
1. **Get tasks** from session state (via `get_tasks(company_id)`)
2. **Calculate summary** using `get_pipeline_summary(company_id)` from tasks.py
3. **Display** the summary with real data

**Summary Structure**:
- **Title**: "🧾 Pipeline Summary (Oct 03 – Oct 10) · [stats]"
- **Stats**: "✅ X completed · ⚠️ Y overdue · 🗓️ Z active"
- **Collapsed by default**: `expanded=False`

**Summary Content** (when expanded):
1. **Last updated**: "Updated today" / "Updated X days ago"
2. **Last discussed**: Bullet list of tasks completed in past 7 days
3. **Outcome**: Bullet list of corresponding outcomes/notes
4. **Next step**: "→ **Task title** by @Assignee [Overdue pill if overdue]"

**The `get_pipeline_summary()` function should**:
- Find all tasks with `done==True` AND `completed_at >= today - 7 days`
- Sort by `completed_at` (most recent first)
- Return dict with:
  ```python
  {
      'last_discussed': ["Task 1 title", "Task 2 title", ...],
      'outcomes': ["Outcome 1", "Outcome 2", ...],
      'next_step': "Next active task title",
      'next_step_assignee': "@Name",
      'next_step_due': date,
      'active_tasks_count': int,
      'overdue_count': int,
      'completed_count': int,
      'total_tasks': int,
      'last_updated': date  # most recent completed_at or created_at
  }
  ```

**If no tasks exist**:
- Still show summary structure
- Empty fields (no "No tasks" message in summary itself)
- Show stats as "0 active" etc.

---

### 3. CRITICAL ISSUES TO FIX

1. **tasks.py** is importing from wrong modules
   - ❌ Current: Tries to use session state directly
   - ✅ Should: Import from `app.dashboard.data` module

2. **Pipeline Summary uses hardcoded data**
   - ❌ Current: Hardcoded HTML with fake tasks
   - ✅ Should: Call `get_pipeline_summary(company_id)` and render real data

3. **Missing functions** in tasks.py:
   - Need: `_ensure_tasks_initialized(company_id)`
   - Need: `TASKS_STATE_KEY` constant
   - BUT these should be in `data.py`, not `tasks.py`!

4. **Task model mismatch**:
   - ❌ Current code uses `task.text`, `task.done`
   - ✅ Should use `task.title`, `task.status`

---

### 4. IMPLEMENTATION PLAN

**Step 1**: Restore `tasks.py` from working commit d5a1a1d ✅ DONE

**Step 2**: Verify `data.py` has correct imports and functions

**Step 3**: Fix `show_pipeline_summary()` in company.py to use real data

**Step 4**: Test in browser:
- Navigate to Generous company
- Check Tasks tab shows 3 mock tasks
- Check Pipeline Summary shows real task data
- Try adding a new task
- Try completing a task
- Verify summary updates

---

### 5. ACCEPTANCE CRITERIA CHECKLIST

#### Tasks Tab:
- [ ] Shows correct metrics (Active/Completed/Total)
- [ ] Add task form works and reloads page on submit
- [ ] Active tasks displayed with correct emoji/colors
- [ ] Completed tasks in collapsible expander
- [ ] Click task title opens edit form
- [ ] Edit form can update title/assignee/date/status
- [ ] Delete requires confirmation
- [ ] Mark complete button works
- [ ] Due date colors show correctly

#### Pipeline Summary:
- [ ] Summary displays between header and tabs
- [ ] Collapsed by default
- [ ] Shows correct date range (last 7 days)
- [ ] Stats show real counts from tasks
- [ ] "Last discussed" lists tasks completed in last 7 days
- [ ] "Outcome" lists corresponding outcomes
- [ ] "Next step" shows earliest active task
- [ ] Overdue pill shows only for overdue tasks
- [ ] Updates automatically when tasks change








