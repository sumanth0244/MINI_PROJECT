CREATE DATABASE IF NOT EXISTS mindcare_db CHARACTER SET utf8mb4;
USE mindcare_db;
CREATE TABLE IF NOT EXISTS patients(
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_code VARCHAR(30) UNIQUE NOT NULL,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(120) NULL,
  age INT NULL,
  caregiver_name VARCHAR(120) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS games(
  id INT AUTO_INCREMENT PRIMARY KEY,
  game_key VARCHAR(40) UNIQUE NOT NULL,
  game_name VARCHAR(100) NOT NULL
);
INSERT IGNORE INTO games(game_key,game_name) VALUES
  ('sequence','Sequence Memory'),
  ('missing_object','Missing Object'),
  ('association','Picture Association'),
  ('recognition','Picture Recognition');
CREATE TABLE IF NOT EXISTS patient_game_levels(
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  game_id INT NOT NULL,
  current_level ENUM('Easy','Medium','Hard') DEFAULT 'Easy',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_pg(patient_id,game_id),
  FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS game_sessions(
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  game_id INT NOT NULL,
  difficulty ENUM('Easy','Medium','Hard') NOT NULL,
  total_questions INT NOT NULL,
  correct_answers INT NOT NULL,
  accuracy DECIMAL(5,2) NOT NULL,
  reaction_time DECIMAL(8,2) DEFAULT 0,
  attempts INT DEFAULT 0,
  hints_used INT DEFAULT 0,
  completed BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_pg_date(patient_id,game_id,created_at),
  FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS agent_decisions(
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  game_id INT NOT NULL,
  session_id BIGINT NULL,
  previous_level ENUM('Easy','Medium','Hard') NOT NULL,
  recommended_level ENUM('Easy','Medium','Hard') NOT NULL,
  decision VARCHAR(30),
  reason VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE,
  FOREIGN KEY(session_id) REFERENCES game_sessions(id) ON DELETE SET NULL
);
