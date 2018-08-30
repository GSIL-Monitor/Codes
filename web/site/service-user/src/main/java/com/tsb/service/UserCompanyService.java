package com.tsb.service;

import java.sql.Date;
import java.sql.Timestamp;
import java.util.List;

import com.tsb.model.user.UserCompanyFollow;
import com.tsb.model.user.UserCompanyNote;
import com.tsb.model.vo.FollowCompany;

@SuppressWarnings("rawtypes")
public interface UserCompanyService {

	List<FollowCompany> getFolCompaniesByStatus(Integer id, int statusValue);

	void unfollow(Integer userId, List companyIds);

	UserCompanyFollow getByUserIdAndCompanyId(int userId, int companyId);

	UserCompanyNote getUserCompanyNote(int userId, int companyId);

	// heart is active
	void updateHeart(int userId, int companyId, Character heart);

	void updateFollowing(int userId, int companyId, int status, Date start);

	void updateNote(int userId, int companyId, String note);

}
