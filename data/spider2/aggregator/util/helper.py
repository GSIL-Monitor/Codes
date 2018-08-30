# -*- coding: utf-8 -*-

def get_table_names(test):
    company_table_name = "company"
    company_alias_table_name = "company_alias"
    artifact_table_name = "artifact"
    funding_table_name = "funding"
    funding_investor_rel_table_name = "funding_investor_rel"
    member_table_name = "member"
    company_member_rel_table_name = "company_member_rel"

    if test:
        company_table_name = "test_" + company_table_name
        company_alias_table_name = "test_" + company_alias_table_name
        artifact_table_name = "test_" + artifact_table_name
        funding_table_name = "test_" + funding_table_name
        funding_investor_rel_table_name = "test_" + funding_investor_rel_table_name
        member_table_name = "test_" + member_table_name
        company_member_rel_table_name = "test_" + company_member_rel_table_name

    return {
        "company": company_table_name,
        "company_alias": company_alias_table_name,
        "artifact": artifact_table_name,
        "funding": funding_table_name,
        "funding_investor_rel": funding_investor_rel_table_name,
        "member": member_table_name,
        "company_member_rel": company_member_rel_table_name
    }