# Website delivery

## Product structure

Use only approved modules. Default candidates are a current briefing separated by topic, deep reads, video/live, the latest seven issues plus searchable monthly archive, a tagged personal library, email subscription after content, and localized language switching.

Keep past issues readable unless expiry is explicit. Never render blocked archive cards as normal links.

## Reading, translation, and copyright

An internal reader may show the site's own summary, metadata, image, and permitted embeds, with a visible original link. Do not reproduce full third-party articles without permission.

For bilingual learning, preserve English, reveal translation passage by passage, explain selected terms on hover/focus/tap, and label machine translation.

## Personal data and delivery

Use anonymous reading, browser-local saves without login, and optional email/account authentication for cross-device sync. Enforce cloud ownership server-side and never accept a client-selected owner ID. Keep newsletter consent/timezone/unsubscribe data separate from the library account.

Use IANA timezones. Track the last local issue date sent to handle retries and daylight-saving changes.

## Quality baseline

- Reuse design tokens and shared components.
- Prioritize content hierarchy over decorative copy.
- Check contrast in default, hover, active, disabled, and modal states.
- Prevent clipping of long Chinese and English titles.
- Provide accessible touch targets, focus states, reduced motion, and performant animation.
- Make dialogs closable by button, Escape, and appropriate backdrop interaction.
- Preserve functions at mobile widths and browser zoom.

Verify issue/localization completeness, source links, images, filters, search, every archive date, previous/next controls, local and cloud saves, account isolation, input readability, mobile language switching, schedule/timezone, production asset versions, and runtime errors.
