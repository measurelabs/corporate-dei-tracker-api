-- Add AI analysis content fields to profiles table

ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS dei_posture TEXT,
ADD COLUMN IF NOT EXISTS dei_posture_summary TEXT,
ADD COLUMN IF NOT EXISTS key_findings JSONB,
ADD COLUMN IF NOT EXISTS leadership_analysis TEXT,
ADD COLUMN IF NOT EXISTS reporting_transparency TEXT,
ADD COLUMN IF NOT EXISTS controversies_summary TEXT,
ADD COLUMN IF NOT EXISTS overall_assessment TEXT,
ADD COLUMN IF NOT EXISTS stance_direction TEXT CHECK (stance_direction IN ('supportive', 'neutral', 'reducing', 'unclear')),
ADD COLUMN IF NOT EXISTS stance_trend TEXT CHECK (stance_trend IN ('increasing', 'stable', 'decreasing', 'mixed'));

-- Add comments
COMMENT ON COLUMN profiles.dei_posture IS 'Full narrative assessment of company DEI stance';
COMMENT ON COLUMN profiles.dei_posture_summary IS 'Executive summary (2-3 sentences)';
COMMENT ON COLUMN profiles.key_findings IS 'JSON array of key findings/bullet points';
COMMENT ON COLUMN profiles.leadership_analysis IS 'Analysis of DEI leadership and governance';
COMMENT ON COLUMN profiles.reporting_transparency IS 'Assessment of DEI reporting and transparency';
COMMENT ON COLUMN profiles.controversies_summary IS 'Summary of DEI-related controversies';
COMMENT ON COLUMN profiles.overall_assessment IS 'Overall qualitative assessment';
COMMENT ON COLUMN profiles.stance_direction IS 'Current DEI stance: supportive, neutral, reducing, unclear';
COMMENT ON COLUMN profiles.stance_trend IS 'Trend over time: increasing, stable, decreasing, mixed';
