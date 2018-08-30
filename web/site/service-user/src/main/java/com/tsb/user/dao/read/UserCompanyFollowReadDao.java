package com.tsb.user.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.user.UserCompanyFollow;

public interface UserCompanyFollowReadDao {
	List<UserCompanyFollow> getByUserId(int userId);

	List<UserCompanyFollow> getByStatus(@Param("userId") int userId, @Param("status") int status);

	UserCompanyFollow getByUserIdAndCompanyId(@Param("userId") int userId, @Param("companyId") int companyId);
}
