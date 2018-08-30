package com.tsb.user.dao.write;

import com.tsb.model.user.UserCompanyFollow;

public interface UserCompanyFollowWriteDao {

	void insert(UserCompanyFollow ucf);

	void update(UserCompanyFollow ucf);
	void updateStatsu(UserCompanyFollow ucf);
	// void updateByUserIdAndCompanyId(UserCompanyRel ucr);
	// void delete(UserCompanyRel ucr);
}
