package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.Job;

public interface JobReadDao {

	List<Job> getByCompanyId(Integer companyId);

	int count(int companyId);
}
