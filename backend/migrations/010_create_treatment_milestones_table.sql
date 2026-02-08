-- Create treatment_milestones table for tracking treatment progress
CREATE TABLE IF NOT EXISTS treatment_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    target_date DATE,
    completed BOOLEAN DEFAULT FALSE,
    completed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_treatment_milestones_user_id ON treatment_milestones(user_id);
CREATE INDEX idx_treatment_milestones_completed ON treatment_milestones(completed);
CREATE INDEX idx_treatment_milestones_target_date ON treatment_milestones(target_date);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER update_treatment_milestones_updated_at BEFORE UPDATE ON treatment_milestones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
