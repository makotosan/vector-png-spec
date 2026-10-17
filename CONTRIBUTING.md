# Contributing

Open issues/PRs describing the interoperability problem, proposed normative text,
wire compatibility impact, security implications and positive/negative examples.
Keep implementation preferences separate from mandatory file-format rules.

English SPEC.md is normative. SPEC.ja.md is its full informative translation.
Add fixture cases for testable rules. Do not embed executable payloads or
live external URLs in fixtures; use inert text and reserved example.invalid URLs.
Run both checks in README before submitting.

This is an experimental draft; no stable v1 release is declared. Incompatible
wire changes require a new keyword/proposal. Registry fields, checksums, signatures
and native document payloads are out of scope until explicitly specified.
Contributions are accepted under the repository's MIT license. Do not copy
third-party specification prose or assets without an appropriate license.

## English and Japanese documentation

[日本語](CONTRIBUTING.ja.md)

The repository-wide rules in [AGENTS.md](AGENTS.md) require complete content
parity between English documents and their Japanese counterparts. Translations
must not be summaries. Keep sections, requirement strength, conditions, exceptions,
numbers, identifiers, examples, commands, links, warnings, limitations, status
and compatibility claims equivalent; natural phrasing and localized headings or
link labels may differ.

Update both languages in the same change, whichever language is edited first.
Apply additions, edits and deletions to both. Every Japanese document must have
an English counterpart; preserve pairings and navigation on creation or rename.
English-only documents do not all require a Japanese translation, but existing
translations must remain complete and synchronized.

Compare affected pairs section by section, including tables, code blocks and
references, before completing a change. Include the checked pairs and parity
confirmation in the issue/PR or change description. Structural checks do not
prove semantic equivalence. SPEC.md remains normative; translation alone must
not change wire requirements or give the Japanese text precedence.
