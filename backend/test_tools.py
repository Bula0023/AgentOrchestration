from tools.web_search import web_search
from tools.schemas import WebSearchInput, DatabaseQueryInput, FileReadInput
from tools.database import query_database
from tools.implement_tool import read_file
import sqlite3
from tools.tool_registry import registry
from agents.research import research_node
from routing.routes import route_after_specialist
# result = read_file(
#     FileReadInput(
#         path="/Users/horoombula/Projects/Agent Orchestration/backend/test.txt"
#     )
# )

# print(result)

# result = web_search(
#     WebSearchInput(
#         query="What is GraphRAG?"
#     )
# )

# print(result)



# Connect to the database (creates app.db if it doesn't exist)
# conn = sqlite3.connect('app.db')
# cursor = conn.cursor()

# # Create the users table
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     email TEXT NOT NULL UNIQUE,
#     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# )
# ''')

# # Insert sample data
# cursor.executemany('''
# INSERT INTO users (name, email) VALUES (?, ?)
# ''', [
#     ('Alice', 'alice@example.com'),
#     ('Bob', 'bob@example.com'),
#     ('Charlie', 'charlie@example.com')
# ])

# # Commit changes and close the connection
# conn.commit()
# conn.close()

# result = query_database(
#     DatabaseQueryInput(
#         query="SELECT * FROM users"
#     )
# )

# print(result)

# result = registry.invoke_tool(
#     tool_name="web_search",
#     specialist="research",
#     inputs={
#         "query": "What is GraphRAG?"
#     }
# )
# print(result)

# registry.invoke_tool(
#     tool_name="file_read",
#     specialist="research",
#     inputs={
#         "path": "notes.txt"
#     }
# )


# registry.invoke_tool(
#     tool_name="file_write",
#     specialist="writing",
#     inputs={
#         "path": "output.txt",
#         "content": "This is a test content"
#     }
# )

# result = registry.invoke_tool(
#     tool_name="code_execution",
#     specialist="code",
#     inputs={
#         "code":"print(1/0)",
#         "language": "python"
#     }
# )
# print(result)
# registry.invoke_tool(
#     tool_name="database_query",
#     specialist="data",
#     inputs={
#         "query": "SELECT * FROM users"
#     }
# )
# registry.invoke_tool(
#     tool_name='api_call',
#     specialist='research',
#     inputs={
#         'url': 'https://api.example.com/data',
#         'method': 'GET',
#         'body': None
#     }
# )

# state = {
#     "task": "Explain GraphRAG",

#     "current_subtask": {
#         "id": "task_1",
#         "description": "Research what GraphRAG is",
#         "specialist": "research",
#         "required_inputs": [],
#         "dependencies": [],
#         "expected_output_format": "Short explanation",
#         "complexity": "low"
#     },

#     "current_subtask_id": "task_1",

#     "review_feedback": "None",
#     "retry_count": 0,
# }


# result = research_node(state)

# print(result)

state = {
    "specialist_success": True
}

print(route_after_specialist(state))

state = {
    "specialist_success": False
}

print(route_after_specialist(state))

from routing.routes import route_confidence


print(
    route_confidence({
        "specialist_confidence": 0.9
    })
)

print(
    route_confidence({
        "specialist_confidence": 0.3
    })
)