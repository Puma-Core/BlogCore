## Context

`Post.author` currently is a required foreign key to `auth.User`, while `PublicProfile` is a one-to-one extension of that user and contains the information intended for public use. See `proposal.md` and the `post-model` delta for the required behavior.

## Goals / Non-Goals

**Goals:**
- Make `PublicProfile` the required author reference for every post.
- Preserve existing posts only when their current user author has a public profile.
- Keep Django admin usable for selecting and inspecting a post's public-profile author.

**Non-Goals:**
- Creating missing public profiles or fabricating their public fields during migration.
- Adding public post pages, templates, URLs, serializers, or APIs.
- Changing the fields or validation rules of `PublicProfile`.

## Decisions

### Store a direct foreign key to `PublicProfile`

`Post.author` will target `profiles.PublicProfile` with a reverse relation for that profile's posts. This exposes the public identity directly to content consumers and prevents them from starting at an authentication account. A derived property over the existing user foreign key was rejected because it leaves the persistence contract tied to private account data and makes public-profile availability optional at read time.

### Use a staged, atomic data migration

The migration will add a temporary nullable profile foreign key, preflight every existing post author for an associated public profile, populate the temporary field, remove the user foreign key, rename the profile field to `author`, and make it required. The preflight executes before any post data is updated; a missing profile raises a descriptive migration error and rolls back the atomic migration. Creating default profiles was rejected because required public content cannot be inferred safely.

The reverse migration will restore a temporary user reference from each profile's one-to-one user, then restore the original `author` field. It will similarly fail if a referenced public profile no longer has an associated user.

### Show the public-profile author in Django admin

The existing `PostAdmin` will include the author in its list display and use related-object selection/query behavior appropriate for the profile relation. This keeps staff workflows aligned with the changed model contract. Leaving the author out of list display was rejected because staff could no longer identify the public identity assigned to a post at a glance.

### Keep tests database-free where possible

Unit tests will assert field metadata, reverse relation behavior through mocks or model instances, admin configuration, and the data-migration mapping helpers without a database. Migration execution that depends on Django's schema editor remains a focused integration concern and will be covered only if the project test conventions require it.

## Risks / Trade-offs

- [Existing author lacks a public profile] -> The preflight aborts before changing posts and reports the affected user so the data can be prepared deliberately.
- [Migration rollback after deployment] -> Reverse mapping uses the profile's one-to-one user and aborts if the association is no longer valid.
- [Cross-app migration dependency] -> Depend on the migration that creates `PublicProfile` and use the historical app registry inside migration code.
- [Admin relation query overhead] -> Select the author relation for changelist queries when Django admin evaluates the list.

## Migration Plan

1. Verify each user who authors an existing post has a `PublicProfile`; create or correct profiles outside this migration where necessary.
2. Apply the staged migration, which validates first and then maps each post to its author's profile.
3. Verify the post admin can create and list posts using public-profile authors.
4. If rollback is required, reverse the migration before removing public profiles so their linked users remain available for reverse mapping.
