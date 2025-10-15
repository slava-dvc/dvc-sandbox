# Streamlit Cloud Deployment Smoke Tests

This document provides step-by-step smoke tests to verify the DVC Portfolio Dashboard is working correctly on Streamlit Cloud.

## Pre-deployment Checklist

Before deploying, ensure:
- [ ] Code changes are committed and pushed to GitHub
- [ ] `LOCAL_DEV=True` is set in `streamlit_app.py`
- [ ] `.streamlit/config.toml` is committed
- [ ] No secrets or environment variables are required

## Deployment Smoke Tests

### Test 1: App Loads Successfully

**Steps:**
1. Navigate to your Streamlit Cloud app URL
2. Wait for the app to load

**Expected Result:**
- App loads without errors
- No red error messages
- Navigation sidebar is visible on the left
- Main content area shows the "Funds" page by default

---

### Test 2: Navigation Between Pages

**Steps:**
1. Click on "Funds" in the sidebar
2. Click on "Companies" in the sidebar
3. Click on "Pipeline" in the sidebar
4. Click on "Tasks (N)" in the sidebar (where N is a number)
5. Click on "Jobs" in the sidebar

**Expected Result:**
- Each page loads successfully
- No errors are displayed
- Page content changes appropriately

---

### Test 3: Testing User Selector (Mock Mode Only)

**Steps:**
1. Look for "Testing:" section in the sidebar
2. Verify the user selector dropdown is present
3. Select different users from the dropdown (e.g., "Marina", "Nick", "Mel")

**Expected Result:**
- User selector dropdown is visible
- Default user is "Nick"
- Can switch between different team members
- Tasks count in navigation updates when user changes

---

### Test 4: View Companies

**Steps:**
1. Navigate to "Companies" page
2. Verify mock companies are displayed

**Expected Result:**
- 4 mock companies are visible:
  - Generous
  - TechFlow
  - HealthSync
  - CloudScale AI
- Each company shows basic information (name, status, industry, etc.)
- No errors loading company data

---

### Test 5: Company Details Page

**Steps:**
1. Navigate to "Companies" page
2. Click on "Generous" company
3. Scroll through the company details
4. Try clicking other companies

**Expected Result:**
- Company detail page loads successfully
- Shows company summary, problem, solution, metrics
- Can navigate back to company list
- Tasks section is visible (if tasks exist)

---

### Test 6: Pipeline View

**Steps:**
1. Navigate to "Pipeline" page
2. Verify companies are organized by status columns

**Expected Result:**
- Pipeline view shows columns for different company statuses
- Companies are distributed across columns based on status
- Can see company cards in each column

---

### Test 7: All Tasks View

**Steps:**
1. Select "Nick" from the Testing user selector
2. Navigate to "Tasks (N)" page
3. Verify tasks are displayed
4. Try toggling between "My tasks" and "All tasks" views

**Expected Result:**
- Task list loads successfully
- Can see tasks with assignees, due dates, and status
- Filter controls work properly
- Can switch between different views

---

### Test 8: Create New Task

**Steps:**
1. Navigate to a company detail page
2. Scroll to the "Tasks" section
3. Click "Add Task" button
4. Fill in task details:
   - Title: "Test task from Streamlit Cloud"
   - Due date: Select tomorrow's date
   - Assignee: Select "Nick"
   - Notes: "Testing task creation"
5. Click "Create Task"

**Expected Result:**
- Task form appears as a dialog
- All fields can be filled
- Task is created successfully
- New task appears in the task list
- Success message is displayed

---

### Test 9: Edit Task

**Steps:**
1. Find an existing task
2. Click the edit/pencil icon on the task
3. Modify the task title or notes
4. Save the changes

**Expected Result:**
- Edit dialog appears
- Can modify task fields
- Changes are saved
- Updated task reflects changes

---

### Test 10: Complete/Mark Task Status

**Steps:**
1. Find an active task
2. Change the status from "active" to "completed"
3. Add an outcome note
4. Save

**Expected Result:**
- Task status changes successfully
- Task count in navigation updates
- Task appears in completed tasks list

---

### Test 11: Jobs Board

**Steps:**
1. Navigate to "Jobs" page
2. Verify mock jobs are displayed

**Expected Result:**
- Mock jobs are visible
- Each job shows title, company, location, type
- No errors loading jobs data

---

### Test 12: Session Persistence

**Steps:**
1. Create a new task on any company
2. Change user selection to "Marina"
3. Navigate to different pages
4. Come back to the company page with the task

**Expected Result:**
- Newly created task persists across page navigation
- User selection persists
- Data remains consistent throughout the session

---

### Test 13: No Add Company Button (Mock Mode)

**Steps:**
1. Look in the sidebar for "Actions:" section
2. Verify no "Add Company" button is present

**Expected Result:**
- "Add Company" button is NOT visible (requires Google Cloud services)
- No error messages related to missing cloud services
- This confirms app is correctly running in mock/LOCAL_DEV mode

---

### Test 14: Responsive Layout

**Steps:**
1. Resize browser window to different widths
2. Try on mobile device if available
3. Check that content adjusts appropriately

**Expected Result:**
- Layout adjusts to different screen sizes
- No horizontal scrolling (except for wide tables)
- Sidebar can be collapsed/expanded
- Content remains readable

---

## Post-Deployment Notes

### What Should Work:
- ✅ All navigation between pages
- ✅ Viewing mock companies, tasks, jobs, pipeline
- ✅ Creating, editing, and deleting tasks
- ✅ User selector for testing task assignments
- ✅ All interactive features using session state
- ✅ Mock data persistence during session

### What Won't Work (Expected Limitations):
- ❌ Add Company button (hidden - requires Google Cloud)
- ❌ Real data from MongoDB/Airtable
- ❌ Google OAuth authentication (bypassed for testing)
- ❌ Data persistence across sessions (mock data resets)

### Performance Expectations:
- Initial load: 5-10 seconds
- Page navigation: < 1 second
- Task operations: < 1 second

### Common Issues:

**Issue: App shows "ModuleNotFoundError"**
- Ensure all dependencies in `requirements.txt` are correct
- Check that the main file path is `synapse/streamlit_app.py`

**Issue: "LOCAL_DEV not working"**
- Verify `streamlit_app.py` sets `os.environ['LOCAL_DEV'] = 'True'`
- Check that `data.py` also has `LOCAL_DEV` check

**Issue: App loads but no data appears**
- This is expected if mock data isn't loading
- Check browser console for JavaScript errors
- Verify `data_mock.py` is present and has mock data

## Sharing the App

Once all tests pass, you can share the Streamlit Cloud URL with external users:

1. Get your app URL from Streamlit Cloud (format: `https://[app-name].streamlit.app`)
2. Share the URL with testers
3. Note that anyone with the link can access (no authentication)
4. Each user will have their own session with mock data

## Contact & Support

If you encounter issues not covered in this guide:
1. Check Streamlit Cloud logs in the app settings
2. Review the GitHub repository for recent changes
3. Check Streamlit Community forum for similar issues

