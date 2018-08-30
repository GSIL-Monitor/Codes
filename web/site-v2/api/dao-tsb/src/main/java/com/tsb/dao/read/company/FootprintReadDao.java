package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.Footprint;

public interface FootprintReadDao {

	List<Footprint> getByCompanyId(Integer companyId);
}
