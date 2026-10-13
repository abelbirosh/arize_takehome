---
name: System one research presentation
description: An editorial reader for research on agent routing.
colors:
  paper: "#f6f5f0"
  ink: "#252c29"
  muted: "#646c62"
  rule: "#dcded4"
  accent: "#e8ee95"
  dark: "#263b31"
  soft: "#eeeee5"
  focus: "#476542"
  selected-navigation: "#e9ecd9"
  diagram-surface: "#eeefe5"
  pending-indicator: "#858c5a"
  ready-indicator: "#3c734c"
  error-surface: "#f3e2d9"
  error-text: "#783f29"
typography:
  display:
    fontFamily: "Times New Roman, Times, serif"
    fontSize: "clamp(48px, 4.9vw, 78px)"
    fontWeight: 400
    lineHeight: 1.04
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Times New Roman, Times, serif"
    fontSize: "clamp(42px, 4.5vw, 68px)"
    fontWeight: 400
    lineHeight: 1.06
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Times New Roman, Times, serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: 1.5
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Times New Roman, Times, serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.8
  label:
    fontFamily: "Times New Roman, Times, serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.5
rounded:
  control: "4px"
  panel: "5px"
  diagram: "8px"
spacing:
  tight: "8px"
  small: "12px"
  medium: "20px"
  large: "24px"
  section: "30px"
  expansive: "35px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "14px 18px"
    typography: "{typography.label}"
  button-primary-hover:
    backgroundColor: "{colors.dark}"
    textColor: "{colors.accent}"
  button-outline:
    rounded: "{rounded.control}"
    padding: "13px 16px"
    typography: "{typography.label}"
  navigation-current:
    backgroundColor: "{colors.selected-navigation}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  routing-diagram:
    backgroundColor: "{colors.diagram-surface}"
    rounded: "{rounded.diagram}"
    padding: "24px 24px 18px"
  action-selected:
    backgroundColor: "{colors.accent}"
    rounded: "{rounded.control}"
  empty-evidence:
    rounded: "{rounded.panel}"
    padding: "30px"
---

# Design System: System one research presentation

## Overview

**Creative North Star: "Conference proceedings"**

Conference proceedings translated into a presentation reader: large editorial titles, an open paper surface, a numbered chapter index, and linked research notes. This description records the implemented visual world; it is not a claim of user-approved qualitative preferences.

The hierarchy gives the question prominence while keeping mechanisms, planned comparisons, and supplied evidence readable. Pending content has its own explicit visual state rather than simulated findings.

**Key Characteristics:**
- Paper surfaces and hairline rules.
- Times New Roman throughout, with size, bold weight, and italic emphasis establishing hierarchy.
- Restrained forest and lime accents.
- Explicit pending, loaded, and error states.

## Colors

The palette combines warm paper neutrals with a forest decision surface and a pale lime selection accent. Values in the frontmatter are normative.

### Primary
- **Forest decision surface** (`dark`): the primary-action hover.
- **Lime selection** (`accent`): the text selection and primary-action hover lettering.

### Neutral
- **Paper** (`paper`): page and reading backgrounds.
- **Ink** (`ink`): primary text and primary buttons.
- **Muted olive gray** (`muted`): explanatory copy and metadata.
- **Hairline rule** (`rule`): structural separators and control outlines.
- **Soft paper** (`soft`): quiet hover fills.
- **Selected navigation** and **diagram surface**: related pale fills for position and mechanism grouping.

### States
- **Focus forest** (`focus`): keyboard outlines and link hover.
- **Pending indicator** and **ready indicator**: status dots accompanied by text.
- **Error surface** and **error text**: the dismissible research-load error notice.

**The Accent Rule.** Use the forest-and-lime pairing sparingly on interactive states; keep reading surfaces on paper.

## Typography

**Font Family:** Times New Roman, with Times and serif fallbacks. The user explicitly requested this family for all text, including controls, navigation, metadata, and diagrams. It uses the device's installed font; no webfont assets are loaded.

### Hierarchy
- **Display:** the large opening question, regular weight with italic emphasis.
- **Headline:** chapter titles at the existing responsive display scale, regular weight.
- **Title:** subsection labels use bold Times New Roman; evidence titles use larger bold Times New Roman.
- **Body:** regular Times New Roman with generous line height and bounded reading measure.
- **Label:** navigation, diagram labels, controls, and metadata use smaller sizes; selected and emphasized labels use bold.

**The Single Family Rule.** Establish levels through Times New Roman's size, regular/bold weight, and italics. Do not mix font families.

## Layout

The desktop shell has an 88px header and a 228px chapter index beside a fluid reading area. The main area is capped at 1600px with responsive horizontal padding. Content occupies the available height, with the chapter footer below it. Cover content is an open text composition; internal chapters use open rows, tables, and rule-separated sections.

