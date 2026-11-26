# post-model

## Purpose

The `post-model` capability establishes the `Post` as the core content entity of the blog: it can be persisted to the database and managed through the Django admin interface.

## Requirements

### Requirement: Post persistence

The system SHALL persist blog posts. A post SHALL have a title, body content, a public-profile author, a normalized `unique_name` derived from its title, and timestamps recording when it was created and last updated. The `unique_name` SHALL use lowercase words separated by hyphens, SHALL be suitable for use in a URL, and SHALL be unique for the combination of author and `unique_name`. The system MUST reject a duplicate combination rather than silently assigning the same identifier to two posts by one author.

#### Scenario: Applying migrations creates the posts table

- **WHEN** a developer runs the database migrations (`manage.py migrate`)
- **THEN** a table for posts exists in the database with columns for the identifier, title, content, normalized `unique_name`, public-profile author, and creation/update timestamps, plus a database constraint preventing duplicate author and `unique_name` combinations

#### Scenario: Creating a post

- **WHEN** a post is created through the ORM with a public profile as its author and a title
- **THEN** the system stores the post with the title, content, author, timestamps, and a `unique_name` generated from the normalized title

#### Scenario: Updating a title recalculates the identifier

- **WHEN** an existing post title is changed and the post is saved
- **THEN** its `unique_name` is recalculated from the new normalized title and the new author/`unique_name` combination is validated for uniqueness

#### Scenario: Equivalent titles collide for one author

- **WHEN** two posts by the same author normalize to the same `unique_name`
- **THEN** the system rejects the second create or update and preserves the existing post without silently adding a suffix

#### Scenario: Equivalent titles may exist for different authors

- **WHEN** two posts owned by different public profiles normalize to the same `unique_name`
- **THEN** both posts can be persisted and remain distinguishable by their author and `unique_name` combination

### Requirement: Post management via admin

The system SHALL expose blog posts through the Django admin interface so that authenticated staff can create, view, edit, and delete posts using a public profile as the author.

#### Scenario: Posts listable in admin

- **WHEN** a staff user opens the posts section of `/admin/`
- **THEN** they see the list of existing posts identified by their title

#### Scenario: Creating a post from the admin

- **WHEN** a staff user submits the post creation form in `/admin/` with a public profile as author
- **THEN** the post is saved with the provided title, content, and public-profile author

### Requirement: Safe author migration

The system SHALL preserve existing posts when changing their author relationship by assigning each post to the public profile associated with its existing user author. The system MUST stop the migration without modifying posts whose user author does not have a public profile.

#### Scenario: Migrating posts with public profiles

- **WHEN** the author migration runs and every existing post author has an associated public profile
- **THEN** every existing post retains its title, content, and timestamps and references the corresponding public profile

#### Scenario: Migrating a post whose author lacks a public profile

- **WHEN** the author migration finds an existing post whose user author has no associated public profile
- **THEN** the migration stops before changing any post data and identifies that a public profile must be created before it can proceed
