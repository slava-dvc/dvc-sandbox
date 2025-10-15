# REAL Acceptance Criteria - Extracted from Conversation History

## CONVERSATION ANALYSIS

### Initial Context
- User started by asking to revert to specific commits (cbcb065, bd31efa)
- User then requested to "completely remove the Task feature tab and all related code"
- After removal, user requested to RE-IMPLEMENT the Tasks tab with specific new features

---

## TASKS TAB - Requirements from Conversation

### Original Request (from conversation):
**User said:** "Implement a Tasks tab/section into each Deal page"

### Core Features Requested:
1. **Allow users to add and complete tasks**
2. **Work reliably under Streamlit's rerun model using `st.session_state`**
3. **Use only built-in Streamlit widgets** (no external DB or custom components)
4. **Task creation like Comments tab** - typing task name and pressing Enter should create without full page reload

### Task Fields Requested:
1. **Assignee field** - parsed from input using `@mention`
   - Example: "setup call with founders tomorrow @Tony"
   - Parse `@Tony` as assignee

2. **Due date field** - parsed from input using `MM/DD` format
   - Example: "setup call with Tony on 10/11 @Nick"
   - Parse `10/11` as due date

3. **Due date color coding** (SPECIFIC REQUEST):
   - ❌ NOT emoji indicators
   - ✅ **Colored text** based on:
     - **Red** - Overdue
     - **Green** - Today
     - **Brown** - Tomorrow
     - **Purple** - Next 2-7 days
     - **No color** - 8+ days

4. **Task metadata**:
   - `created_on` (timestamp)
   - `created_by` (user who created it)

### Filter Dropdown Requested:
Options: "All", "Active", "Completed", "Overdue", "Mine"

**CRITICAL "Mine" Filter Behavior:**
- **User explicitly said:** "The 'Mine' filter should specifically show only tasks assigned to the current logged-in user (e.g., @Nick, @Marina, @Slava)"
- **Regardless of status** (active, overdue, due later)
- **Should NOT show tasks created by the user** if they are not assigned to them

### Inline Editing Requested:
- Update task text, due date, and assignee directly in UI
- Can add notes to a task in edit mode
- Notes should be saved and viewable by anyone

### Task Completion Feature:
- When completing a task, prompt for **one-line "Outcome / Decision"**
- Store in notes metadata
- User later requested: **Remove "Quick Outcome Selection" buttons**, keep only custom text input

### Task Completion Modal - Requirements from Screenshot:
**Visual & Functional Requirements:**

1. **Complete Task Modal/Form:**
   - **Title:** "Complete Task: [Task Title]" (e.g., "Complete Task: Get technical architecture documentation")
   - **General Notes (Optional):** Large, multi-line text input area for additional context
   - **Outcome / Decision Field (Optional):**
     - Label: "Outcome / Decision (optional):"
     - Placeholder: "e.g., 'Moved to Diligence', 'Passed', 'Waiting on founder reply'"
     - Single-line text input field
   - **Action Buttons:**
     - **"Complete Task" Button:** Red background, white text, green checkmark icon (✔)
     - **"Cancel" Button:** Dark gray background, white text, red 'X' icon (X)
   - **Styling:** Dark theme with clear white text, distinct button styling

### Task Edit Form - Requirements from Screenshot:
**Visual & Functional Requirements:**

1. **Edit Task Modal/Form:**
   - **Title:** "Edit Task" prominently displayed
   - **Form Fields:**
     - **Task Text Field:** Label "Task text:", dark gray input with help icon
     - **Assignee Field:** Label "Assignee:", dark gray input with help icon  
     - **Due Date Field:** Label "Due date:", dark gray input with help icon (YYYY/MM/DD format)
     - **Notes Section:** Label "Notes:", sub-label "Add notes, updates, or context:", larger textarea with placeholder
   - **Action Buttons (Bottom):**
     - **Save Button:** Red background, white floppy disk icon, "Save" text
     - **Cancel Button:** Dark gray background, red 'X' icon, "Cancel" text
     - **Delete Button:** Dark gray background, white trash can icon, "Delete" text

