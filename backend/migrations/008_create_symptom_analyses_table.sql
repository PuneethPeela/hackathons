-- Create symptom_analyses table
CREATE TABLE IF NOT EXISTS symptom_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symptoms JSONB NOT NULL,
    predictions JSONB NOT NULL,
    risk_severity VARCHAR(20) NOT NULL CHECK (risk_severity IN ('low', 'medium', 'high', 'critical')),
    recommended_action TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_symptom_analyses_user_id ON symptom_analyses(user_id);
CREATE INDEX idx_symptom_analyses_risk ON symptom_analyses(risk_severity);
CREATE INDEX idx_symptom_analyses_created_at ON symptom_analyses(created_at);
