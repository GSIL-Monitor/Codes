package com.tsb.user.dao.write;

import com.tsb.model.user.CompanyListRel;

public interface CompanyListRelWriteDao {
	void insert(CompanyListRel clr);

	void updateModifyTime(CompanyListRel clr);
}
