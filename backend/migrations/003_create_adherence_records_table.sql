-- Create adherence_records table
CREATE TABLE IF NOT EXISTS adherence_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medication_id UUID NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP NOT NULL,
    taken_time TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('taken', 'missed', 'skipped')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_adherence_medication_id ON adherence_records(medication_id);
CREATE INDEX idx_adherence_scheduled_time ON adherence_records(scheduled_time);
CREATE INDEX idx_adherence_status ON adherence_records(status);
CREATE INDEX idx_adherence_taken_time ON adherence_records(taken_time);
