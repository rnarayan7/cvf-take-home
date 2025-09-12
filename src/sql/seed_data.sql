-- Sample data for CVF Portfolio Management
-- Run this after the main schema setup

-- Insert sample companies
INSERT INTO companies (name) VALUES 
    ('Acme Corp'),
    ('TechStart Inc'),
    ('GrowthCo')
ON CONFLICT (name) DO NOTHING;

-- Get company IDs for reference
DO $$
DECLARE
    acme_id INTEGER;
    techstart_id INTEGER;
    growthco_id INTEGER;
BEGIN
    SELECT id INTO acme_id FROM companies WHERE name = 'Acme Corp';
    SELECT id INTO techstart_id FROM companies WHERE name = 'TechStart Inc';
    SELECT id INTO growthco_id FROM companies WHERE name = 'GrowthCo';

    -- Insert cohorts (S&M spend plans)
    INSERT INTO cohorts (company_id, cohort_month, planned_sm) VALUES
        -- Acme Corp cohorts
        (acme_id, '2024-01-01', 100000),
        (acme_id, '2024-02-01', 120000),
        (acme_id, '2024-03-01', 90000),
        (acme_id, '2024-04-01', 110000),
        
        -- TechStart Inc cohorts  
        (techstart_id, '2024-01-01', 50000),
        (techstart_id, '2024-02-01', 60000),
        (techstart_id, '2024-03-01', 75000),
        
        -- GrowthCo cohorts
        (growthco_id, '2024-02-01', 200000),
        (growthco_id, '2024-03-01', 180000)
    ON CONFLICT (company_id, cohort_month) DO NOTHING;

    -- Insert sample payments
    INSERT INTO payments (company_id, customer_id, payment_date, cohort_month, amount) VALUES
        -- Acme Corp payments
        (acme_id, 'cust_001', '2024-01-15', '2024-01-01', 5000),
        (acme_id, 'cust_001', '2024-02-15', '2024-01-01', 4500),
        (acme_id, 'cust_001', '2024-03-15', '2024-01-01', 4000),
        (acme_id, 'cust_002', '2024-01-20', '2024-01-01', 8000),
        (acme_id, 'cust_002', '2024-02-20', '2024-01-01', 7500),
        (acme_id, 'cust_003', '2024-02-10', '2024-02-01', 12000),
        (acme_id, 'cust_003', '2024-03-10', '2024-02-01', 11000),
        (acme_id, 'cust_004', '2024-02-25', '2024-02-01', 6000),
        (acme_id, 'cust_005', '2024-03-05', '2024-03-01', 15000),
        (acme_id, 'cust_006', '2024-04-05', '2024-04-01', 9000),
        
        -- TechStart Inc payments
        (techstart_id, 'tech_001', '2024-01-10', '2024-01-01', 3000),
        (techstart_id, 'tech_001', '2024-02-10', '2024-01-01', 2800),
        (techstart_id, 'tech_002', '2024-02-05', '2024-02-01', 5000),
        (techstart_id, 'tech_002', '2024-03-05', '2024-02-01', 4800),
        (techstart_id, 'tech_003', '2024-03-15', '2024-03-01', 7500),
        
        -- GrowthCo payments
        (growthco_id, 'growth_001', '2024-02-12', '2024-02-01', 25000),
        (growthco_id, 'growth_001', '2024-03-12', '2024-02-01', 22000),
        (growthco_id, 'growth_002', '2024-03-08', '2024-03-01', 18000);

    -- Insert sample trades
    INSERT INTO trades (company_id, cohort_start_at, sharing_percentage, cash_cap) VALUES
        -- Acme Corp trades
        (acme_id, '2024-01-01', 0.35, 150000),
        (acme_id, '2024-02-01', 0.40, 180000),
        (acme_id, '2024-03-01', 0.32, 135000),
        
        -- TechStart Inc trades
        (techstart_id, '2024-01-01', 0.45, 75000),
        (techstart_id, '2024-02-01', 0.42, 90000),
        
        -- GrowthCo trades
        (growthco_id, '2024-02-01', 0.30, 300000);

    -- Insert sample thresholds
    INSERT INTO thresholds (company_id, payment_period_month, minimum_payment_percent) VALUES
        -- Acme Corp thresholds
        (acme_id, 0, 0.15),  -- Month 0: need 15% of spend back
        (acme_id, 1, 0.10),  -- Month 1: need 10% of spend back
        (acme_id, 3, 0.25),  -- Month 3: need 25% cumulative
        
        -- TechStart Inc thresholds
        (techstart_id, 0, 0.20),
        (techstart_id, 2, 0.30),
        
        -- GrowthCo thresholds  
        (growthco_id, 1, 0.12),
        (growthco_id, 4, 0.35);

END $$;