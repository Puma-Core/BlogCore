## MODIFIED Requirements

### Requirement: Post persistence
The system SHALL persist blog posts. A post SHALL have a title, body content, a public-profile author, and timestamps recording when it was created and last updated. The author SHALL identify a `PublicProfile`, making that profile's public information available to downstream consumers of the post.

#### Scenario: Applying migrations creates the posts table
- **WHEN** a developer runs the database migrations (`manage.py migrate`)
- **THEN** a table for posts exists in the database with columns for the identifier, title, content, public-profile author, and creation/update timestamps

#### Scenario: Creating a post
- **WHEN** a post is created through the ORM with a public profile as its author
- **THEN** the post is stored in the database with the values provided for its title and content, and the public-profile author and creation/update timestamps are recorded

### Requirement: Post management via admin
The system SHALL expose blog posts through the Django admin interface so that authenticated staff can create, view, edit, and delete posts using a public profile as the author.

#### Scenario: Posts listable in admin
- **WHEN** a staff user opens the posts section of `/admin/`
- **THEN** they see the list of existing posts identified by their title

#### Scenario: Creating a post from the admin
- **WHEN** a staff user submits the post creation form in `/admin/` with a public profile as author
- **THEN** the post is saved with the provided title, content, and public-profile author

## ADDED Requirements

### Requirement: Safe author migration
The system SHALL preserve existing posts when changing their author relationship by assigning each post to the public profile associated with its existing user author. The system MUST stop the migration without modifying posts whose user author does not have a public profile.

#### Scenario: Migrating posts with public profiles
- **WHEN** the author migration runs and every existing post author has an associated public profile
- **THEN** every existing post retains its title, content, and timestamps and references the corresponding public profile

#### Scenario: Migrating a post whose author lacks a public profile
- **WHEN** the author migration finds an existing post whose user author has no associated public profile
- **THEN** the migration stops before changing any post data and identifies that a public profile must be created before it can proceed
