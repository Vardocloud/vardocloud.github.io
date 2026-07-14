# Zoom Webinar Registration — SPA Form Handling (29 Haz 2026)

## Summary
Zoom webinar registration forms use React-controlled combobox components that resist standard `browser_click` automation. Unlike Zoom meeting join (which hits reCAPTCHA), registration forms can be automated with the right element targeting.

## Registration Flow
1. Navigate to `https://[subdomain].zoom.us/j/[meeting-id]`
2. Fill text inputs (name, email, city) with `browser_type`
3. Country/Region combobox: click parent `generic` wrapper → listbox opens → click `option`
4. State/Province: same pattern → "Other" works for non-US
5. "How do you identify professionally?" combobox: same pattern — click parent wrapper, not the combobox itself
6. Register button: `browser_click`

## Critical Pattern — React Combobox
Zoom's comboboxes are React-controlled. The clickable element in the snapshot tree is:
```
- generic [ref=e22] clickable [cursor:pointer]
  - combobox "How do you identify professionally?" [expanded=false, required, ref=e35]
```

**Must click the PARENT generic** (e22), not the combobox (e35). After clicking, the listbox appears below the form with `option` elements. Then click the desired option.

## When Click Doesn't Register
If React state doesn't update after clicking an option (form still shows "required field" error):
1. Use `browser_console` to list all inputs: `document.querySelectorAll('input')`
2. Find the hidden text input with matching `aria-label`
3. Set its value via native value setter + dispatchEvent (see SKILL.md SPA section)

## reCAPTCHA Note
Registration forms may show a reCAPTCHA iframe after submit. On first visit, the form submits without CAPTCHA challenge. Second visit may show reCAPTCHA with disabled Register button — this is normal; the registration already went through.

## After Registration
- Success page shows: "You have successfully registered"
- Confirmation email sent to registrant
- URL format: `https://[subdomain].zoom.us/rest/webinar/registrant/[id]/info?tk=[token]&ac=approved`
- APA sends recording link "2 weeks after the live event"
- For live joining, the email contains the actual join link with auth token
