-- Needs to be present in the Postgres DB if data needs to be retrieved for Elasticsearch
DROP VIEW IF EXISTS transaction_delta_view;

CREATE VIEW transaction_delta_view AS
SELECT
  UTM.transaction_id,
  FPDS.detached_award_proc_unique,
  FABS.afa_generated_unique,

  CASE
    WHEN FPDS.detached_award_proc_unique IS NOT NULL THEN 'CONT_TX_' || UPPER(FPDS.detached_award_proc_unique)
    WHEN FABS.afa_generated_unique IS NOT NULL THEN 'ASST_TX_' || UPPER(FABS.afa_generated_unique)
    ELSE NULL  -- if this happens: Activate Batsignal
  END AS generated_unique_transaction_id,

  CASE
    WHEN UTM.type IN ('02', '03', '04', '05', '06', '10', '07', '08', '09', '11') AND UTM.fain IS NOT NULL THEN UTM.fain
    WHEN UTM.piid IS NOT NULL THEN UTM.piid  -- contracts. Did it this way to easily handle IDV contracts
    ELSE UTM.uri
  END AS display_award_id,

  AWD.update_date,
  UTM.modification_number,
  AWD.generated_unique_award_id,
  UTM.award_id,
  UTM.piid,
  UTM.fain,
  UTM.uri,
  UTM.transaction_description AS award_description,

  UTM.product_or_service_code,
  UTM.product_or_service_description,
  CASE
    WHEN UTM.product_or_service_code IS NOT NULL THEN CONCAT('{"code":"', UTM.product_or_service_code, '","description":"', UTM.product_or_service_description, '"}')
    ELSE NULL
  END AS psc_agg_key,
  UTM.naics_code,
  UTM.naics_description,
  CASE
    WHEN UTM.naics_code IS NOT NULL
      THEN CONCAT('{"code":"', UTM.naics_code, '","description":"', UTM.naics_description, '"}')
    ELSE NULL
  END AS naics_agg_key,
  AWD.type_description,
  UTM.award_category,

  UTM.recipient_unique_id,
  UTM.recipient_name,
  UTM.recipient_hash,
  CASE
    WHEN RECIPIENT_HASH_AND_LEVEL.recipient_hash IS NULL or RECIPIENT_HASH_AND_LEVEL.recipient_level IS NULL
      THEN CONCAT('{"hash_with_level": "","name":"', UTM.recipient_name, '","unique_id":"', UTM.recipient_unique_id, '"}')
    ELSE
      CONCAT(
        '{"hash_with_level":"', CONCAT(RECIPIENT_HASH_AND_LEVEL.recipient_hash, '-', RECIPIENT_HASH_AND_LEVEL.recipient_level),
        '","name":"', UTM.recipient_name,
        '","unique_id":"', UTM.recipient_unique_id, '"}'
      )
  END AS recipient_agg_key,

  UTM.parent_recipient_unique_id,
  UPPER(PRL.legal_business_name) AS parent_recipient_name,
  PRL.recipient_hash AS parent_recipient_hash,

  UTM.action_date,
  DATE(UTM.action_date + interval '3 months') AS fiscal_action_date,
  AWD.period_of_performance_start_date,
  AWD.period_of_performance_current_end_date,
  FPDS.ordering_period_end_date,
  UTM.fiscal_year AS transaction_fiscal_year,
  AWD.fiscal_year AS award_fiscal_year,
  UTM.award_amount,
  UTM.federal_action_obligation AS transaction_amount,
  UTM.face_value_loan_guarantee,
  UTM.original_loan_subsidy_cost,
  UTM.generated_pragmatic_obligation,

  UTM.awarding_agency_id,
  UTM.funding_agency_id,
  UTM.awarding_toptier_agency_name,
  UTM.funding_toptier_agency_name,
  UTM.awarding_subtier_agency_name,
  UTM.funding_subtier_agency_name,
  UTM.awarding_toptier_agency_abbreviation,
  UTM.funding_toptier_agency_abbreviation,
  UTM.awarding_subtier_agency_abbreviation,
  UTM.funding_subtier_agency_abbreviation,
  CASE
    WHEN UTM.awarding_toptier_agency_name IS NOT NULL
      THEN CONCAT('{"name":"', UTM.awarding_toptier_agency_name, '","abbreviation":"', UTM.awarding_toptier_agency_abbreviation, '","id":"', TAA.id, '"}')
    ELSE NULL
  END AS awarding_toptier_agency_agg_key,
  CASE
    WHEN UTM.funding_toptier_agency_name IS NOT NULL
      THEN CONCAT('{"name":"', UTM.funding_toptier_agency_name, '","abbreviation":"', UTM.funding_toptier_agency_abbreviation, '","id":"', TFA.id, '"}')
    ELSE NULL
  END AS funding_toptier_agency_agg_key,
  CASE
    WHEN UTM.awarding_subtier_agency_name IS NOT NULL
      THEN CONCAT('{"name":"', UTM.awarding_subtier_agency_name, '","abbreviation":"', UTM.awarding_subtier_agency_abbreviation, '","id":"', AA.id, '"}')
    ELSE NULL
  END AS awarding_subtier_agency_agg_key,
  CASE
    WHEN UTM.funding_subtier_agency_name IS NOT NULL
      THEN CONCAT('{"name":"', UTM.funding_subtier_agency_name, '","abbreviation":"', UTM.funding_subtier_agency_abbreviation, '","id":"', FA.id, '"}')
    ELSE NULL
  END AS funding_subtier_agency_agg_key,

  UTM.cfda_number,
  CFDA.program_title AS cfda_title,
  CASE
    WHEN UTM.cfda_number IS NOT NULL THEN CONCAT('{"code":"', UTM.cfda_number, '","description":"', CFDA.program_title, '","id":"', CFDA.id, '"}')
    ELSE NULL
  END AS cfda_agg_key,

  UTM.type_of_contract_pricing,
  UTM.type_set_aside,
  UTM.extent_competed,
  UTM.type,

  UTM.pop_country_code,
  UTM.pop_country_name,
  UTM.pop_state_code,
  UTM.pop_county_code,
  UTM.pop_county_name,
  UTM.pop_zip5,
  UTM.pop_congressional_code,
  UTM.pop_city_name,
  CASE
    WHEN UTM.pop_county_code IS NOT NULL
      THEN CONCAT('{"country_code":"', UTM.pop_country_code, '","state_code":"', UTM.pop_state_code, '","county_code":"', UTM.pop_county_code, '","county_name":"', UTM.pop_county_name, '"}')
    ELSE NULL
  END AS pop_county_agg_key,
  CASE
    WHEN UTM.pop_congressional_code IS NOT NULL
      THEN CONCAT('{"country_code":"', UTM.pop_country_code, '","state_code":"', UTM.pop_state_code, '","congressional_code":"', UTM.pop_congressional_code, '"}')
    ELSE NULL
  END AS pop_congressional_agg_key,
  CASE
    WHEN UTM.pop_state_code IS NOT NULL
      THEN CONCAT('{"country_code":"', UTM.pop_country_code, '","state_code":"', UTM.pop_state_code, '","state_name":"', POP_STATE_LOOKUP.name, '"}')
    ELSE NULL
  END AS pop_state_agg_key,
  CASE
    WHEN UTM.pop_country_code IS NOT NULL
      THEN CONCAT('{"country_code":"', UTM.pop_country_code, '","country_name":"', POP_COUNTRY_LOOKUP.country_name, '"}')
    ELSE NULL
  END AS pop_country_agg_key,

  UTM.recipient_location_country_code,
  UTM.recipient_location_country_name,
  UTM.recipient_location_state_code,
  UTM.recipient_location_county_code,
  UTM.recipient_location_county_name,
  UTM.recipient_location_zip5,
  UTM.recipient_location_congressional_code,
  UTM.recipient_location_city_name,

  TREASURY_ACCT.treasury_accounts,
  FEDERAL_ACCT.federal_accounts,
  UTM.business_categories

