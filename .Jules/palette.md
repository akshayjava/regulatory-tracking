## 2024-05-18 - Missing ARIA Labels in Unlabeled Form Inputs and Improved Empty States
**Learning:** This app uses inline styles heavily and inputs like Search and Status filters did not have associated `<label>` tags. This caused accessibility issues for screen readers. Additionally, replacing generic "No results found" messages with a clear recovery path (e.g., a CTA to clear filters) significantly improves the user experience.
**Action:** Next time working on custom styled inputs, ensure ARIA attributes are added if standard label tags aren't present. Also, look out for empty states that leave the user stranded, and try to add actionable buttons to help them recover.

## 2024-05-12 - Adding focus states to inline-styled React components
**Learning:** Because CSS pseudo-classes like `:focus-visible` cannot be natively applied via React inline styles (`style={{...}}`), inputs that use inline styles and `outline: 'none'` become completely invisible to keyboard navigators.
**Action:** When working with inline-styled components, handle accessibility focus states by attaching `onFocus` and `onBlur` handlers to the semantic element to manage an `isFocused` state. Then, conditionally apply custom focus rings (e.g., via `boxShadow` and `borderColor`) based on that state.
