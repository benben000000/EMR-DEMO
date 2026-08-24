# Workspace Guidelines & Rules

Refer to [AGENTS.md](file:///Users/kloudtech/Project/AGENTS.md) and [.agents/rules/refactoring-and-personalization.md](file:///Users/kloudtech/Project/.agents/rules/refactoring-and-personalization.md) for complete workspace refactoring and personalization guidelines.

## Quick Summary
- **Personalization Assets**: Check `/Personalization/` (`logos/`, `theme/`, `hospital-info/`, `print-headers/`) for white-labeling files.
- **No Hardcoding**: Parameterize all hospital names, print formats, and styling via database parameters and CSS variables.
- **Backend DI**: Register new services in `DanpheServicesExtensions.cs`.
- **Frontend**: Maintain modular SPA structure, use CSS variables for theming, and preserve dual AD/BS date safety.
