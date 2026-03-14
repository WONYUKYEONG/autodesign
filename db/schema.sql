-- 통신선로 설계 프로그램 DB 스키마

-- 1. 자재 마스터
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    spec TEXT DEFAULT '',
    unit TEXT NOT NULL,
    unit_price INTEGER NOT NULL DEFAULT 0,
    category TEXT DEFAULT ''
);

-- 2. 공종 마스터
CREATE TABLE IF NOT EXISTS work_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    category TEXT DEFAULT ''
);

-- 3. 일위대가
CREATE TABLE IF NOT EXISTS unit_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_type_code TEXT NOT NULL,
    labor_cost INTEGER NOT NULL DEFAULT 0,
    material_cost INTEGER NOT NULL DEFAULT 0,
    expense_cost INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (work_type_code) REFERENCES work_types(code)
);

-- 4. 일위대가 세부 구성
CREATE TABLE IF NOT EXISTS unit_price_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_price_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    spec TEXT DEFAULT '',
    unit TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    unit_cost INTEGER NOT NULL DEFAULT 0,
    cost_type TEXT NOT NULL CHECK(cost_type IN ('labor', 'material', 'expense')),
    FOREIGN KEY (unit_price_id) REFERENCES unit_prices(id)
);

-- 5. 시나리오 규칙
CREATE TABLE IF NOT EXISTS scenario_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_event TEXT NOT NULL,
    condition_json TEXT,
    action_type TEXT NOT NULL CHECK(action_type IN ('ADD_WORK', 'ADD_MATERIAL', 'FIRE_EVENT')),
    target_code TEXT NOT NULL,
    quantity_expr TEXT NOT NULL DEFAULT '1',
    priority INTEGER NOT NULL DEFAULT 0,
    description TEXT DEFAULT ''
);

-- 6. 프로젝트
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 도면 요소
CREATE TABLE IF NOT EXISTS drawing_elements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    element_type TEXT NOT NULL,
    label TEXT DEFAULT '',
    x REAL NOT NULL DEFAULT 0,
    y REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'existing',
    properties_json TEXT DEFAULT '{}',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 8. 요소 연결 관계
CREATE TABLE IF NOT EXISTS element_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    from_element_id INTEGER NOT NULL,
    to_element_id INTEGER NOT NULL,
    connection_type TEXT DEFAULT 'cable',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (from_element_id) REFERENCES drawing_elements(id) ON DELETE CASCADE,
    FOREIGN KEY (to_element_id) REFERENCES drawing_elements(id) ON DELETE CASCADE
);

-- 9. 작업 지시서
CREATE TABLE IF NOT EXISTS work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_cost INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 10. 작업 지시서 상세
CREATE TABLE IF NOT EXISTS work_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    item_type TEXT NOT NULL CHECK(item_type IN ('work', 'material')),
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    spec TEXT DEFAULT '',
    unit TEXT NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    unit_cost INTEGER NOT NULL DEFAULT 0,
    labor_cost INTEGER NOT NULL DEFAULT 0,
    material_cost INTEGER NOT NULL DEFAULT 0,
    expense_cost INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE
);