### Completed Tasks Display - Requirements from Screenshot:
**Visual & Functional Requirements:**

1. **Completed Tasks Section:**
   - **Header:** "Completed Tasks (3)" with:
     - Downward chevron icon (expandable)
     - Green square with white checkmark icon
     - Task count in parentheses
   - **Expandable/Collapsible:** Like st.expander

2. **Individual Completed Task Display:**
   - **Task Title:** White text (e.g., "Check references from previous investors")
   - **Outcome Display:**
     - Green rectangular box below title
     - Format: "✅ Outcome: [Description]" in white text
     - Example: "✅ Outcome: All references positive. Team execution is strong."
   - **Metadata Line:**
     - Format: "Due: [Date] • [Assignee] • Created by [Creator] on [Date]"
     - **Due Date Styling:** Red text for overdue tasks
     - Bullet separators (•) between elements
   - **Action Buttons (Right-aligned):**
     - **Edit Button:** Yellow pencil icon (✏️)
     - **Revert Button:** Curved arrow icon (↩️) for undoing completion

3. **Footer:** "Created X days ago" at bottom

### Active Tasks Display - Requirements from Screenshot:
**Visual & Functional Requirements:**

1. **Active Tasks Section:**
   - **Header:** "Active Tasks (4)" with clipboard icon and count
   - **Task List:** Distinct card-like elements

2. **Individual Active Task Display:**
   - **Task Title:** Bold white text (e.g., "Draft IC memo for investment committee")
   - **Metadata Line:** Lighter gray text with:
     - **Due Date:** Color-coded text:
       - **Red** for overdue (e.g., "Oct 08")
       - **Green** for today (e.g., "Oct 10")
       - **Brown** for tomorrow (e.g., "Oct 11") 
       - **Purple** for next 2-7 days (e.g., "Oct 15")
     - **Assignee:** Name with person icon (e.g., "Marina", "Nick", "Slava")
     - **Created By:** "Created by [Name] on [Date]" with person icon
     - **Separators:** Bullet points (•) between elements
   - **Action Buttons (Right-aligned):**
     - **Edit Button:** Yellow pencil icon (✏️)
     - **Complete Button:** Checkmark icon

3. **Task Ordering:** Recently added first (by creation date)

### Main Tasks Interface - Requirements from Screenshot:
**Visual & Functional Requirements:**

1. **Add New Task Section:**
   - **Input Field:** Dark gray rectangular input with rounded corners
   - **Placeholder:** "Add a new task (e.g., 'setup call on 10/11 @Nick')" - shows parsing format
   - **Submit Button:** Small rounded button with white paper airplane icon

2. **Filter Section:**
   - **Label:** "Filter tasks:" with help icon (white question mark)
   - **Dropdown:** Dark gray rectangular dropdown with rounded corners
   - **Current Selection:** "All" selected (white text)
   - **Dropdown Indicator:** White downward chevron on right

3. **Overall Theme:**
   - Dark background with light text
   - Consistent small icons throughout
   - Clear visual hierarchy with different text sizes and colors
   - Card-like layout with clear separation

### SCREENSHOT DISCREPANCY IDENTIFIED:
**Issue:** Screenshot shows "Active Tasks (4)" header, but conversation requirement was to "remove stats for now"
**Resolution Needed:** Clarify whether to keep or remove the task count display

### UI Layout Requested:
**User explicitly specified order:**
1. Input box for tasks (first)
2. Filter dropdown (second)
3. List of tasks - **recently added first**
4. **Remove stats** (active, completed, overdue) "for now"

---

## PIPELINE SUMMARY - Requirements from Conversation

### Location:
**Between the Company Header and the tabs** (Overview / Team / Signals / Comments / Meetings / Tasks)

### Display Requirements:
**User provided specific format:**
```
🔹 Last Pipeline Summary (auto-generated)
- Last discussed: …
- Outcome: …
- Next step: …
```

### Collapsible:
- User requested it to be **collapsible**
- User later requested: **Always collapsed when opening the company details page**

### Initial Implementation:
- User asked to "use mock data for the pipeline summary initially to verify the UI"
- Then switch to real data

