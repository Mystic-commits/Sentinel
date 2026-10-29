# Sentinel production launch plan

Prepared 29 October 2026. Individuals and business teams are equal launch priorities, per product direction.

## Product and architecture

One local agent owns scanning, inference, review, execution, and local audit history. The public website explains the product and distributes signed builds. A separate business control plane manages organization membership, device enrollment, policies, and billing. It must never accept arbitrary filesystem paths from internet callers. File contents and prompts stay on devices by default; business telemetry requires an explicit documented policy.

| Individual edition | Business edition | Shared foundation |
|---|---|---|
| Folder selection and model setup | Organization creation and invitations | Local inference and strict plan validation |
| Preview, approve/reject, execution receipt | Owner/admin/member permissions | Durable task state and crash recovery |
| Local preferences and recovery UI | Signed policy distribution and device enrollment | Collision protection and audit records |
| Clear free/paid limits if monetized | Tenant isolation and audit export | Signed updates and offline support |

## Findings and initial repairs

The audit found scope errors classified as warnings, approval selections ignored by execution, no execution replay guard, hardcoded developer logging, symlink traversal, fabricated API undo completion, stale tests, a mismatched Poetry lock, and vulnerable frontend dependencies.

The initial repair branch addresses these issues, restores full test collection, upgrades frontend dependencies, makes local-model configuration explicit, constrains JSON generation, and removes unverified testimonials from the homepage. These changes establish a safer developer preview, not production certification.

## Release work in dependency order

1. **Durable safety foundation:** replace the in-memory task store with transactional persistence; record immutable plan revisions, selected approvals, operation receipts and actual task timestamps. Require audit storage before mutation. Persist and recover interrupted jobs. Restrict creation to approved directories. Add source identity/hash checks and race-resistant operations so file or symlink replacement between review and execution cannot escape validation. Never overwrite during rollback or undo. Exit gate: crash/restart, concurrent requests, collision and race tests pass with no lost data.
2. **Complete local workflow:** wire scan IDs, custom prompts and depth consistently; surface scan errors; bound files and prompt tokens; add cancellation, queue limits and deterministic no-model mode. Integrate durable undo for moves with collision checks; explain manual Trash recovery for deletions. Finish CLI apply/plan persistence. Exit gate: real scan → plan → selected review → execute → restart → undo succeeds on all supported platforms using disposable datasets.
3. **Local AI quality:** evaluate Qwen3 4B and at least one smaller model on labelled organization fixtures. Measure schema validity, incorrect moves, unsafe proposals, time, memory and fallback rate. Pin model digest and license. Enforce local-only runtime, refuse remotely backed model aliases, and test offline startup. Exit gate: documented hardware matrix and release thresholds met. Current check verifies structured inference with installed Llama 2; it does not validate Qwen3 quality or latency.
4. **Business product:** implement organization membership, invitations, roles, policy versioning, device pairing/revocation, tenant isolation and scoped audit export. Keep business control plane separated from local filesystem APIs. Exit gate: cross-tenant and unauthorized-role access tests fail closed; policy enforcement is deterministic on device.
5. **Individual product and commercial flows:** onboarding, model health/model download progress, folder permissions, review accessibility, understandable error handling, settings, data export/delete and recovery guidance. Add billing only after tier limits and provider are selected. Exit gate: new users complete the workflow without terminal intervention.
6. **Website and distribution:** distinct Personal and Business journeys, truthful feature availability, real screenshots, verified customer evidence, working contact/demo flow, support policy and product-specific privacy/terms. Replace zero-byte installer placeholders with signed/notarized builds, checksums, SBOMs and a verified update channel. Exit gate: download/install/update/uninstall pass on macOS, Windows and Linux release targets.
7. **Operations and rollout:** dependency and secret scanning, reproducible builds, required CI checks, backup/restore drills, structured logs with redaction, rollback instructions, release ownership and opt-in error diagnostics. Run individual and business pilots in parallel before general availability. Exit gate: restore drill, security review and documented pilot acceptance pass.

## Decisions still needed

Target minimum RAM/GPU and supported OS versions; deployment/domain to preserve; team hosting requirements; organization identity provider; pricing and billing provider; support contact and ownership. Do not invent credentials, customer testimonials or legal commitments.

## Local model references

- [Ollama generation API](https://docs.ollama.com/api/generate): JSON schema format and thinking controls.
- [Ollama FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.mdx): local-only configuration.
- [Qwen3 upstream](https://github.com/QwenLM/Qwen3): model variants and licensing; verify the exact checkpoint before redistribution.
