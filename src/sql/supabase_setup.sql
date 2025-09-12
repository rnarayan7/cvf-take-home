-- CVF Portfolio Management Database Schema
-- Run this script in your Supabase SQL editor

-- Enable Row Level Security on all tables
-- Create tables

CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cohorts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    cohort_month DATE NOT NULL,
    planned_sm NUMERIC NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, cohort_month)
);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    customer_id VARCHAR NOT NULL,
    payment_date DATE NOT NULL,
    cohort_month DATE NOT NULL,
    amount NUMERIC NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    cohort_start_at DATE NOT NULL,
    sharing_percentage NUMERIC NOT NULL CHECK (sharing_percentage >= 0 AND sharing_percentage <= 1),
    cash_cap NUMERIC NOT NULL CHECK (cash_cap >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS thresholds (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    payment_period_month INTEGER NOT NULL CHECK (payment_period_month >= 0),
    minimum_payment_percent NUMERIC NOT NULL CHECK (minimum_payment_percent >= 0 AND minimum_payment_percent <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cashflow_snapshots (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    cohort_month DATE NOT NULL,
    as_of_month DATE NOT NULL,
    planned_sm NUMERIC NOT NULL,
    actual_sm NUMERIC,
    cumulative_payments NUMERIC NOT NULL DEFAULT 0,
    share_rate NUMERIC NOT NULL,
    owed_this_month NUMERIC NOT NULL DEFAULT 0,
    cumulative_shared NUMERIC NOT NULL DEFAULT 0,
    at_cap BOOLEAN DEFAULT FALSE,
    flip_100_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recalc_jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    trigger VARCHAR NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finished_at TIMESTAMP WITH TIME ZONE,
    log TEXT,
    error_message TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_cohorts_company_month ON cohorts(company_id, cohort_month);
CREATE INDEX IF NOT EXISTS idx_payments_company ON payments(company_id);
CREATE INDEX IF NOT EXISTS idx_payments_cohort ON payments(cohort_month);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_trades_company ON trades(company_id);
CREATE INDEX IF NOT EXISTS idx_thresholds_company ON thresholds(company_id);
CREATE INDEX IF NOT EXISTS idx_cashflow_company_date ON cashflow_snapshots(company_id, as_of_month);
CREATE INDEX IF NOT EXISTS idx_jobs_company_status ON recalc_jobs(company_id, status);

-- Enable Row Level Security
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE thresholds ENABLE ROW LEVEL SECURITY;
ALTER TABLE cashflow_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE recalc_jobs ENABLE ROW LEVEL SECURITY;

-- Create user profiles table for authentication
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email VARCHAR,
    company_id INTEGER REFERENCES companies(id),
    role VARCHAR NOT NULL CHECK (role IN ('company', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Companies: Admin can see all, company users can only see their own
CREATE POLICY "Admin can view all companies" ON companies
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

CREATE POLICY "Company users can view their company" ON companies
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.company_id = companies.id
        )
    );

CREATE POLICY "Admin can manage companies" ON companies
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

-- Cohorts: Users can only access their company's data
CREATE POLICY "Users can view own company cohorts" ON cohorts
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = cohorts.company_id)
        )
    );

CREATE POLICY "Users can manage own company cohorts" ON cohorts
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = cohorts.company_id)
        )
    );

-- Payments: Users can only access their company's data
CREATE POLICY "Users can view own company payments" ON payments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = payments.company_id)
        )
    );

CREATE POLICY "Users can manage own company payments" ON payments
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = payments.company_id)
        )
    );

-- Trades: Admin can see all, company users can only see their own
CREATE POLICY "Users can view own company trades" ON trades
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = trades.company_id)
        )
    );

CREATE POLICY "Admin can manage trades" ON trades
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

-- Thresholds: Admin can manage, company users can view
CREATE POLICY "Users can view company thresholds" ON thresholds
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = thresholds.company_id)
        )
    );

CREATE POLICY "Admin can manage thresholds" ON thresholds
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

-- Cashflow snapshots: Read-only for company users, full access for admin
CREATE POLICY "Users can view own company cashflows" ON cashflow_snapshots
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = cashflow_snapshots.company_id)
        )
    );

CREATE POLICY "Admin can manage cashflows" ON cashflow_snapshots
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'admin'
        )
    );

-- Jobs: Users can view their company's jobs
CREATE POLICY "Users can view own company jobs" ON recalc_jobs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND (profiles.role = 'admin' OR profiles.company_id = recalc_jobs.company_id)
        )
    );

CREATE POLICY "System can manage jobs" ON recalc_jobs
    FOR ALL USING (true); -- Allow service role to manage jobs

-- Profiles: Users can view their own profile, admin can see all
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (profiles.id = auth.uid());

CREATE POLICY "Admin can view all profiles" ON profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles p 
            WHERE p.id = auth.uid() 
            AND p.role = 'admin'
        )
    );

CREATE POLICY "Admin can manage profiles" ON profiles
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles p 
            WHERE p.id = auth.uid() 
            AND p.role = 'admin'
        )
    );

-- Function to create a new profile after user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, role)
    VALUES (NEW.id, NEW.email, 'company'); -- Default to company role
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();