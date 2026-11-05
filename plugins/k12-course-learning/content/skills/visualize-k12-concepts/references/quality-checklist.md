# Quality checklist

## Teaching

- State one measurable learning goal.
- Name prerequisites and do not silently assume advanced knowledge.
- Make the interaction reveal a relationship, not merely animate an illustration.
- Keep facts, source material, assumptions, and analogies distinguishable.
- Include the boundary of every analogy or simplified model.
- Use a fresh check question instead of repeating the worked example.
- Hide recall answers until the learner chooses to reveal them.
- Do not expose a submitted homework answer as the lesson's check question.

## Content safety and accuracy

- Verify calculations, labels, units, directions, and graph relationships.
- Prefer the user's textbook over the bundled taxonomy when scope differs.
- Treat taxonomy retrieval as a candidate match and record the selected topic ID.
- Preserve Marble attribution when reusing taxonomy text.
- Do not invent curriculum alignment or claim evidence not present in supplied files.

## Interaction and accessibility

- Make every control keyboard reachable and visibly focused.
- Give range inputs an accessible label and live value.
- Do not rely on hover or color alone.
- Provide text equivalents for canvas observations.
- Respect `prefers-reduced-motion`.
- Keep touch targets at least 44×44 CSS pixels.
- Verify at 360 px width and at 200% browser zoom.

## Offline and privacy

- Produce one HTML file with embedded CSS, JavaScript, and lesson data.
- Reject runtime dependencies containing `http://`, `https://`, protocol-relative URLs, imports, iframes, analytics, or trackers.
- Do not use cookies, `localStorage`, service workers, authentication, forms that transmit data, or network requests.
- Keep all interaction state in page memory and discard it when the tab closes.

## Handoff

- Run the generator once with the example spec after changing the template.
- When the active runtime supports local preview, start a request-scoped local server, load the exact
  URL, and exercise the visual, quiz, recall reveal, keyboard focus, and narrow layout. Otherwise run
  static checks and disclose that browser interaction was not executed.
- Return the absolute HTML path, local URL when running, selected taxonomy topic, and any assumptions.
