# Frontend — Public Showcase Pages

**Goal:** Port the existing `demo.html` to Vue components, creating the public-facing product showcase with filters, masonry grid, and detail modal.

**Depends on:** `01-scaffold.md`

---

## Task F3.1: Home page (product showcase)

**File:** `frontend/src/views/public/Home.vue`

Sections:
1. **Hero** — title "新品速递", subtitle, gradient background
2. **Filter card** — `FilterChips` component with three filter groups (form/effect/function tags fetched from API)
3. **Product grid** — CSS columns masonry layout (`columns:1` → `2` at 768px → `3` at 1024px). Each item is a `ProductCard` component.
4. **Detail modal** — `el-dialog` containing `ProductDetail` component, opened when clicking a card

Data flow:
- On mount: `tagsApi.list('form'/'effect'/'function')` + `productsApi.list({per_page:50})`
- Filter changes trigger re-fetch with `form_type_id/effect_type_id/function_type_id` params

---

## Task F3.2: ProductCard component

**File:** `frontend/src/components/ProductCard.vue`

Props: `product` (object)
Emits: `click`

Shows:
- Image (or gradient placeholder with icon if no image)
- Form/effect tags (colored badges)
- Product name (bold, 18px)
- Description (2-line clamp)
- Published date + arrow icon in footer

Hover: scale image, blue shadow, arrow slides right.

---

## Task F3.3: FilterChips component

**File:** `frontend/src/components/FilterChips.vue`

Props: `groups` (array of `{key, label, items}` where items are `[{id, name}]`)
Emits: `change(filters)` where filters is `{form_type_id: '', effect_type_id: '', function_type_id: ''}`

Renders one row per group. Each chip is a `<button>` with active state (blue bg + white text). Clicking a chip toggles it; clicking again deselects. Clicking different chip in same group switches selection.

---

## Task F3.4: ProductDetail component

**File:** `frontend/src/views/public/ProductDetail.vue`

Props: `product` (object)

Two-column layout on desktop (image left, info right). Shows:
- Full-size product image
- Product name, published date
- All three tag types as colored badges
- Description section
- Ingredients section (pre-wrapped text)

---

## Task F3.5: Commit

```bash
git add frontend/src/views/public/ frontend/src/components/ProductCard.vue frontend/src/components/FilterChips.vue
git commit -m "feat: add public showcase pages"
```
