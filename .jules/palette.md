## 2024-05-01 - Focus States with Inline Styles
**Learning:** Because this React app heavily uses inline `style={{...}}` rather than CSS utility classes, native CSS pseudo-classes like `:focus-visible` cannot be applied directly to elements.
**Action:** When adding semantic interactive elements (like replacing a `<div>` with a `<button>`), manually implement focus tracking by using `onFocus` and `onBlur` to manage a state variable (e.g., `focusedId`), and use that state to conditionally render a focus ring (e.g., via `boxShadow`).