### Real Data Logic - 7-Day Window:
**User Story Provided:**
> "As a GP reviewing a deal in the pipeline, I want the Last Pipeline Summary section to show all completed tasks and their outcomes from the past 7 days"

**Acceptance Criteria from User Story:**

1. **7-day window logic:**
   - Select all tasks marked as `done == True`
   - Where `completed_at >= today - 7 days`
   - No manual meeting date input - refreshes daily

2. **Display format:**
   - **"Last discussed"**: List titles of all tasks completed in last 7 days (most recent first)
   - **"Outcome"**: List corresponding notes (results) of those tasks, in same order
   - **"Next step"**: Show next active (not done) task with nearest due date

3. **Empty state:**
   - If no tasks completed in last 7 days: "No completed tasks in the past week."
   - Still display "Next step" if active tasks exist

4. **Automatic update:**
   - Summary updates automatically on each app rerun
   - No manual refresh required
   - When new tasks completed, they appear immediately

5. **Formatting:**
   - Keep existing structure
   - **Do not add new sections or UI elements**
   - Only modify content logic

### Enhanced Summary Format:
**User later requested more informative summary with:**
```
🧾 Last Pipeline Summary (Oct 03 – Oct 10)
Updated today
✅ 3 completed ⚠️ 1 overdue 🗓️ 4 active
```

### Summary Period Display:
- User requested: **Show period instead of single date** (e.g., "Oct 3 - Oct 10")

### Auto-refresh Behavior:
- User confirmed: **"Auto-refresh on every page load"**
- Summary always shows latest data when page loads/reruns
- No manual refresh button needed

### Detailed UI Polish Requests:
**User provided "Final Polish Checklist" with specific styling:**

1. **Header line:**
   - Add subtle divider (`·`) between "Updated today" and counts
   - Lighten meta text color (`#8a8d92`, `font-size:13px`, `letter-spacing:.1px`)

2. **List indentation:**
   - CSS for `summary-card ul`: `margin-left:1.1rem`, `padding:0`
   - CSS for `summary-card li`: `margin:2px 0`, `line-height:1.45`

3. **Section labels:**
   - Small caps and slightly translucent
   - `font-size:12px`, `color:#9a9a9a`
   - `font-variant-caps:all-small-caps`, `letter-spacing:.4px`, `margin-bottom:2px`

4. **"Next step" styling:**
   - Keep arrow `→`
   - Use neutral gray for assignee
   - 4px spacing between line and pill
   - Pill styling: `background:#ffecec`, `color:#c65353`, `font-size:11px`, `padding:2px 6px`, `border-radius:8px`, `margin-left:6px`

5. **Bottom spacing:**
   - `padding-bottom:12px; margin-bottom:10px` to `.summary-card`

### Additional Fine-tuning:
1. Reduce vertical rhythm between meta line and "Last discussed" to 6px
2. Soften meta gray tone to `#7a7d81`
3. Improve bullet alignment to `margin-left: 1.4rem`
4. Emphasize "Next step" with 4px top margin, darker text (`#2f2f2f`), `font-weight: 500`
5. Make overdue pill softer: `background: #fff2f2; color: #b24747; border: 1px solid #ffdede; padding: 1px 6px;`

### Spacing Adjustments:
- User requested various spacing adjustments (16px → 8px → 4px → 0px)
- User identified "big space" due to styling boxes (section labels) margins

### Final Notion-like Design:
**User requested (as "VP of UI/UX in Notion"):**
- Move summary stats to right-aligned secondary column
- Reduce header padding for compactness
- Make "Last Pipeline Summary" slightly bolder, date range lighter gray
- Reduce divider line opacity to 50%
- Decrease vertical spacing between section titles and lists
- Change section headers to small-caps gray (`#7a7d81`)
- Turn "Overdue" tag into inline rounded pill
- Reduce bullet indentation (~10px)
- Add hover background on header row (light gray tint)
- Round bottom corners of expander body

