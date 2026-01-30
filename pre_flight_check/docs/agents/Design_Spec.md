# Design_Spec.md

---

## To-Do App - Design Specification Document

### Overview

This document details the page structure, UI components, and interaction patterns for the To-Do App as outlined in the Product Requirements Document (PRD). It aims to facilitate front-end and UI developers in building a polished, accessible, responsive, and user-friendly interface that meets all functionalities including authentication, task management, and drag-and-drop interactions.

---

## 1. Page Structure

### 1.1 Authentication

- **Registration Page**
  - URL/Route: `/register`
  - Purpose: Allow new users to create an account.
  - Key Components:
    - Form inputs: Full Name, Email, Password, Confirm Password.
    - Action Buttons: Register, Link to Login page.
    - Error Message Areas: For validation errors (e.g., invalid email, weak password, password mismatch).
    - Success Feedback: On successful registration, redirect to Login or auto-login.

- **Login Page**
  - URL/Route: `/login`
  - Purpose: Allow existing users to authenticate.
  - Key Components:
    - Form inputs: Email, Password.
    - Action Buttons: Log In, Link to Register page, Forgot Password (optional).
    - Error Message Areas: For invalid credentials.
    - Loading state indication during submission.

---

### 1.2 Main Task Management Page

- **URL/Route:** `/tasks`
- **Purpose:** Core dashboard for task creation, editing, status updates, and drag-drop management.

#### Layout & Structure:

- Responsive layout with three main columns representing task statuses:
  1. **To Do**
  2. **In Progress**
  3. **Done**

- Columns arranged horizontally on desktop, stacked vertically on mobile.
- Header includes app branding, user profile access/logout button, and new task creation button.

---

## 2. UI Components and Detailed Descriptions

### 2.1 Authentication Components

| Component            | Description                                                                                               | States                                   | Error Handling                                                                                      | Accessibility                                         |
|----------------------|-----------------------------------------------------------------------------------------------------------|------------------------------------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| Input Fields         | Text inputs for email, password, name.                                                                   | Default, Focused, Filled, Disabled       | Inline validation error messages below inputs. Color and icon cues for invalid input.              | Use `<label>` tags, ARIA-required, aria-invalid        |
| Buttons              | Primary call to action buttons (Register, Login)                                                         | Default, Hover, Focused, Disabled        | Disabled state when form invalid or submitting.                                                    | Keyboard accessible, visible focus indicator            |
| Error Messages      | Inline text messages for incorrect inputs or server responses                                             | Visible or Hidden                        | Clear red coloring, icon (exclamation). Persist until user corrects input.                         | Announced by screen readers using `aria-live="assertive"` |
| Success Notification | Confirmation message after successful registration, optionally as a toast                                 | Visible momentarily then disappears      | N/A                                                                                                | Use ARIA role="alert" or polite for screen readers      |

---

### 2.2 Task Management Components

| Component                    | Description                                                                                              | States                                             | Error Handling and Visual Feedback                                                            | Accessibility                                           |
|------------------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------|------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| Header                       | Contains App logo/title, user profile icon with dropdown, logout button, and "New Task" button.          | Default, Hover on buttons/menu items                | Button loading spinner on logout or new task actions                                            | Keyboard accessible, ARIA roles for menu and buttons    |
| Task Column                  | Three vertical lists labeled: To Do, In Progress, Done                                                   | Default, Empty state, Dragging over                 | Empty message if no tasks, visual highlight on drag-over                                      | Columns labeled with `aria-label` and role="list"       |
| Task Card                    | Displays task title, optional description preview, due date, and priority label. Click to edit.          | Default, Hover, Dragging, Focused, Disabled         | Shadow or elevation increase on hover/dragging, subtle opacity change when disabled             | Each task is a button or link with ARIA `draggable="true"` |
| New/Edit Task Modal          | Modal window for creating or editing a task, includes inputs for title (required), description, priority, due date, status | Default, Validation error, Loading submission        | Inline validation errors with messages below inputs, form disabled while saving                 | Modal has ARIA modal role; focus trapped; labelled by heading |
| Drag and Drop Interaction    | Enables moving task cards between columns by drag and drop. Includes keyboard support                     | Drag start, Dragging over target, Drop success/failure | Visual cues: shadow, color change on drag source, highlight drop target column, error on invalid drop | Keyboard accessible: draggable via SPACE/ENTER and arrow keys; ARIA live notifications on drop |

---

## 3. Component States

