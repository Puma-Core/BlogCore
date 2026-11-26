## Purpose

The `post-model` capability establishes the `Post` as the core content entity of the blog: it can be persisted to the database and managed through the Django admin interface.

## ADDED Requirements

### Requirement: Post persistence
The system SHALL persist blog posts. A post SHALL have a title, body content, an author, and timestamps recording when it was created and last updated.

#### Scenario: Applying migrations creates the posts table
- **WHEN** a developer runs the database migrations (`manage.py migrate`)
- **THEN** a table for posts exists in the database with columns for the identifier, title, content, author, and creation/update timestamps

#### Scenario: Creating a post
- **WHEN** a post is created through the ORM
- **THEN** the post is stored in the database with the values provided for its title and content, and the author and creation/update timestamps are recorded

### Requirement: Post management via admin
The system SHALL expose blog posts through the Django admin interface so that authenticated staff can create, view, edit, and delete posts.

#### Scenario: Posts listable in admin
- **WHEN** a staff user opens the posts section of `/admin/`
- **THEN** they see the list of existing posts identified by their title

#### Scenario: Creating a post from the admin
- **WHEN** a staff user submits the post creation form in `/admin/`
- **THEN** the post is saved with the provided title, content, and author