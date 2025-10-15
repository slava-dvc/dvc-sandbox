# Final Consolidated Acceptance Criteria
**Based on: Conversation History + Screenshots + User's ACs**

## ✅ PIPELINE SUMMARY — Acceptance Criteria

### **Functional Requirements**

1. **Rolling Window Logic:**
   - Shows tasks completed within the last 7 days (based on `completed_at` timestamp)
   - Automatically updates as new tasks are completed or time progresses

2. **Header Metrics:**
   - Dynamic summary bar: `🧾 Pipeline Summary (Oct 03 – Oct 10) · ✅ X completed · ⚠️ Y overdue · 🗓️ Z active`
   - Counts update in real time from current company's task list

3. **Sections Inside Expander:**
   - **Last discussed:** Lists task names of all tasks completed within the last 7 days
   - **Outcome:** Lists the notes (outcomes/decisions) attached to those completed tasks
     - If missing → show "(no notes)"
   - **Next step:**
     - Shows the next active task by earliest due date
     - Includes assignee (@Name) and due status badge (Overdue/Today/Tomorrow/This Week/Future)
     - If no active tasks → shows "→ Add the next step below."

4. **Automatic Refresh:**
   - Updating or completing tasks immediately reflects in summary after `st.rerun()`

5. **Sorting:**
   - Completed tasks shown newest → oldest
   - Next step chosen by earliest due date

### **Visual/UI Requirements**

1. **Compact Header (Always Visible):**
   - Inside a Streamlit expander label (dark background friendly)
   - "Last updated: Today" shown in gray caption below header

2. **Typography:**
   - Section titles ("Last discussed", "Outcome", "Next step") use small-caps styling
   - Bullet points rendered via Markdown with reduced indentation (~1.4rem)

3. **Color Tags:**
   - Due buckets map to semantic colors:
     - **Overdue** = red (`#b24747`)
     - **Today** = green (`#2e7d32`) 
     - **Tomorrow** = brown (`#8d6e63`)
     - **This Week** = purple (`#7b1fa2`)
     - **Future** = gray (no color)

4. **Empty States:**
   - If no completed tasks → show "– No completed tasks in the past week."
   - If no outcomes → show "– (no outcomes)" under Outcome

5. **Styling Details (from Screenshots):**
   - Soft overdue pill: `background: #fff2f2; color: #b24747; border: 1px solid #ffdede; padding: 1px 6px; border-radius: 8px; margin-left: 6px; font-size: 11px;`
   - Thin dividers between sections (50% opacity)
   - Proper spacing and rounded bottom corners

### **Non-Functional Requirements**

- Must run fully inside Streamlit (no JS or DB dependency)
- Render time < 1s for ≤ 100 tasks
- All layout uses native Streamlit widgets (expander, markdown, caption)

---

## ✅ TASKS TAB — Acceptance Criteria

### **Functional Requirements**

1. **Add Task:**
   - Input parses free-form text like "setup call 10/11 @Nick"
   - Extracts:
     - **text** → "setup call"
     - **due** → parsed date (10/11)
     - **assignee** → "Nick"
   - On Add → task saved and immediately appears in list

2. **Filter Dropdown:**
   - Options: **All**, **Mine**, **Overdue**, **Completed**
   - Filtering updates task list dynamically
   - **"Mine" Filter Logic:** Shows only tasks assigned to current user (@Nick, @Marina, @Slava), regardless of status

3. **Task Card Fields:**
   - text, due date, assignee, created by, created on metadata shown
   - Buttons: ✏️ Edit, ✅ Complete, 🗑️ Delete
   - Completed tasks appear only in Completed filter (or when toggled to All)

4. **Edit Task:**
   - Opens inline form with editable fields (text, assignee, due, notes)
   - **Form Fields:**
     - Task text field with help icon
     - Assignee field with help icon
     - Due date field with help icon (YYYY/MM/DD format)
     - Notes section with sub-label and placeholder
   - **Action Buttons:** Red Save (💾), Dark gray Cancel (✖️), Dark gray Delete (🗑️)
   - Save → updates task; Cancel → discards

5. **Complete Task:**
   - Opens modal: "Complete Task: [Title]"
   - **Modal Fields:**
     - Large notes textarea (optional)
     - "Outcome / Decision (optional)" input with placeholder examples
   - **Action Buttons:** Red Complete (✅), Dark gray Cancel (✖️)
   - Save → sets `status = "completed"`, stores notes as outcome, stamps `completed_at = UTC now`
   - Completed task moves to Completed section

6. **Delete Task:**
   - Immediate removal from task list with rerun

