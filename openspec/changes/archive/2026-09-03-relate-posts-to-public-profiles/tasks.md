## 1. Post Author Model and Migration

- [x] 1.1 Change `Post.author` to a required foreign key to `PublicProfile` with a reverse relation for that profile's posts.
- [x] 1.2 Create a staged, atomic migration that preflights public-profile coverage, maps existing post authors, replaces the user relationship, and supports reverse mapping to users.
- [x] 1.3 Verify migrations apply successfully when every existing post author has a public profile and fail descriptively without changing posts when one is missing.

## 2. Django Admin

- [x] 2.1 Update `PostAdmin` to display and select the public-profile author efficiently in the post changelist and form.

## 3. Tests and Validation

- [x] 3.1 Add database-free unit tests for the `Post.author` field contract, reverse relation, and public-profile association.
- [x] 3.2 Add database-free unit tests for the post admin author configuration and changelist behavior.
- [x] 3.3 Run `uv run python project/manage.py test` and `uv run python project/manage.py check`.
