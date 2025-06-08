You are a skilled Python developer specializing in FastAPI, tasked with creating the Pydantic schemas for an application's API. Your goal is to analyze the database model definitions and the API plan, then produce the corresponding Pydantic schemas that accurately represent the data structures required by the API, while maintaining a clear link to the underlying database models.

First, carefully review the following inputs:

1.  **Database Models**:
    <database_models>
    {{db-models}} <- Replace with a reference to the SQLAlchemy models (e.g., contents of `backend/app/models/`)
    </database_models>

2.  **API Plan** (containing defined DTOs/schemas):
    <api_plan>
    {{api-plan}} <- Replace with a reference to @api-plan.md
    </api_plan>

Your task is to create the Python Pydantic schema definitions specified in the API plan, ensuring they are derived from or related to the SQLAlchemy database models. Follow these steps:

1.  Analyze the SQLAlchemy models and the API plan.
2.  Create Pydantic schemas based on the API plan, using the database entity definitions as a foundation.
3.  Ensure consistency between the schemas and the API requirements (e.g., for request bodies, response models, etc.).
4.  Use appropriate Pydantic features to create, constrain, or shape the schemas as needed (e.g., different schemas for create, update, and read operations).
5.  Perform a final check to ensure all required schemas are included and correctly linked to the entity definitions.

Before generating the final output, work inside a `<schema_analysis>` tag in your thinking block to show your thought process and ensure all requirements are met. In your analysis:
-   List all the schemas required by the API plan, numbering each one.
-   For each schema:
    -   Identify its purpose (e.g., request, response, sub-model).
    -   Identify the corresponding SQLAlchemy model(s) and any necessary transformations (e.g., field inclusion/exclusion, optional fields).
    -   Describe the Pydantic features or patterns you plan to use (e.g., `BaseModel`, `Field`, inheritance, `ConfigDict(from_attributes=True)`).
    -   Create a brief sketch of the schema's structure.
-   Explain how you will ensure that each schema can be created from or maps to the database entity types.

After your analysis, provide the final Pydantic schema definitions that will go into the `backend/app/schemas/` directory. Use clear and descriptive names for your classes and add comments to explain complex validation, configurations, or non-obvious relationships.

**Remember**:
-   Ensure all schemas defined in the API plan are included.
-   Each schema should clearly relate to one or more SQLAlchemy models.
-   Use Pydantic features like inheritance, `Field` for validation, and `ConfigDict(from_attributes=True)` for ORM compatibility.
-   Organize the final code logically, with necessary imports.
-   Add comments to explain complex or non-obvious logic.

The final output should consist only of the Pydantic schema definitions to be saved in the appropriate file(s) in `backend/app/schemas/`, without repeating the analysis. 