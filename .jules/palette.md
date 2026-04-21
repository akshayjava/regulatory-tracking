## 2024-04-21 - [Focus States with Inline Styles]
**Learning:** This app heavily uses inline styles (`style={{...}}`) for components. Native CSS pseudo-classes like `:focus` or `:focus-visible` cannot be applied directly via inline styles.
**Action:** When adding keyboard navigation and focus states to custom interactive elements (like turning a `div` into a `<button>`), use React state (e.g. `const [isFocused, setIsFocused] = useState(false)`) toggled via `onFocus` and `onBlur` to dynamically apply `outline` styles.
