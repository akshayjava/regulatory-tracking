## 2024-05-18 - Missing ARIA Labels in Unlabeled Form Inputs and Improved Empty States
**Learning:** This app uses inline styles heavily and inputs like Search and Status filters did not have associated `<label>` tags. This caused accessibility issues for screen readers. Additionally, replacing generic "No results found" messages with a clear recovery path (e.g., a CTA to clear filters) significantly improves the user experience.
**Action:** Next time working on custom styled inputs, ensure ARIA attributes are added if standard label tags aren't present. Also, look out for empty states that leave the user stranded, and try to add actionable buttons to help them recover.

## 2025-02-12 - Adding ARIA Labels to Standalone Textareas
**Learning:** When textareas or input elements are visually self-explanatory in context but lack a visible `<label>` (often to save space or achieve a specific design), screen readers cannot determine their purpose. Relying purely on placeholder text is insufficient as it often disappears when users start typing.
**Action:** Always provide an explicitly descriptive `aria-label` to these interactive elements (e.g., `aria-label="Ask a question about regulations"`) to ensure the intent is accessible to assistive technologies without altering the visual design.
