Users Table:

This table stores information about registered users of the website.
Columns:
-user_id (Primary Key): Unique identifier for each user.
-username: User's chosen username.
-password: User's hashed password.
-email: User's email address.
(other user-related information)
Books Table:

This table stores information about books available in the system.
Columns:
-book_id (Primary Key): Unique identifier for each book.
-title: Title of the book.
-author: Author of the book.
-publication_date: Date when the book was published.
-isbn: International Standard Book Number (ISBN) for the book.
(other book-related information)
BookLists Table:

This table stores information about user-created book lists (bklists).
Columns:
-list_id (Primary Key): Unique identifier for each book list.
-user_id (Foreign Key): References the user who created the list.
-list_name: Name of the book list.
-created_at: Timestamp indicating when the list was created.
BookListItems Table:

This table stores information about books added to user's book lists.
Columns:
-item_id (Primary Key): Unique identifier for each list item.
-list_id (Foreign Key): References the book list to which the book is added.
-book_id (Foreign Key): References the book being added to the list.
-added_at: Timestamp indicating when the book was added to the list.
