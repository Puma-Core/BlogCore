## Purpose

Lets authors compose posts in a Markdown-rich editor while retaining portable source content.

## ADDED Requirements

### Requirement: Post authoring uses a Markdown rich text editor
The post authoring form MUST render a Vditor-based editor for `Post.content`, configured to produce Markdown rather than HTML as its submitted value.

#### Scenario: Author opens a new post form
- **WHEN** an authorized author opens the post creation form
- **THEN** the content control is initialized as a Vditor editor with Markdown output enabled
- **AND** the editor is configured to use the application's attachment upload endpoint for images.

#### Scenario: Author edits an existing Markdown post
- **WHEN** an authorized author opens an existing post
- **THEN** the editor is initialized with the stored Markdown content
- **AND** saving without content changes preserves the Markdown representation.

### Requirement: Markdown is the persisted post content
The system MUST persist the editor's Markdown value in `Post.content` without replacing it with generated HTML or editor-specific JSON.

#### Scenario: Author saves formatted content
- **WHEN** an authorized author saves a post containing headings, emphasis, links, and an image reference
- **THEN** `Post.content` contains the corresponding Markdown source
- **AND** the existing post API returns that Markdown source in its content field.

#### Scenario: Existing content remains compatible
- **WHEN** a post contains content saved before the editor integration
- **THEN** the form loads that content as-is
- **AND** saving the post does not require a data migration or HTML conversion.

### Requirement: Editor integration preserves server-side validation
The system MUST continue to apply server-side form/model validation when content is submitted through Vditor and MUST NOT trust client-side editor configuration as a security boundary.

#### Scenario: Invalid post data is submitted
- **WHEN** the post form fails existing validation
- **THEN** the form is redisplayed with validation errors
- **AND** no invalid post content or attachment association is persisted.
