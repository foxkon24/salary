-- データベース作成
CREATE DATABASE IF NOT EXISTS salary;
USE salary;

-- 既存のテーブルを削除
DROP TABLE IF EXISTS income;
DROP TABLE IF EXISTS years;

-- 年度テーブル
CREATE TABLE IF NOT EXISTS years (
    year_id INT PRIMARY KEY,
    display_name VARCHAR(20) NOT NULL
);

-- 給与テーブル
CREATE TABLE IF NOT EXISTS income (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year_id INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    monthly_total INT DEFAULT 0,
    monthly_deduction INT DEFAULT 0, 
    year_end_adjustment INT DEFAULT 0,
    monthly_income INT DEFAULT 0,
    bonus_total INT DEFAULT 0,
    bonus_deduction INT DEFAULT 0,
    bonus_income INT DEFAULT 0,
    total INT DEFAULT 0,
    cumulative_total INT DEFAULT 0,
    FOREIGN KEY (year_id) REFERENCES years(year_id),
    CONSTRAINT unique_year_month UNIQUE (year_id, month)
);

-- 初期データ挿入
INSERT INTO years (year_id, display_name) VALUES 
(2022, '2022年度'),
(2023, '2023年度'),
(2024, '2024年度');

-- 2022年度のデータ作成（5月～翌年4月）
INSERT INTO income (year_id, year, month) VALUES
(2022, 2022, 5), (2022, 2022, 6), (2022, 2022, 7), (2022, 2022, 8), (2022, 2022, 9), (2022, 2022, 10),
(2022, 2022, 11), (2022, 2022, 12), (2022, 2023, 1), (2022, 2023, 2), (2022, 2023, 3), (2022, 2023, 4);

-- 2023年度のデータ作成
INSERT INTO income (year_id, year, month) VALUES
(2023, 2023, 5), (2023, 2023, 6), (2023, 2023, 7), (2023, 2023, 8), (2023, 2023, 9), (2023, 2023, 10),
(2023, 2023, 11), (2023, 2023, 12), (2023, 2024, 1), (2023, 2024, 2), (2023, 2024, 3), (2023, 2024, 4);

-- 2024年度のデータ作成
INSERT INTO income (year_id, year, month) VALUES
(2024, 2024, 5), (2024, 2024, 6), (2024, 2024, 7), (2024, 2024, 8), (2024, 2024, 9), (2024, 2024, 10),
(2024, 2024, 11), (2024, 2024, 12), (2024, 2025, 1), (2024, 2025, 2), (2024, 2025, 3), (2024, 2025, 4); 