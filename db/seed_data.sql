-- 초기 데이터: 자재

INSERT OR IGNORE INTO materials (code, name, spec, unit, unit_price, category) VALUES
('MAT001', '디딤쇠', '전주용 표준', '개', 15000, '전주자재'),
('MAT002', '고무링', '단자함용 방수', '개', 3000, '단자자재'),
('MAT003', '왕관밴드', '인입선 고정용', '개', 5000, '인입자재'),
('MAT004', '전주', '8m 콘크리트주', '본', 350000, '전주자재'),
('MAT005', '케이블', 'UTP CAT5e 50P', 'm', 2500, '케이블자재'),
('MAT006', '단자함', '10회선 옥외형', '개', 85000, '단자자재'),
('MAT007', '인입선', '2C 드롭와이어', 'm', 1200, '인입자재'),
('MAT008', '행거밴드', '전주 부착용', '개', 8000, '전주자재'),
('MAT009', '케이블행거', '케이블 지지용', '개', 6000, '케이블자재'),
('MAT010', '접지봉', '접지용 동봉', '개', 25000, '전주자재');

-- 초기 데이터: 공종

INSERT OR IGNORE INTO work_types (code, name, unit, category) VALUES
('WRK001', '전주철거', '본', '전주공사'),
('WRK002', '전주신설', '본', '전주공사'),
('WRK003', '케이블이설', '조', '케이블공사'),
('WRK004', '케이블신설', 'm', '케이블공사'),
('WRK005', '단자취부', '개', '단자공사'),
('WRK006', '인입선설치', '회선', '인입공사'),
('WRK007', '인입선철거', '회선', '인입공사'),
('WRK008', '케이블철거', '조', '케이블공사'),
('WRK009', '단자철거', '개', '단자공사'),
('WRK010', '접지공사', '개소', '접지공사');

-- 초기 데이터: 일위대가

INSERT OR IGNORE INTO unit_prices (work_type_code, labor_cost, material_cost, expense_cost) VALUES
('WRK001', 185000, 0, 25000),
('WRK002', 245000, 350000, 35000),
('WRK003', 120000, 15000, 18000),
('WRK004', 3500, 2500, 500),
('WRK005', 65000, 85000, 8000),
('WRK006', 45000, 25000, 5000),
('WRK007', 35000, 0, 5000),
('WRK008', 95000, 0, 15000),
('WRK009', 45000, 0, 6000),
('WRK010', 85000, 45000, 12000);

-- 초기 데이터: 일위대가 세부 (전주신설 예시)

INSERT OR IGNORE INTO unit_price_details (unit_price_id, item_name, spec, unit, quantity, unit_cost, cost_type) VALUES
(2, '통신외선공(케이블)', '', '인', 0.8, 220000, 'labor'),
(2, '보통인부', '', '인', 1.2, 140000, 'labor'),
(2, '콘크리트주', '8m', '본', 1, 350000, 'material'),
(2, '장비사용료', '크레인', '시간', 1, 35000, 'expense');

-- 초기 데이터: 시나리오 규칙

-- 전주 파손/철거 시
INSERT OR IGNORE INTO scenario_rules (trigger_event, condition_json, action_type, target_code, quantity_expr, priority, description) VALUES
('POLE_DEMOLISH', NULL, 'ADD_WORK', 'WRK001', '1', 10, '전주 철거 작업 추가'),
('POLE_DEMOLISH', '{"has_cable": true}', 'ADD_WORK', 'WRK003', 'cable_count', 20, '연결된 케이블 이설'),
('POLE_DEMOLISH', '{"has_terminal": true}', 'ADD_WORK', 'WRK009', 'terminal_count', 20, '기존 단자 철거'),
('POLE_DEMOLISH', '{"has_dropwire": true}', 'ADD_WORK', 'WRK007', 'dropwire_count', 20, '기존 인입선 철거'),
('POLE_DEMOLISH', NULL, 'FIRE_EVENT', 'POLE_INSTALL', '1', 30, '신규 전주 설치 이벤트 연쇄');

-- 전주 신설 시
INSERT OR IGNORE INTO scenario_rules (trigger_event, condition_json, action_type, target_code, quantity_expr, priority, description) VALUES
('POLE_INSTALL', NULL, 'ADD_WORK', 'WRK002', '1', 10, '전주 신설 작업 추가'),
('POLE_INSTALL', NULL, 'ADD_MATERIAL', 'MAT001', '6', 11, '디딤쇠 6개'),
('POLE_INSTALL', NULL, 'ADD_MATERIAL', 'MAT010', '1', 12, '접지봉 1개'),
('POLE_INSTALL', NULL, 'ADD_WORK', 'WRK010', '1', 13, '접지공사'),
('POLE_INSTALL', '{"has_terminal": true}', 'FIRE_EVENT', 'TERMINAL_ATTACH', '1', 20, '단자 취부 이벤트 연쇄'),
('POLE_INSTALL', '{"has_dropwire": true}', 'FIRE_EVENT', 'DROPWIRE_INSTALL', 'dropwire_count', 20, '인입선 설치 이벤트 연쇄');

-- 단자 취부 시
INSERT OR IGNORE INTO scenario_rules (trigger_event, condition_json, action_type, target_code, quantity_expr, priority, description) VALUES
('TERMINAL_ATTACH', NULL, 'ADD_WORK', 'WRK005', '1', 10, '단자 취부 작업 추가'),
('TERMINAL_ATTACH', NULL, 'ADD_MATERIAL', 'MAT002', '4', 11, '고무링 4개');

-- 인입선 설치 시
INSERT OR IGNORE INTO scenario_rules (trigger_event, condition_json, action_type, target_code, quantity_expr, priority, description) VALUES
('DROPWIRE_INSTALL', NULL, 'ADD_WORK', 'WRK006', '1', 10, '인입선 설치 작업 추가'),
('DROPWIRE_INSTALL', NULL, 'ADD_MATERIAL', 'MAT003', '1', 11, '왕관밴드 1개');

-- 케이블 신설 시
INSERT OR IGNORE INTO scenario_rules (trigger_event, condition_json, action_type, target_code, quantity_expr, priority, description) VALUES
('CABLE_INSTALL', NULL, 'ADD_WORK', 'WRK004', 'cable_length', 10, '케이블 포설 작업'),
('CABLE_INSTALL', NULL, 'ADD_MATERIAL', 'MAT009', 'hanger_count', 11, '케이블행거');
