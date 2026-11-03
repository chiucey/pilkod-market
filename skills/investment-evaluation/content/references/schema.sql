-- Investment Evaluation System Database Schema
-- Complete schema for all evaluation-related tables

-- Users table (core authentication)
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  openId VARCHAR(64) NOT NULL UNIQUE,
  name TEXT,
  email VARCHAR(320),
  loginMethod VARCHAR(64),
  role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  lastSignedIn TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Evaluations table (main investment records)
CREATE TABLE evaluations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL,
  projectName VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Composite scores
  kanoScore DECIMAL(3, 2),
  industryScore DECIMAL(3, 2),
  lifecycleScore DECIMAL(3, 2),
  financialScore DECIMAL(3, 2),
  compositeScore DECIMAL(3, 2),
  
  -- Decision recommendation
  recommendation VARCHAR(50),
  
  -- Business brief
  businessBrief LONGTEXT,
  
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_userId (userId),
  INDEX idx_compositeScore (compositeScore)
);

-- KANO Model Assessment (40% weight)
CREATE TABLE kano_assessments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  evaluationId INT NOT NULL UNIQUE,
  
  -- Three dimensions
  differentiationAnalysis TEXT,
  differentiationScore DECIMAL(3, 2),
  
  demandAnalysis TEXT,
  demandScore DECIMAL(3, 2),
  
  retentionAnalysis TEXT,
  retentionScore DECIMAL(3, 2),
  
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (evaluationId) REFERENCES evaluations(id) ON DELETE CASCADE,
  INDEX idx_evaluationId (evaluationId)
);

-- Industry & Competition Analysis (20% weight)
CREATE TABLE industry_assessments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  evaluationId INT NOT NULL UNIQUE,
  
  -- Five dimensions
  concentrationAnalysis TEXT,
  concentrationScore DECIMAL(3, 2),
  
  barrierAnalysis TEXT,
  barrierScore DECIMAL(3, 2),
  
  incrementalAnalysis TEXT,
  incrementalScore DECIMAL(3, 2),
  
  leaderAnalysis TEXT,
  leaderScore DECIMAL(3, 2),
  
  entryAnalysis TEXT,
  entryScore DECIMAL(3, 2),
  
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (evaluationId) REFERENCES evaluations(id) ON DELETE CASCADE,
  INDEX idx_evaluationId (evaluationId)
);

-- Product Lifecycle Evaluation (10% weight)
CREATE TABLE lifecycle_assessments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  evaluationId INT NOT NULL UNIQUE,
  
  -- Three dimensions
  stageAnalysis TEXT,
  stageScore DECIMAL(3, 2),
  
  driversAnalysis TEXT,
  driversScore DECIMAL(3, 2),
  
  scaleAnalysis TEXT,
  scaleScore DECIMAL(3, 2),
  
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (evaluationId) REFERENCES evaluations(id) ON DELETE CASCADE,
  INDEX idx_evaluationId (evaluationId)
);

-- Financial Analysis (30% weight)
CREATE TABLE financial_assessments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  evaluationId INT NOT NULL UNIQUE,
  
  -- Financial metrics
  peRatio DECIMAL(8, 2),
  growthRate DECIMAL(8, 2),
  pegRatio DECIMAL(8, 2),
  
  -- Analysis notes
  analysis TEXT,
  financialScore DECIMAL(3, 2),
  
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (evaluationId) REFERENCES evaluations(id) ON DELETE CASCADE,
  INDEX idx_evaluationId (evaluationId)
);

-- User Memberships (quota management)
CREATE TABLE memberships (
  id INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL UNIQUE,
  membershipType ENUM('free', 'premium') NOT NULL DEFAULT 'free',
  
  -- Premium subscription details
  subscriptionStartDate TIMESTAMP,
  subscriptionEndDate TIMESTAMP,
  
  -- Quota tracking
  monthlyQuota INT NOT NULL DEFAULT 50,
  
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_userId (userId),
  INDEX idx_membershipType (membershipType)
);

-- Usage Logs (track API usage for quota)
CREATE TABLE usage_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  userId INT NOT NULL,
  evaluationId INT,
  
  -- Usage tracking
  usageType VARCHAR(50) NOT NULL,
  usageCount INT NOT NULL DEFAULT 1,
  
  createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (evaluationId) REFERENCES evaluations(id) ON DELETE SET NULL,
  INDEX idx_userId (userId),
  INDEX idx_createdAt (createdAt),
  INDEX idx_userMonth (userId, createdAt)
);

-- Indexes for common queries
CREATE INDEX idx_evaluations_userId_createdAt ON evaluations(userId, createdAt DESC);
CREATE INDEX idx_evaluations_compositeScore ON evaluations(compositeScore DESC);
CREATE INDEX idx_usageLogs_userMonth ON usage_logs(userId, DATE_FORMAT(createdAt, '%Y-%m'));