At 1100px and below the index narrows to 190px. At 820px and below it becomes a wrapping two-column chapter index. All labels remain fully visible, including long section names. At 600px and below the cover and mechanism collapse to a single column, with 22px main-side padding. Wide tables scroll within their own wrapper. A 1550px minimum-width adjustment increases upper spacing.

Spacing uses compact 8–12px control gaps, 20–24px grouping, and 30–35px section breathing room, alongside responsive larger chapter separations. Presentation mode hides the index and expands the question. Print hides shell controls and retains the reading content.

## Elevation & Depth

The system has no box shadows. Tonal paper fills group mechanisms, while thin borders and whitespace separate the narrative. The page stays flat and open; flowcharts are deferred.

**The Flat Reading Surface Rule.** Separate content with spacing, hairline rules, and tonal fills; the implementation uses no box shadows.

## Shapes

Controls use gently rounded corners and thin borders. One-pixel rules remain visible. The previous-page control is circular, as are status dots; keyboard hints use compact outlined key shapes. Pending evidence uses a dashed enclosure. No large pill-shaped card vocabulary is established.

## Components

### Buttons
Primary actions are compact ink rectangles with paper lettering, 46px minimum height, and forest/lime hover. Outline actions share that minimum height and use a thin border; their hover fill is paper. Presentation controls use a slightly softer corner and a soft hover fill. Text actions remain visually quiet. Disabled buttons use 0.4 opacity and the default cursor. Buttons and links retain a 2px focus outline offset by 5px.

### Navigation
The chapter index combines two-digit numbers and sentence-case labels. A pale selected fill, bold text weight, and inline arrow identify the current chapter. On narrow screens the arrow disappears and the index scrolls; changing chapters automatically brings the active section into view. The top of the reading area shows only chapter position, avoiding a redundant current-chapter label. Previous and next actions remain at the foot; keyboard navigation also supports arrows, Page Up/Down, Home, and End.


### Pending and loaded evidence
An empty findings panel has a dashed outline, a small abstract chart illustration, and explicit awaiting-research text. Practice recommendations remain visibly pending. Supplied evidence becomes rule-separated text articles, preserving long text wrapping. Ready and pending statuses use both a dot and words.

### Tables and source rows
Comparison tables have open cells separated by horizontal rules, with muted column headings and readable row labels. Source rows pair title and hostname with an inline SVG arrow; hover underlines the title. On mobile the table scrolls independently.

### Attached references
Research notes keep supporting links immediately below their text. Links form a wrapping inline list with a small external-arrow SVG, forest text, and a quiet underline; hover changes both text and underline to ink. The list starts 18px below the note, with 10px row gaps and 22px column gaps (18px on mobile). Link text stays at 12px with a 1.6 line height, wraps long words, retains the shared keyboard focus outline, and opens references in a new tab.

### Challenge and solution pairs
Each note keeps its serif article title above two equal columns, labeled Challenge and Solution in 12px bold Times New Roman. The pair starts 20px below the title, with a 36px column gap and 14px supporting text at 1.85 line height. At 600px and below the pair stacks in reading order, the gap becomes 20px, and supporting text becomes 13px. Attached references follow the complete pair. This extends the existing rule-separated article pattern without new surface or color tokens.

### Notices
Research loads automatically from the hosted JSON file. There are no research upload, file-picker, or download controls. Dismissible research-load errors use the warm error surface and alert semantics; presentation-mode feedback uses the status surface.

Chapter changes reveal content over 0.42s with an 8px upward travel and a shallow clip. Link/button color and background transitions take 0.18s. Reduced-motion mode removes animations and transitions.

## Do's and Don'ts

### Do:
- **Do** preserve the paper, ink, forest, and lime roles defined by the frontmatter.
- **Do** keep chapter navigation, current position, and previous/next controls clear.
- **Do** distinguish pending evidence from supplied findings using explicit status text.
- **Do** retain visible keyboard focus and respect reduced-motion preferences.
- **Do** wrap the full chapter wording in the mobile index while page content remains within the viewport.

### Don't:
- **Don't** add invented result values or treat the empty-chart illustration as measured data.
- **Don't** repeat the current chapter name as an eyebrow above its title.
- **Don't** replace the open, rule-separated composition with a generic shadowed-card grid.
- **Don't** infer additional approved aesthetic preferences from this observed implementation.

The header is the text-only title “When and When Not to Jev”, with no adjacent mark. The browser favicon is a three-slice pie in the chart colours (green, amber, blue). Current sections are Question, Methodology, Detailed results, How I used Phoenix?, What went wrong and how we fixed it?, and Takeaways. No flowcharts appear in the interface.