### Meta Information Refinements:
- Font size of header date range and status: ~13px
- Use lighter gray `#9b9b9b`
- Add 4-6px vertical padding above/below header row
- Align "Updated today…" text to right edge of expander header
- Make bullet separators (•) consistent
- Add 5-10px spacing between section groups
- Lighten section headings color slightly (`#8c9a9e`)
- Reduce bottom padding inside expander
- Optional faint hover state on header background

### UI Element Fixes:
- User reported: "styling code was visible in the expander label"
- User reported: "bolding was not working"
- User requested: **Remove word "Last" from "Last Pipeline Summary"** → becomes "Pipeline Summary"
- User requested: Move "Updated today" inside content area (not in title)
- User requested: Make "Last updated: Today" more readable (increased to 12px)
- User confirmed: **Keep expander collapsed by default**
- User requested: **Ensure "Overdue" chip appears only for overdue tasks**
- User reported: "Overdue" chip location incorrect (on new line) - requested fix

### Pipeline Summary - Requirements from Screenshot:
**Visual & Functional Requirements:**

1. **Pipeline Summary Header:**
   - **Title:** "Pipeline Summary (Oct 03 - Oct 10)"
     - "Pipeline Summary" text slightly bolder
     - Date range "(Oct 03 - Oct 10)" in lighter gray (~13px font size)
   - **Stats Line (Right-aligned):** "✅ 3 completed · ⚠️ 1 overdue · 🗓️ 4 active"
     - Each stat with emoji icon (green checkmark, yellow warning, calendar)
     - Subtle divider (`·`) between stats
     - Lighter gray text color (~13px font size)
   - **"Last updated" line:** "Last updated: Today"
     - Positioned below header, left-aligned
     - Readable gray tone, 12px font size
   - **Collapsible:** st.expander with dropdown arrow
   - **Default State:** Collapsed by default
   - **Header Padding:** 4-6px vertical padding above/below

2. **Pipeline Summary Content (within expander):**
   - **Section Labels:** "LAST DISCUSSED", "OUTCOME", "NEXT STEP"
     - Small-caps, translucent gray (`#7a7d81`)
     - 12px font size, letter-spacing: .4px
     - Reduced margins to minimize vertical space
   - **Content Lists:**
     - **LAST DISCUSSED:** Bullet points, reduced indentation (~1.4rem)
     - **OUTCOME:** Bullet points, matching order with LAST DISCUSSED
     - **NEXT STEP:** 
       - Starts with arrow (→)
       - Darker text (`#2f2f2f`), font-weight: 500
       - **"Overdue" Pill:** Inline rounded pill with soft styling:
         - `background: #fff2f2; color: #b24747; border: 1px solid #ffdede; padding: 1px 6px; border-radius: 8px; margin-left: 6px; font-size: 11px;`
         - Only appears for actually overdue tasks
   - **Dividers:** Thin horizontal lines between sections (50% opacity)
   - **Spacing:** 5-10px between section groups, reduced bottom padding
   - **Bottom Corners:** Slightly rounded expander body

3. **Functional Requirements:**
   - **Dynamic Content:** All content generated from real task data
   - **7-Day Window:** Completed tasks from last 7 days
   - **Auto-refresh:** Updates on every page load/rerun
   - **Empty State:** "No completed tasks in the past week" when applicable
   - **Overdue Logic:** Pill only for overdue tasks, inline positioning

---

## CRITICAL ISSUES IDENTIFIED

### From User's Final Statement:
**User said:** "no they don't you fully screwed task, review history of this conversation like busines anlaysi and buil AC for Summary and For Task tab"

This indicates:
1. The implementation doesn't match what was discussed in conversation
2. Need to focus on ACTUAL conversation requirements, not just code found in git history
3. Tasks and Summary both need proper implementation per conversation specs

---

## KEY DIFFERENCES FROM CODE I FOUND:

### What Code Had vs What User Requested:

**Tasks Tab:**
- Code: Used `task.title` field
- **Conversation:** User wanted **inline parsing** of task text for @mentions and dates
- Code: Had separate form fields for title, assignee, due date
- **Conversation:** User wanted **Comments-style input** - type everything in one box and parse it
- Code: Had emoji indicators for due dates
- **Conversation:** User explicitly requested **colored text, NOT emojis**
- Code: Showed stats (Active/Completed/Total)
- **Conversation:** User said **"remove stats for now"**

