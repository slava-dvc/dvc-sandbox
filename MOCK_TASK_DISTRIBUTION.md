# Mock Task Distribution for All Tasks View Testing

## Overview
Created realistic mock tasks assigned to actual team members across 6 companies to enable comprehensive testing of the All Tasks view with "My tasks" filter.

## Team Member Task Assignments

### Marina (Managing Partner, Founder)
- **Generous**: Draft IC memo, Review pitch deck and financials
- **HealthSync**: Due diligence on HIPAA compliance  
- **SaaS**: Customer success metrics analysis
- **Total**: 4 active tasks

### Nick (Managing Partner, Founder)  
- **Generous**: Schedule follow-up call with founders, Check references from previous investors (completed)
- **TechFlow**: Analyze competitive landscape
- **FinTech**: Due diligence call with founders (completed)
- **Total**: 3 active tasks, 2 completed

### Mel (GP)
- **TechFlow**: Validate MRR growth metrics
- **HealthSync**: Verify health system partnerships
- **FinTech**: Regulatory compliance review
- **Total**: 3 active tasks

### Charles (GP)
- **TechFlow**: Schedule demo with founders (completed)
- **HealthSync**: Review FDA fast-track designation
- **FinTech**: Enterprise sales strategy review
- **Total**: 2 active tasks, 1 completed

### Alexey (Venture Partner)
- **TechFlow**: Review technical architecture
- **AI Startup**: Review AI model performance metrics
- **FinTech**: Technical security audit
- **Total**: 3 active tasks

### Tony (Head of Product)
- **AI Startup**: Platform automation improvements
- **FinTech**: Product roadmap review
- **SaaS**: Product analytics dashboard
- **Total**: 3 active tasks

### Elena (Head of IR & Community)
- **AI Startup**: Investor relations update
- **FinTech**: Community event planning
- **SaaS**: LP quarterly report (completed)
- **Total**: 2 active tasks, 1 completed

### Vlad (Head of Engineering)
- **Generous**: Get technical architecture documentation
- **HealthSync**: Technical assessment of data sync platform
- **AI Startup**: Build AI agent for deal sourcing
- **SaaS**: Platform scalability assessment
- **Total**: 4 active tasks

### Slava (User)
- **AI Startup**: Board meeting preparation (completed)
- **Total**: 1 completed task

## Company Distribution

### Generous (68e69a2dc32b590896149739)
- 5 tasks total (4 active, 1 completed)
- Marina: 2 tasks, Nick: 2 tasks, Vlad: 1 task

### TechFlow (68e69a2dc32b590896149740)  
- 4 tasks total (3 active, 1 completed)
- Nick: 1 task, Alexey: 1 task, Mel: 1 task, Charles: 1 task

### HealthSync (68e69a2dc32b590896149741)
- 4 tasks total (all active)
- Marina: 1 task, Mel: 1 task, Charles: 1 task, Vlad: 1 task

### AI Startup (68e69a2dc32b590896149742)
- 5 tasks total (4 active, 1 completed)
- Alexey: 1 task, Tony: 1 task, Elena: 1 task, Vlad: 1 task, Slava: 1 task

### FinTech (68e69a2dc32b590896149743)
- 5 tasks total (4 active, 1 completed)
- Mel: 1 task, Alexey: 1 task, Elena: 1 task, Tony: 1 task, Nick: 1 task

### SaaS (68e69a2dc32b590896149744)
- 5 tasks total (4 active, 1 completed)
- Marina: 1 task, Vlad: 1 task, Charles: 1 task, Tony: 1 task, Elena: 1 task

## Task Status Distribution
- **Active Tasks**: 22 total
- **Completed Tasks**: 6 total
- **Overdue Tasks**: 4 active tasks
- **Due Today**: 2 active tasks
- **Due Tomorrow**: 3 active tasks
- **Future Tasks**: 13 active tasks

## Testing Scenarios

### "My Tasks" Filter Testing
Each team member can test the "My tasks" filter and should see:
- **Marina**: 4 active tasks
- **Nick**: 3 active tasks  
- **Mel**: 3 active tasks
- **Charles**: 2 active tasks
- **Alexey**: 3 active tasks
- **Tony**: 3 active tasks
- **Elena**: 2 active tasks
- **Vlad**: 4 active tasks
- **Slava**: 0 active tasks (1 completed)

### Company Column Testing
All tasks should display the correct company name in the Company column, showing tasks from 6 different companies.

### Task Editing Testing
All tasks can be edited inline with the same functionality as company-specific Tasks tabs, including:
- Marking tasks as complete with results dialog
- Editing task text, assignee, due date, and notes
- Real-time synchronization between All Tasks and company Tasks tabs
