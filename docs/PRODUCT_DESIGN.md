# Sentinel workspace design

## Product position

Sentinel helps people organize scattered local files while retaining control over each proposed change. Trust, explainability and repeatable organization are the product's strongest initial value. A preview is valuable before execution: users can see destinations and reasoning rather than trusting an opaque cleanup button.

Individuals need low-friction orientation and a way to try the product without risking files. Technical users need explicit scope, useful records and terminal access. Teams eventually need centrally enforced policies and permissions; the interface must not imply those exist today.

## Design system

Warm paper surfaces, a charcoal-green navigation rail, restrained green accents, generous spacing and consistent line icons. Inter handles navigation and work; a serif italic headline adds character without turning the workspace into a marketing page. Small text has explicit contrast and visible keyboard focus. Mobile navigation uses a compact top rail, not three panels stacked above the task.

## Implemented journeys

- Workspace: choose a recipe or write instructions, set folder scope, request a preview.
- Sample workspace: clearly labelled synthetic data; select changes, cancel confirmation, simulate completion. It never calls filesystem execution.
- Recipe library: reusable defaults, custom recipes stored in the browser, removal of custom recipes.
- Review: file reasoning, source/destination, search, original-index selection, explicit final confirmation and report export.
- History: persisted sessions from the local agent, search, real state and timestamps, reopen a session.
- Activity: actual stored receipts and interrupted-session guidance.
- Command search: Cmd/Ctrl+K, session search and navigation actions.
- Terminal guide: real supported commands, copy button, setup prerequisites.
- Agent connection: health checks and explicit setup instructions; the interface does not pretend installation is automatic.

## Quality boundaries

No fabricated usage metrics, testimonials, team accounts, model-ready indicators, cloud storage integration or working undo claims. Browser recipes are local to that browser, not team policies. The sample session is never presented as a real scan. General agent health does not establish model readiness.

The filesystem engine still needs race protection, authenticated device pairing, complete crash reconciliation and safe undo before public production release. Native folder selection and automatic local setup remain major onboarding opportunities. Actual performance and user comprehension need pilot evaluation.

## Verified interactions

Browser checks covered the sample approval/cancel/completion flow; applying a real move to an agent-created disposable file; saved recipe creation, persistence after reload and removal; terminal command copying; filtering and reopening persisted sessions through command search; receipt viewing and report download. The no-model planning route produced a real validated preview and its selected execution preserved the synthetic file's contents. Desktop and mobile breakpoints were visually inspected. Full Python suite: 141 passing tests at this iteration; frontend lint, TypeScript and production static build pass.

File type rules organize only recognized top-level documents, media and archives. Existing folders, code/unsupported types and destination collisions are left alone. AI fallback is disclosed rather than presented as successful interpretation of custom instructions.
