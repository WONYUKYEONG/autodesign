"""프로젝트 CRUD"""
from db.database import execute_query, fetch_all, fetch_one


def create_project(name, description=""):
    return execute_query(
        "INSERT INTO projects (name, description) VALUES (?, ?)",
        (name, description)
    )


def get_project(project_id):
    return fetch_one("SELECT * FROM projects WHERE id = ?", (project_id,))


def list_projects():
    return fetch_all("SELECT * FROM projects ORDER BY updated_at DESC")


def update_project(project_id, name, description=""):
    execute_query(
        "UPDATE projects SET name=?, description=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (name, description, project_id)
    )


def delete_project(project_id):
    execute_query("DELETE FROM projects WHERE id = ?", (project_id,))


def save_elements(project_id, elements):
    """도면 요소 일괄 저장"""
    execute_query("DELETE FROM drawing_elements WHERE project_id = ?", (project_id,))
    execute_query("DELETE FROM element_connections WHERE project_id = ?", (project_id,))
    id_map = {}
    for elem in elements:
        new_id = execute_query(
            """INSERT INTO drawing_elements
               (project_id, element_type, label, x, y, status, properties_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, elem.element_type, elem.label,
             elem.x, elem.y, elem.status, elem.properties_json)
        )
        id_map[elem.id] = new_id
    return id_map


def save_connections(project_id, connections, id_map):
    for from_id, to_id, conn_type in connections:
        new_from = id_map.get(from_id, from_id)
        new_to = id_map.get(to_id, to_id)
        execute_query(
            """INSERT INTO element_connections
               (project_id, from_element_id, to_element_id, connection_type)
               VALUES (?, ?, ?, ?)""",
            (project_id, new_from, new_to, conn_type)
        )


def load_elements(project_id):
    return fetch_all(
        "SELECT * FROM drawing_elements WHERE project_id = ?",
        (project_id,)
    )


def load_connections(project_id):
    return fetch_all(
        "SELECT * FROM element_connections WHERE project_id = ?",
        (project_id,)
    )
