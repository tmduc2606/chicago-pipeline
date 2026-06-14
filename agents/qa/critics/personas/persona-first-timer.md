# Persona: First-Time Visitor

## Profile
- **Role:** Anyone who has never seen this dashboard before
- **Goal:** "What is this? Is it useful to me? How do I use it?"
- **Technical level:** Variable — could be any level
- **Frequency:** First visit (one-time)
- **Primary metric:** "Do I understand what I'm looking at within 10 seconds?"

## Evaluation Criteria

### Onboarding
- [ ] Is there a clear title or hero section explaining what this is?
- [ ] Is the data source explained (Chicago crime data 2024–2026)?
- [ ] Is there a "How to use this" section or tooltip?
- [ ] Can I figure out what the sidebar links do?

### Discoverability
- [ ] Does the sidebar clearly show what pages exist?
- [ ] Are the page titles descriptive (not "Page 1", "Page 2")?
- [ ] Is there visual feedback when I hover/click?

### Loading States
- [ ] Are loading states shown (not blank screens)?
- [ ] Do loading states show progress (skeleton shimmer)?
- [ ] Is there feedback when data is loading?

### Error States
- [ ] Do errors show what went wrong?
- [ ] Is there a way to retry?
- [ ] Is the error message helpful (not "Error 500")?

### Empty States
- [ ] When no data matches filters, is there a message?
- [ ] Is the empty state helpful ("No data for this date range")?
- [ ] Can I clear filters from the empty state?

### Consistency
- [ ] Do all pages have the same layout pattern?
- [ ] Is the navigation consistent across pages?
- [ ] Do all charts look like they belong to the same app?

## Red Flags to Watch For
- Blank screens on first load
- No loading indicators
- Cryptic error messages
- No explanation of what the data means
- Inconsistent layout between pages
- Missing "What am I looking at?" context

## Page-Specific Checklist

### Dashboard (/)
- First impression: Can I tell this is a Chicago crime dashboard in 3 seconds?
- Hero: "Chicago crime data overview 2024–2026" — is this prominent?
- Loading: Do KPIs show skeleton shimmer while loading?
- Maps: Do maps show a loading state (not black boxes)?

### Crime Types (/crime-types)
- Is it clear this is about different types of crimes?
- Is there context for what each type means?

### Locations (/locations)
- Is it clear this is about geographic distribution?
- Do the maps make sense (not empty, not broken)?

### Analysis (/analysis)
- Is it clear this is a deep dive?
- Is the Key Insights section helpful for a first-timer?

### All Pages
- Does the sidebar make sense?
- Can I navigate without getting lost?
