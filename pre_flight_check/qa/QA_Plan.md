# QA Test Plan - Pre-flight Check Tool

## 1. Functional Testing
### Backend API (/api/analyze)
- [ ] **TC-001**: Verify successful analysis with valid input (Video + All fields).
- [ ] **TC-002**: Verify handling of missing file.
- [ ] **TC-003**: Verify calculation of Benchmark Score (Target CPA vs Industry).
- [ ] **TC-004**: Verify n8n integration fallback (Mock mode if no URL).

### Frontend UI
- [ ] **TC-005**: Verify Drag & Drop file upload works.
- [ ] **TC-006**: Verify Form Validation (Required fields).
- [ ] **TC-007**: Verify Dashboard updates correctly after API response.
- [ ] **TC-008**: Verify "Traffic Light" logic (Red/Yellow/Green).

## 2. Integration Testing
- [ ] **TC-009**: Test with real n8n Webhook (Set N8N_WEBHOOK_URL).
- [ ] **TC-010**: Verify big file upload limits (>50MB).

## 3. UI/UX Testing
- [ ] **TC-011**: Check Responsive Design on Mobile/Tablet.
- [ ] **TC-012**: Verify Glassmorphism effects are visible.
