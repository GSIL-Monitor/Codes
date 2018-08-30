select id from contest_company where contestId=10;

delete from stage_user_rel where stageId in (11,12,13);

delete from contest_company_organization_result 
where contestCompanyId in (select id from contest_company where contestId=10);

delete from contest_company_user_result
where contestCompanyId in (select id from contest_company where contestId=10);

delete from contest_company_file
where contestCompanyId in (select id from contest_company where contestId=10);

delete from contest_company_score
where contestCompanyId in (select id from contest_company where contestId=10);

delete from stage_contest_company_user_comment
where contestCompanyId in (select id from contest_company where contestId=10);

delete from stage_score_dimension where stageId in (11,12,13);
delete from contest_company_stage where stageId in (11,12,13);
delete from stage_user_rel where stageId in (11,12,13);
delete from contest_stage where id in (11,12,13);

delete from contest_organization_topic where topicId in (11,12,13);
delete from contest_company where contestId=10;
delete from contest_topic where id in (11,12,13);

delete from contest_organization where contestId=10;
delete from contest where id=10;

