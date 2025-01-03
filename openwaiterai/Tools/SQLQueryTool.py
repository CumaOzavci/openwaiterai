import os
import ast
from typing import Optional

from langchain.tools import BaseTool
from langchain_community.utilities import SQLDatabase


class SQLQueryTool(BaseTool):
    """
    A LangChain tool for querying a SQL database.
    """

    debug: bool = False
    name: str = "SQLQueryTool"
    description: str = (
        "A tool to query a SQL database. Provide an SQL query as input, and it will return the results."
    )
    sql_database: Optional[SQLDatabase] = None

    def __init__(self, debug: bool = False):
        """
        Initializes the SQLQueryTool with a database connection string from environment variables.

        The following environment variables are used:
        - OPENWAITERAI_DB_HOST: The database host.
        - OPENWAITERAI_DB_PORT: The database port.
        - OPENWAITERAI_DB_NAME: The database name.
        - OPENWAITERAI_DB_USER: The database username.
        - OPENWAITERAI_DB_PASSWORD: The database password.
        """
        super().__init__()
        self.debug = debug
        db_host = os.getenv("OPENWAITERAI_DB_HOST", "localhost")
        db_port = os.getenv("OPENWAITERAI_DB_PORT", "5432")
        db_name = os.getenv("OPENWAITERAI_DB_NAME", "example")
        db_user = os.getenv("OPENWAITERAI_DB_USER", "user")
        db_password = os.getenv("OPENWAITERAI_DB_PASSWORD", "password")

        connection_string = (
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        self.sql_database = SQLDatabase.from_uri(connection_string)

    def _run(self, query: str) -> str:
        """
        Execute an SQL query and return the result as a string.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        if self.debug:
            print(f"DEBUG: Executing Query: {query}")
        try:
            result = self.sql_database.run(query)  # Use the run method
            if self.debug:
                print(f"DEBUG: Query Result: {result}")
            return str(result)
        except Exception as e:
            if self.debug:
                print(f"DEBUG: Error occurred: {str(e)}")
            return f"Error executing query: {str(e)}"

    async def _arun(self, query: str) -> str:
        """
        Asynchronously execute an SQL query. Not implemented in this tool.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: The query result.
        """
        raise NotImplementedError("Async query is not supported.")

    def get_schema_description(self):
        return """
You can access to restaurant database. Database is a SQL database. You can find database schema below:
-- == RESTAURANT INFO ==
CREATE TABLE RestaurantInfo (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL
);

-- == CATEGORIES ==
CREATE TABLE categories (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    description TEXT
);

-- == ALLERGENS ==
CREATE TABLE allergens (
    id INT PRIMARY KEY,
    name VARCHAR(100) UNIQUE
);

-- == INGREDIENTS ==
CREATE TABLE ingredients (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

-- == MENUITEMS ==
CREATE TABLE menuitems (
    id INT PRIMARY KEY,
    category_id INT,
    name VARCHAR(100),
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- == MENUITEMINGREDIENTS (join table for menuitems ↔ ingredients) ==
CREATE TABLE menuitemingredients (
    menu_item_id INT,
    ingredient_id INT,
    PRIMARY KEY (menu_item_id, ingredient_id),
    FOREIGN KEY (menu_item_id) REFERENCES menuitems(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- == MENUITEMALLERGENS (join table for menuitems ↔ allergens) ==
CREATE TABLE menuitemallergens (
    menu_item_id INT,
    allergen_id INT,
    PRIMARY KEY (menu_item_id, allergen_id),
    FOREIGN KEY (menu_item_id) REFERENCES menuitems(id) ON DELETE CASCADE,
    FOREIGN KEY (allergen_id) REFERENCES allergens(id) ON DELETE CASCADE
);

-- == NUTRITIONALVALUES ==
CREATE TABLE nutritionalvalues (
    id INT PRIMARY KEY,
    menu_item_id INT,
    calories NUMERIC(6,2),
    protein NUMERIC(6,2),
    carbohydrates NUMERIC(6,2),
    fats NUMERIC(6,2),
    saturated_fats NUMERIC(6,2),
    sugar NUMERIC(6,2),
    salt NUMERIC(6,2),
    fiber NUMERIC(6,2),
    FOREIGN KEY (menu_item_id) REFERENCES menuitems(id) ON DELETE CASCADE
);
"""

    def get_restaurant_description(self):
        query = "SELECT category, description FROM restaurantinfo;"
        rows_string = self.sql_database.run(query)

        try:
            # Safely parse the string to a list of tuples.
            rows = ast.literal_eval(rows_string)
        except (SyntaxError, ValueError) as e:
            # If parsing fails, handle it
            print(f"Could not parse result: {e}")
            return "You do not have any information about your restaurant."

        summary = ""
        categories = ""
        for row in rows:
            category, description = row
            if category == "summary":
                summary = description
            else:
                categories += f"- {category}\n"

        restaurant_description = f"General information about your restaurant: {summary}"
        restaurant_description += f"\nAlso, you can find the name of the restaurant info categories below\n{categories}"

        return restaurant_description

    def get_menu_description(self):
        """
        Returns a dictionary with a "categories" key, mapping to a list of
        { id, name, items } objects. Each "items" value is a list of { id, name }
        for the menu items in that category.
        """

        # SQL to fetch category and related menu item info
        query = """
                SELECT c.id AS category_id,
                    c.name AS category_name,
                    m.id AS item_id,
                    m.name AS item_name
                FROM categories c
                LEFT JOIN menuitems m
                    ON c.id = m.category_id
                ORDER BY c.id, m.id;
            """

        # Execute the query
        rows_string = self.sql_database.run(query)

        try:
            # Safely parse the string to a list of tuples.
            rows = ast.literal_eval(rows_string)
        except (SyntaxError, ValueError) as e:
            # If parsing fails, handle it
            print(f"Could not parse result: {e}")
            return {"categories": []}

        # We'll group them by category_id
        categories_map = {}
        for row in rows:
            cat_id, cat_name, item_id, item_name = row

            if cat_id not in categories_map:
                categories_map[cat_id] = {"id": cat_id, "name": cat_name, "items": []}

            # If a category has no items (item_id is None), skip adding item
            if item_id is not None:
                categories_map[cat_id]["items"].append(
                    {"id": item_id, "name": item_name}
                )

        # Convert to a list
        categories_list = list(categories_map.values())

        menu_description = f"You can find menu categories and contents below:\nmenu categories: {str(categories_list)}"

        return menu_description
