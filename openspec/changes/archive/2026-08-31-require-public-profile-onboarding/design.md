## Context

`PublicProfile` is a one-to-one extension of the authentication user. The project already exposes Django's staff-oriented admin at `/admin/`; the prior separate self-service admin route must be removed. The onboarding flow is therefore limited to active staff accounts and uses standard Django groups and permissions to expose administrative tools. See `proposal.md` and the two specification deltas for the required behavior.

## Goals / Non-Goals

**Goals:**
- Use one standard Django admin entry point at `/admin/` for onboarding and all authorized tools.
- Keep every staff account without a public profile confined to its own profile-creation form.
- Use Django groups and permissions to define tools available after onboarding.
- Leave the assignment of post-onboarding tool groups to an administrator.
- Preserve server-derived, immutable public-profile ownership and the native admin form UI.

**Non-Goals:**
- Supporting onboarding for non-staff accounts.
- Automatically adding, removing, or choosing a user's post-onboarding groups.
- Public presentation pages, APIs, social-link management, or a separate dashboard route.
- Changing the user model or inferring missing public-profile values.

## Decisions

### Use the default Django admin at `/admin/`

The existing `admin.site` will register `PublicProfile` and serve both onboarding and authorized tools. The `/dashboard/` URL and separate `AdminSite` will be removed. This gives users a single location and lets Django's existing group-permission system govern registered models. Retaining a separate site was rejected because it duplicates the admin entry point and separates tools the user wants unified.

### Gate profileless staff accounts with admin middleware

A middleware positioned after Django's authentication middleware will inspect `/admin/` requests. An active staff user without a `PublicProfile` will be redirected to the standard admin add view for `PublicProfile`; login, logout, and that add view are exempt. The middleware applies independently of a user's group permissions, including for superusers, so no profileless staff account can reach other tools. Relying solely on per-model permissions was rejected because it does not prevent direct navigation to already-permitted or superuser tools before onboarding.

### Use groups for onboarding and post-onboarding tools

A data migration will create an onboarding group with only the `add_publicprofile` permission. Staff accounts awaiting onboarding are assigned to this group by an administrator. Existing or future tool groups grant model permissions through Django's standard permission system; after a profile is created, an administrator manually assigns the appropriate tool groups. Automatic membership changes were rejected because tool access is an administrative decision, not a consequence that can be inferred from profile completion.

### Restrict the public-profile ModelAdmin to its owner

The default-site `PublicProfileAdmin` will use an owner-scoped queryset and object-level add/change/view rules. Its form includes only public fields, receives `request.user` for editable initial values, and saves the owner from the request rather than input data. A limited `change_form` override may hide breadcrumbs and the sidebar while retaining native controls and logout. Letting group permissions alone control profile objects was rejected because Django model permissions are not object-specific.

### Add database-backed admin flow tests

Tests will use Django's test client, staff users, groups, and `PublicProfile` records to validate middleware redirects, permitted onboarding, logout, group-gated tool visibility, and owner isolation. Unit tests continue to cover form and ModelAdmin behavior, but mock-only tests were rejected for the group and middleware contract because it depends on real sessions and permissions.

## Risks / Trade-offs

- [Staff account lacks onboarding group] -> It cannot access the profile form; administrators must assign the onboarding group deliberately.
- [Profileless superuser reaches a tool] -> Middleware redirects all profileless staff accounts before the standard admin view executes.
- [User remains in onboarding group after creation] -> The user sees only permissions granted by that group until an administrator assigns tool groups.
- [A client forges a user identifier] -> The form never accepts ownership input and the admin saves `request.user`.
- [Middleware loops on onboarding] -> Explicitly exempt the standard admin add, login, and logout URLs.

## Migration Plan

1. Add the onboarding group and its `PublicProfile` add permission with a reversible data migration.
2. Register the owner-restricted profile admin on the default site, remove the separate site and `/dashboard/` route, and add the admin onboarding middleware.
3. Assign the onboarding group to existing profileless staff accounts as an explicit administrative preparation step.
4. Verify profileless staff are redirected to onboarding, can log out, and see no other tools; verify staff with profiles see only group-authorized tools.
5. Roll back application code and remove or reverse the group migration if necessary; existing profile data remains unchanged.