**Pipeline Summary:**
- Code: Had hardcoded HTML mock data
- **Conversation:** User wanted real data from tasks with 7-day window logic
- Code: Complex HTML structure
- **Conversation:** User wanted simple bullet lists with specific Notion-like styling

---

## DEFINITION OF DONE

### Tasks Tab:
✅ Single input box (like Comments)
✅ Parse @mentions for assignee
✅ Parse MM/DD for due date
✅ Colored text for due dates (Red/Green/Brown/Purple)
✅ Filter dropdown (All/Active/Completed/Overdue/Mine)
✅ "Mine" filter shows only tasks assigned to me
✅ Inline editing for task text, date, assignee
✅ Add notes in edit mode
✅ Prompt for "Outcome" when completing
✅ Recently added tasks first
⚠️ **DISCREPANCY:** Stats display - screenshot shows "Active Tasks (4)" but conversation said "remove stats for now"

### Task Completion Modal:
✅ "Complete Task: [Title]" header
✅ Large notes textarea (optional)
✅ "Outcome / Decision (optional)" field with placeholder examples
✅ Red "Complete Task" button with green checkmark icon
✅ Dark gray "Cancel" button with red X icon
✅ Dark theme styling

### Task Edit Form:
✅ "Edit Task" header
✅ Task text field with help icon
✅ Assignee field with help icon
✅ Due date field with help icon (YYYY/MM/DD format)
✅ Notes section with sub-label and placeholder
✅ Red "Save" button with floppy disk icon
✅ Dark gray "Cancel" button with red X icon
✅ Dark gray "Delete" button with trash can icon

### Completed Tasks Display:
✅ "Completed Tasks (X)" expandable header with green checkmark icon
✅ Individual task cards with white title text
✅ Green outcome boxes with "✅ Outcome: [Description]" format
✅ Metadata line: "Due: [Date] • [Assignee] • Created by [Creator] on [Date]"
✅ Red text for overdue due dates
✅ Yellow pencil edit button (✏️)
✅ Curved arrow revert button (↩️)
✅ "Created X days ago" footer

### Active Tasks Display:
✅ "Active Tasks (X)" header with clipboard icon
✅ Bold white task titles
✅ Color-coded due dates (Red/Green/Brown/Purple)
✅ Assignee names with person icons
✅ "Created by [Name] on [Date]" with person icons
✅ Bullet separators (•) in metadata
✅ Yellow pencil edit button (✏️)
✅ Checkmark complete button
✅ Recently added first ordering

### Main Interface:
✅ Dark gray input with placeholder showing parsing format
✅ Paper airplane submit button
✅ "Filter tasks:" label with help icon
✅ Dark gray dropdown with "All" selected
✅ White downward chevron indicator
✅ Dark theme throughout
✅ Consistent iconography
✅ Card-like layout with clear separation

### Pipeline Summary:
✅ Between header and tabs
✅ Collapsible, collapsed by default
✅ 7-day window for completed tasks
✅ "Last discussed" - completed task titles
✅ "Outcome" - corresponding notes
✅ "Next step" - next active task
✅ Auto-refreshes on page load
✅ Stats in header (completed/overdue/active)
✅ Notion-like clean design
✅ Proper spacing and typography
✅ Overdue pill only when applicable

### Pipeline Summary Visual:
✅ "Pipeline Summary (Oct 03 - Oct 10)" title with date range
✅ Right-aligned stats: "✅ 3 completed · ⚠️ 1 overdue · 🗓️ 4 active"
✅ "Last updated: Today" line below header
✅ Small-caps section labels ("LAST DISCUSSED", "OUTCOME", "NEXT STEP")
✅ Bullet points with reduced indentation (~1.4rem)
✅ "NEXT STEP" with arrow (→) and darker text
✅ Soft overdue pill styling (inline positioning)
✅ Thin dividers between sections (50% opacity)
✅ Proper spacing and rounded bottom corners

