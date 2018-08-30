package com.tsb.user.dao.write;

import com.tsb.model.user.UserCompanyNote;

public interface UserCompanyNoteWriteDao {

	void insert(UserCompanyNote ucn);

	void update(UserCompanyNote ucn);
}
