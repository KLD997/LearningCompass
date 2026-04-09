# UI Design System & Component Inventory

## Design Goals
- Child-friendly clarity with minimal clutter.
- Parent efficiency for planning and reporting.
- Consistent, low-friction lesson navigation.

## Visual Tokens

### Color roles
- Primary: action buttons and highlights
- Secondary: navigation accents
- Success: completion states
- Warning: missing/overdue assignments
- Neutral: surfaces and text hierarchy

### Typography
- Heading: clear rounded sans-serif
- Body: readable sans-serif
- Minimum body size: 16px for child screens

### Spacing and layout
- 8px spacing scale
- Large touch targets (44px min)
- Fixed top nav + responsive card grid

## Core Components

### Shared
- App shell (top nav + side nav)
- Card
- Badge
- Progress ring/bar
- Pill tag (subject, level, rights flag)
- Modal/dialog
- Toast notification

### Parent Components
- Student summary card
- Assignment calendar grid
- Lesson library table with filters
- Source rights status indicator
- Report chart cards

### Student Components
- Today lesson queue card
- Continue lesson hero button
- Mascot message panel (optional by age)
- Achievement strip
- Help/request-parent button

### Lesson/Assessment Components
- Lesson renderer wrapper (hosted/link/embed/offline)
- Rich text content block
- Video player frame
- Quiz question block
- Rubric scoring panel
- Parent observational checklist

## Accessibility & UX Rules
- Keyboard navigable parent screens.
- Child screens limit choices per view.
- Clear state labels: assigned, in progress, complete, skipped.
- Do not hide critical actions behind hover-only controls.
