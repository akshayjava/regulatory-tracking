## 2024-05-18 - Missing ARIA Labels in Unlabeled Form Inputs and Improved Empty States
**Learning:** This app uses inline styles heavily and inputs like Search and Status filters did not have associated `<label>` tags. This caused accessibility issues for screen readers. Additionally, replacing generic "No results found" messages with a clear recovery path (e.g., a CTA to clear filters) significantly improves the user experience.
**Action:** Next time working on custom styled inputs, ensure ARIA attributes are added if standard label tags aren't present. Also, look out for empty states that leave the user stranded, and try to add actionable buttons to help them recover.

## 2024-05-15 - Inline Styles and Focus States
**Learning:** Because React inline styles do not support pseudo-classes like `:focus-visible`, interactive elements (like custom checklist buttons) that rely on inline styles will lack critical keyboard focus indicators by default.
**Action:** When refactoring clickable `<div>`s to semantic `<button>` elements with inline styling, always attach `onFocus` and `onBlur` event handlers to manage a local state (e.g., `focusedId`), and use that state to conditionally render custom focus rings (e.g., via `boxShadow`) to ensure keyboard accessibility.
