## MODIFIED Requirements

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