7. **Due Bucket Logic:**
   - **Overdue** (< today) = Red text
   - **Today** = Green text  
   - **Tomorrow** = Brown text
   - **This Week** (≤ 7 days ahead) = Purple text
   - **Future** (> 7 days ahead or None) = No color

8. **Persistence:**
   - Stored in `st.session_state["tasks_by_company"][company_id]`
   - Each task unique id
   - All changes survive until session reset

### **Visual/UI Requirements**

1. **Layout:**
   - Add-bar (input + Add button) aligned left; Filter dropdown right (`st.columns([4, 1.3])`)
   - Tasks grouped with bordered containers; Completed tasks shaded green
   - **Order:** Input box first, filter second, task list third

2. **Task Display:**
   - **Active Tasks Section:** "Active Tasks (X)" header with clipboard icon and count
   - **Completed Tasks Section:** "Completed Tasks (X)" expandable header with green checkmark icon
   - **Individual Task Cards:**
     - Bold white task titles
     - Metadata: "Due: [Date] • [Assignee] • Created by [Creator] on [Date]"
     - Color-coded due dates (Red/Green/Brown/Purple)
     - Person icons for assignee/creator
     - Action buttons (Edit/Complete/Revert) right-aligned

3. **Forms:**
   - Edit and Complete render inline forms using `st.form()` to keep state stable
   - Dark theme styling throughout

4. **Icons/Buttons:**
   - Consistent emoji set (✏️, ✅, 🗑️, 💾, ✖️, ↩️)
   - Yellow pencil for edit, checkmark for complete, curved arrow for revert

5. **Responsive Sizing:**
   - Works in wide layout; no horizontal scroll for ≤ 100 tasks

6. **Empty States:**
   - If no tasks → show "(No active tasks yet)" placeholder
   - If no completed tasks → show appropriate empty state

### **Non-Functional Requirements**

- No external JS/CSS beyond minimal injected CSS
- All operations idempotent; reruns safe
- Validation: empty text ignored; bad date parsed → stored as None
- Error handling: invalid input → no crash

---

## ✅ DATA MODEL REQUIREMENTS

### **Task Model Updates:**
```python
class Task:
    id: str
    company_id: str
    text: str                    # Parsed from input
    assignee: str                # Parsed from @mention
    due_date: Optional[date]     # Parsed from MM/DD format
    status: Literal["active", "completed"]
    outcome: Optional[str]       # From completion form
    notes: Optional[str]         # From edit form
    created_at: datetime
    created_by: str
    completed_at: Optional[datetime]  # For 7-day window logic
```

### **Mock Data Requirements:**
- Tasks with `completed_at` timestamps (last 7 days)
- Tasks with `outcome` and `notes` fields
- Mix of active/completed/overdue tasks for testing
- Proper assignee examples (@Nick, @Marina, @Slava)

---

## ✅ IMPLEMENTATION PRIORITY

### **Phase 1: Foundation**
1. Update Task data model
2. Update mock data with new fields
3. Implement single input parsing logic

### **Phase 2: Tasks Tab Core**
1. Build completion modal
2. Build edit form
3. Implement colored due dates (replace emojis)
4. Create active/completed task displays

### **Phase 3: Pipeline Summary**
1. Implement 7-day window logic
2. Build visual summary with exact styling from screenshots
3. Add automatic refresh functionality

### **Phase 4: Integration & Polish**
1. Add filtering functionality
2. Apply CSS styling and dark theme
3. Test against screenshots and ACs

---

## ✅ VALIDATION CHECKLIST

### **Tasks Tab:**
- [ ] Single input parsing works: "setup call 10/11 @Nick"
- [ ] Colored due dates display correctly (Red/Green/Brown/Purple)
- [ ] Completion modal opens with proper fields and styling
- [ ] Edit form opens with all fields and help icons
- [ ] "Mine" filter shows only assigned tasks
- [ ] Stats display shows: "Active Tasks (X)" (KEEP per user decision)
- [ ] Completed tasks show green outcome boxes
- [ ] Action buttons work correctly (Edit/Complete/Delete/Revert)

### **Pipeline Summary:**
- [ ] 7-day window logic works correctly
- [ ] Header shows dynamic counts and date range
- [ ] "Last discussed" lists completed task names
- [ ] "Outcome" lists corresponding notes
- [ ] "Next step" shows next active task with due status
- [ ] Soft overdue pill styling matches screenshot
- [ ] Auto-refreshes on task changes
- [ ] Collapsed by default

### **Visual Validation:**
- [ ] Matches screenshots exactly
- [ ] Dark theme consistent throughout
- [ ] Proper spacing and typography
- [ ] Icons and buttons styled correctly
- [ ] Expandable sections work properly