FROM universal_transaction_matview UTM
INNER JOIN transaction_normalized TN ON (UTM.transaction_id = TN.id)
INNER JOIN awards AWD ON (UTM.award_id = AWD.id)
LEFT JOIN transaction_fpds FPDS ON (UTM.transaction_id = FPDS.transaction_id)
LEFT JOIN transaction_fabs FABS ON (UTM.transaction_id = FABS.transaction_id)
-- Similar joins are already performed on universal_transaction_matview, however, to avoid making the matview larger
-- than needed they have been placed here. Feel free to phase out if the columns gained from the following joins are
-- added to the universal_transaction_matview.
LEFT JOIN agency AA on (TN.awarding_agency_id = AA.id)
LEFT JOIN (
  SELECT a.id, a.toptier_agency_id, a.toptier_flag, ta.name, ta.abbreviation, ta.toptier_code
  FROM agency a
  INNER JOIN toptier_agency ta ON (a.toptier_agency_id = ta.toptier_agency_id)
  WHERE a.toptier_flag = TRUE
) TAA ON (AA.toptier_agency_id = TAA.toptier_agency_id)
LEFT JOIN subtier_agency SAA ON (AA.subtier_agency_id = SAA.subtier_agency_id)
LEFT JOIN agency FA on (TN.funding_agency_id = FA.id)
LEFT JOIN (
  SELECT a.id, a.toptier_agency_id, a.toptier_flag, ta.name, ta.abbreviation, ta.toptier_code
  FROM agency a
  INNER JOIN toptier_agency ta ON (a.toptier_agency_id = ta.toptier_agency_id)
  WHERE a.toptier_flag = TRUE
) TFA ON (FA.toptier_agency_id = TFA.toptier_agency_id)
LEFT JOIN subtier_agency SFA ON (FA.subtier_agency_id = SFA.subtier_agency_id)
LEFT JOIN references_cfda CFDA ON (FABS.cfda_number = CFDA.program_number)
LEFT JOIN recipient_lookup PRL ON (PRL.duns = UTM.parent_recipient_unique_id AND UTM.parent_recipient_unique_id IS NOT NULL)
LEFT JOIN LATERAL (
  SELECT   recipient_hash, recipient_level, recipient_unique_id
  FROM     recipient_profile
  WHERE    (recipient_hash = UTM.recipient_hash or recipient_unique_id = UTM.recipient_unique_id) AND
           recipient_name NOT IN (
             'MULTIPLE RECIPIENTS',
             'REDACTED DUE TO PII',
             'MULTIPLE FOREIGN RECIPIENTS',
             'PRIVATE INDIVIDUAL',
             'INDIVIDUAL RECIPIENT',
             'MISCELLANEOUS FOREIGN AWARDEES'
           ) AND recipient_name IS NOT NULL
  ORDER BY CASE
             WHEN recipient_level = 'C' then 0
             WHEN recipient_level = 'R' then 1
             ELSE 2
           END ASC
  LIMIT 1
) RECIPIENT_HASH_AND_LEVEL ON TRUE
LEFT JOIN LATERAL (
  SELECT country_name
  FROM   ref_country_code
  WHERE  country_code = UTM.pop_country_code
  LIMIT  1
) POP_COUNTRY_LOOKUP ON TRUE
LEFT JOIN LATERAL (
  SELECT   name
  FROM     state_data
  WHERE    code = UTM.pop_state_code
  ORDER BY id desc
  LIMIT    1
) POP_STATE_LOOKUP ON TRUE
LEFT JOIN (
  SELECT
    faba.award_id,
    JSONB_AGG(
      DISTINCT JSONB_BUILD_OBJECT(
        'aid', taa.agency_id,
        'ata', taa.allocation_transfer_agency_id,
        'main', taa.main_account_code,
        'sub', taa.sub_account_code,
        'bpoa', taa.beginning_period_of_availability,
        'epoa', taa.ending_period_of_availability,
        'a', taa.availability_type_code
       )
     ) treasury_accounts
 FROM
   treasury_appropriation_account taa
   INNER JOIN financial_accounts_by_awards faba ON (taa.treasury_account_identifier = faba.treasury_account_id)
 WHERE
   faba.award_id IS NOT NULL
 GROUP BY
   faba.award_id
) TREASURY_ACCT ON (TREASURY_ACCT.award_id = UTM.award_id)
LEFT JOIN (
  SELECT
    faba.award_id,
    JSONB_AGG(
      DISTINCT JSONB_BUILD_OBJECT(
        'id', fa.id,
        'account_title', fa.account_title,
        'federal_account_code', fa.federal_account_code
      )
    ) federal_accounts
  FROM
    federal_account fa
    INNER JOIN treasury_appropriation_account taa ON fa.id = taa.federal_account_id
    INNER JOIN financial_accounts_by_awards faba ON taa.treasury_account_identifier = faba.treasury_account_id
  WHERE
    faba.award_id IS NOT NULL
  GROUP BY
    faba.award_id
) FEDERAL_ACCT ON (FEDERAL_ACCT.award_id = UTM.award_id);
