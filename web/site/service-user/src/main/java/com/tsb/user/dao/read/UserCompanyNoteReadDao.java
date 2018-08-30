package com.tsb.user.dao.read;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.user.UserCompanyNote;

public interface UserCompanyNoteReadDao {
	UserCompanyNote get(@Param("userId") int userId, @Param("companyId") int companyId);

	UserCompanyNote getAll(@Param("userId") int userId, @Param("companyId") int companyId);
}
