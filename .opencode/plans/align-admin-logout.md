# Align Admin/Logout & Adjust Åtgärder Column

## Changes

### 1. `frontend/static/css/style.css` - Nav menu alignment
- Add `align-items: center` to `.nav-menu` so the Admin link text and logout icon align vertically

### 2. `frontend/static/css/style.css` - Åtgärder column width
- Add a new rule for `.news-table .actions` column cells (`th` and `td`) with `width: 80px; min-width: 80px; white-space: nowrap;` to fit the two 32px icon buttons snugly
