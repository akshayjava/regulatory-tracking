## 2025-04-25 - [Inline Focus States]
**Learning:** In React applications using strictly inline styles, standard `:focus-visible` pseudoclasses are unavailable. This impacts accessibility by making focus rings difficult to style directly via properties.
**Action:** Implemented custom state handlers (`onFocus`, `onBlur`) to track active focus and manually apply custom `boxShadow` styling to interactive elements like buttons.

## 2025-04-25 - [Div as Buttons]
**Learning:** Found interactive checklist elements structured as `div` components using `onClick`. These do not naturally receive focus via tab key interaction or keyboard 'Space' and 'Enter' actions.
**Action:** Changed to semantic `button` elements, combined with ARIA properties (`aria-pressed`) to improve screen reader feedback and fully restore standard keyboard usability.
