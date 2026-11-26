## 1. Unified Admin Onboarding Group

- [x] 1.1 Create a reversible data migration that adds an onboarding group with only the `add_publicprofile` permission.
- [x] 1.2 Register the onboarding group name in settings or a module constant so tests and code refer to a single source of truth.
- [x] 1.3 Document that administrators must assign this group to staff accounts without a public profile; tool groups are assigned manually after onboarding.

## 2. PublicProfile on the Default Admin Site

- [x] 2.1 Remove the separate self-service `AdminSite` and the `/dashboard/` URL route.
- [x] 2.2 Register `PublicProfile` on the default `admin.site` with an owner-scoped `ModelAdmin`.
- [x] 2.3 Keep the dedicated `ModelForm` with only public fields, keyword-only `request.user`, editable initial values for `public_username`, `first_name`, and `last_name`, and server-side ownership assignment on save.
- [x] 2.4 Restrict queryset and object-level add/change/view/delete permissions to the current staff user's own profile.
- [x] 2.5 Preserve the existing scoped `change_form` override that hides breadcrumbs and the sidebar while keeping the top navbar and logout.

## 3. Onboarding Middleware

- [x] 3.1 Add middleware that runs after Django's authentication middleware and intercepts requests under `/admin/`.
- [x] 3.2 Redirect active staff users without a `PublicProfile` to the standard admin add view for `PublicProfile`.
- [x] 3.3 Exempt login, logout, password reset, and the public-profile add view from the redirect.
- [x] 3.4 Skip the check for non-staff and unauthenticated requests so the existing admin login controls handle them.
- [x] 3.5 Register the middleware in the project settings.

## 4. Group-Based Tool Access

- [x] 4.1 Verify that the onboarding group only grants access to the `PublicProfile` add view and nothing else in `/admin/`.
- [x] 4.2 Verify that other tool groups are ordinary Django groups with model permissions and have no automatic relationship to onboarding.
- [x] 4.3 Confirm that creating a profile does not modify the user's groups.

## 5. Flow Verification

- [x] 5.1 Add request-level tests that verify profileless staff users are redirected from `/admin/` and other admin routes to onboarding, and that they can log out.
- [x] 5.2 Add request-level tests that verify profileless staff with the onboarding group can submit valid and invalid native-admin onboarding forms, that the profile is tied to the session user, and that invalid submissions stay on the form.
- [x] 5.3 Add request-level tests that verify staff users with profiles but without tool groups see no tools, and that assigning a tool group reveals the corresponding admin sections.
- [x] 5.4 Add request-level tests that verify superusers without profiles are also redirected to onboarding.
- [x] 5.5 Add request-level tests that verify a user cannot list, view, edit, or create a profile for another user.
- [x] 5.6 Run `uv run python project/manage.py check` and `uv run pytest`.
