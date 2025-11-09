CREATE TABLE public.ai_contexts (
  profile_id uuid NOT NULL,
  executive_summary text,
  trend_analysis text,
  comparative_context text,
  commitment_strength_rating integer CHECK (commitment_strength_rating >= 1 AND commitment_strength_rating <= 10),
  transparency_rating integer CHECK (transparency_rating >= 1 AND transparency_rating <= 10),
  recommendation USER-DEFINED,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT ai_contexts_pkey PRIMARY KEY (profile_id),
  CONSTRAINT ai_contexts_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.ai_key_insights (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL,
  insight_text text NOT NULL,
  insight_order integer NOT NULL CHECK (insight_order > 0),
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT ai_key_insights_pkey PRIMARY KEY (id),
  CONSTRAINT ai_key_insights_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.ai_strategic_implications (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL,
  implication_text text NOT NULL,
  implication_order integer NOT NULL CHECK (implication_order > 0),
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT ai_strategic_implications_pkey PRIMARY KEY (id),
  CONSTRAINT ai_strategic_implications_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.api_keys (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  name character varying NOT NULL,
  key_hash character varying NOT NULL UNIQUE,
  key_prefix character varying NOT NULL,
  is_active boolean NOT NULL DEFAULT true,
  is_admin boolean NOT NULL DEFAULT false,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by uuid,
  last_used_at timestamp with time zone,
  expires_at timestamp with time zone,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  CONSTRAINT api_keys_pkey PRIMARY KEY (id)
);
CREATE TABLE public.cdo_role_sources (
  profile_id uuid NOT NULL,
  source_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT cdo_role_sources_pkey PRIMARY KEY (profile_id, source_id),
  CONSTRAINT cdo_role_sources_profile_fkey FOREIGN KEY (profile_id) REFERENCES public.cdo_roles(profile_id),
  CONSTRAINT cdo_role_sources_source_fkey FOREIGN KEY (source_id) REFERENCES public.data_sources(id)
);
CREATE TABLE public.cdo_roles (
  profile_id uuid NOT NULL,
  exists boolean NOT NULL DEFAULT false,
  name text,
  title text,
  reports_to text,
  appointment_date date,
  c_suite_member boolean NOT NULL DEFAULT false,
  quotes jsonb,
  provenance_ids ARRAY,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT cdo_roles_pkey PRIMARY KEY (profile_id),
  CONSTRAINT cdo_roles_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.commitment_sources (
  commitment_id uuid NOT NULL,
  source_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT commitment_sources_pkey PRIMARY KEY (commitment_id, source_id),
  CONSTRAINT commitment_sources_commitment_fkey FOREIGN KEY (commitment_id) REFERENCES public.commitments(id),
  CONSTRAINT commitment_sources_source_fkey FOREIGN KEY (source_id) REFERENCES public.data_sources(id)
);
CREATE TABLE public.commitments (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL,
  commitment_name text NOT NULL,
  commitment_type USER-DEFINED NOT NULL,
  current_status USER-DEFINED NOT NULL,
  quotes jsonb,
  provenance_ids ARRAY,
  status_changed_at timestamp with time zone,
  previous_status USER-DEFINED,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT commitments_pkey PRIMARY KEY (id),
  CONSTRAINT commitments_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.companies (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  ticker character varying NOT NULL UNIQUE CHECK (ticker::text = upper(ticker::text)),
  name text NOT NULL,
  cik character varying,
  industry USER-DEFINED,
  hq_city text,
  hq_state USER-DEFINED,
  hq_country USER-DEFINED DEFAULT 'USA'::country_code,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT companies_pkey PRIMARY KEY (id)
);
CREATE TABLE public.controversies (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL,
  date date,
  type USER-DEFINED NOT NULL,
  status USER-DEFINED NOT NULL,
  description text NOT NULL,
  case_name text,
  docket_number text,
  court text,
  nlrb_case_id text,
  filing_url text,
  quotes jsonb,
  provenance_ids ARRAY,
  status_standard USER-DEFINED,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT controversies_pkey PRIMARY KEY (id),
  CONSTRAINT controversies_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.controversy_sources (
  controversy_id uuid NOT NULL,
  source_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT controversy_sources_pkey PRIMARY KEY (controversy_id, source_id),
  CONSTRAINT controversy_sources_controversy_fkey FOREIGN KEY (controversy_id) REFERENCES public.controversies(id),
  CONSTRAINT controversy_sources_source_fkey FOREIGN KEY (source_id) REFERENCES public.data_sources(id)
);
CREATE TABLE public.data_quality_flags (
  profile_id uuid NOT NULL,
  incomplete_data boolean NOT NULL DEFAULT false,
  conflicting_sources boolean NOT NULL DEFAULT false,
  outdated_information boolean NOT NULL DEFAULT false,
  verification_needed ARRAY,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT data_quality_flags_pkey PRIMARY KEY (profile_id),
  CONSTRAINT data_quality_flags_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.data_sources (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL,
  source_id text NOT NULL,
  source_type USER-DEFINED NOT NULL,
  publisher text,
  author text,
  url text,
  date date,
  title text,
  reliability_score integer CHECK (reliability_score >= 1 AND reliability_score <= 5),
  doc_type text,
  notes text,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT data_sources_pkey PRIMARY KEY (id),
  CONSTRAINT data_sources_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.dei_posture_sources (
  profile_id uuid NOT NULL,
  source_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT dei_posture_sources_pkey PRIMARY KEY (profile_id, source_id),
  CONSTRAINT dei_posture_sources_profile_fkey FOREIGN KEY (profile_id) REFERENCES public.dei_postures(profile_id),
  CONSTRAINT dei_posture_sources_source_fkey FOREIGN KEY (source_id) REFERENCES public.data_sources(id)
);
CREATE TABLE public.dei_postures (
  profile_id uuid NOT NULL,
  status USER-DEFINED NOT NULL,
  evidence_summary text,
  last_verified_date date,
  quotes jsonb,
  provenance_ids ARRAY,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT dei_postures_pkey PRIMARY KEY (profile_id),
  CONSTRAINT dei_postures_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.event_sources (
  event_id uuid NOT NULL,
  source_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT event_sources_pkey PRIMARY KEY (event_id, source_id),
  CONSTRAINT event_sources_source_fkey FOREIGN KEY (source_id) REFERENCES public.data_sources(id),
  CONSTRAINT event_sources_event_fkey FOREIGN KEY (event_id) REFERENCES public.events(id)
);
CREATE TABLE public.events (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL,
  date date,
  headline text,
  event_type USER-DEFINED NOT NULL,
  sentiment USER-DEFINED,
  impact USER-DEFINED,
  summary text,
  quotes jsonb,
  provenance_ids ARRAY,
  impact_magnitude USER-DEFINED,
  impact_direction USER-DEFINED,
  event_category USER-DEFINED,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT events_pkey PRIMARY KEY (id),
  CONSTRAINT events_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.profiles (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  company_id uuid NOT NULL,
  schema_version character varying NOT NULL DEFAULT '1.0'::character varying,
  profile_type character varying NOT NULL DEFAULT 'dei_profile'::character varying,
  generated_at timestamp with time zone NOT NULL,
  research_captured_at timestamp with time zone,
  research_notes text,
  source_count integer NOT NULL DEFAULT 0 CHECK (source_count >= 0),
  is_latest boolean NOT NULL DEFAULT true,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT profiles_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id)
);
CREATE TABLE public.reporting_practice_sources (
  profile_id uuid NOT NULL,
  source_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT reporting_practice_sources_pkey PRIMARY KEY (profile_id, source_id),
  CONSTRAINT reporting_practice_sources_profile_fkey FOREIGN KEY (profile_id) REFERENCES public.reporting_practices(profile_id),
  CONSTRAINT reporting_practice_sources_source_fkey FOREIGN KEY (source_id) REFERENCES public.data_sources(id)
);
CREATE TABLE public.reporting_practices (
  profile_id uuid NOT NULL,
  standalone_dei_report boolean NOT NULL DEFAULT false,
  dei_in_esg_report boolean NOT NULL DEFAULT false,
  dei_in_annual_report boolean NOT NULL DEFAULT false,
  reporting_frequency USER-DEFINED,
  last_report_date date,
  report_url text,
  quotes jsonb,
  provenance_ids ARRAY,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT reporting_practices_pkey PRIMARY KEY (profile_id),
  CONSTRAINT reporting_practices_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.risk_assessments (
  profile_id uuid NOT NULL,
  overall_risk_score integer CHECK (overall_risk_score >= 0 AND overall_risk_score <= 100),
  risk_level USER-DEFINED NOT NULL,
  ongoing_lawsuits integer NOT NULL DEFAULT 0,
  settled_cases integer NOT NULL DEFAULT 0,
  negative_events integer NOT NULL DEFAULT 0,
  high_impact_events integer NOT NULL DEFAULT 0,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT risk_assessments_pkey PRIMARY KEY (profile_id),
  CONSTRAINT risk_assessments_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.supplier_diversity (
  profile_id uuid NOT NULL,
  program_exists boolean NOT NULL DEFAULT false,
  program_status USER-DEFINED,
  spending_disclosed boolean NOT NULL DEFAULT false,
  quotes jsonb,
  provenance_ids ARRAY,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT supplier_diversity_pkey PRIMARY KEY (profile_id),
  CONSTRAINT supplier_diversity_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(id)
);
CREATE TABLE public.supplier_diversity_sources (
  profile_id uuid NOT NULL,
  source_id uuid NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT supplier_diversity_sources_pkey PRIMARY KEY (profile_id, source_id),
  CONSTRAINT supplier_diversity_sources_profile_fkey FOREIGN KEY (profile_id) REFERENCES public.supplier_diversity(profile_id),
  CONSTRAINT supplier_diversity_sources_source_fkey FOREIGN KEY (source_id) REFERENCES public.data_sources(id)
);