| Component            | State                                  | Description / Behavior                                                  | Visual Style                                                   |
|----------------------|--------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------|
| Button               | Default                              | Normal clickable state                                                | Primary color background, white text                           |
| Button               | Hover                               | Mouse over interaction                                               | Slightly darker background shade, pointer cursor              |
| Button               | Focused                             | Keyboard navigation on button                                        | Visible outline/focus ring                                     |
| Button               | Disabled                           | Non-interactive                                                      | Greyed out, no pointer cursor                                  |
| Input Field          | Default                              | Ready for input                                                      | Border grey, white background                                  |
| Input Field          | Focused                             | Active/focused by user                                               | Highlighted border (primary color), subtle shadow             |
| Input Field          | Error                               | Validation failed                                                   | Red border, error icon and message below input                 |
| Task Card            | Default                              | Static display                                                     | White background, subtle shadow, border-radius                |
| Task Card            | Hover                               | Mouse pointer over task                                            | Slight elevation shadow, cursor pointer                        |
| Task Card            | Dragging                            | Task user is dragging                                            | Opacity 0.7, slight scale increase, cursor grabbing           |
| Task Card            | Disabled/Completed                  | Completed task or disabled                                         | Grayscale or muted color, strikethrough (task title optional) |
| Modal                | Open                                | Active modal window                                                 | Overlay dimming behind modal, modal centered                   |
| Modal                | Validation Error                    | Failed field validation                                             | Inline red message, red border on invalid fields               |
| Drag-and-Drop Target | Dragging over                       | Column where task can be dropped                                  | Highlighted background or border glow                          |

---

## 4. Responsive Design Considerations

| Viewport           | Layout Adjustments                                                                            | Specific Notes                                                               |
|--------------------|-----------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| Desktop (≥1024px)  | Three columns side-by-side horizontally, main layout with header on top.                      | Task columns visually distinct with vertical scroll if overflow occurs.     |
| Tablet (≥768px <1024px) | Columns remain horizontal but narrow, font sizes slightly reduced, modal width adjusted.       | Touch targets remain minimum 44px, vertical scrolling on columns enabled.    |
| Mobile (<768px)    | Columns stacked vertically; user can swipe vertically to view each status column.             | Simplified navigation with collapsible header, hamburger menu if needed.     |
| Modal Windows      | Modal width adapts: max 90% viewport width on mobile, centered pop-up on desktop/tablet.       | Full height scrolling inside modal if large form content.                    |

---

## 5. Error Handling UI and Feedback

- **Form Submission Errors:** Inline error messages appear below the relevant input fields when validation fails. Errors use red text color (#D32F2F) and an icon (exclamation circle).
- **Authentication Errors:** Display a prominent alert box above the form with error message (e.g. "Incorrect password") using ARIA alert role.
- **Network/Server Errors:** Generic toast notification at top-right corner for issues such as connection failure or server errors with clear retry instructions.
- **Drag and Drop Errors:** If user attempts to drop a task outside valid columns, a shaking animation or red highlight animates briefly on invalid drop target.
- **Loading States:** Buttons and forms have loading spinner overlays (small spinner in button or overlay on modal) indicating pending states to prevent multiple submissions.

---

## 6. Visual Feedback & Accessibility Features

- All interactive elements have visible focus styles to support keyboard navigation.
- Drag-and-drop has keyboard interaction support:
  - Use SPACE/ENTER to pick up or drop a task.
  - Use arrow keys to navigate between tasks and columns.
  - Screen reader announcements for drag start, drag over, drop success or failure using `aria-live`.
- Color contrast ratios meet WCAG AA standards to ensure readability.
- Task status columns have clear color differentiation:
  - To Do: #2196F3 (blue)
  - In Progress: #FFC107 (amber)
  - Done: #4CAF50 (green)
- Task priority labels use additional iconography and tooltips for clarity.
- Modal dialogs trap keyboard focus until closed, with `aria-modal="true"` and descriptive labels.
- Form inputs use semantic HTML elements (`<label>`, `<input>`) with associated `for` attributes.

---

## 7. Summary of Key UI Components

| Component                 | Included UI Elements                                           | Interaction Notes                                |
|---------------------------|---------------------------------------------------------------|-------------------------------------------------|
| Authentication Forms      | Labels, inputs, buttons, error messages                       | Keyboard & screen reader accessible, validation |
| Task Columns              | Title header, empty state message, task card list             | Scrollable, drag and drop target                  |
| Task Cards                | Title, due date, priority, description summary, drag handlers | Click to open edit modal, focusable               |
| New/Edit Task Modal       | Form inputs, validation, submit/cancel buttons, loading state | Accessible modal, focus trap, error feedback     |
| Header                   | Branding, profile menu, logout, new task button                | Responsive, accessible menu navigation            |
| Drag and Drop             | Visual drag feedback, keyboard support, color highlights      | Announced by screen readers, smooth visual cues  |

---

# End of Design_Spec.md