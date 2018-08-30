package com.tsb.service;

import java.util.List;

import com.tsb.model.user.CompanyList;
import com.tsb.user.model.vo.UserList;

@SuppressWarnings("rawtypes")
public interface UserListService {
	UserList getUserList(Integer userId, int page);

	// getAll without page
	UserList getAllList(Integer userId);

	void updateDesc(int listId, String desc);

	void deleteList(int listId);

	List getCompanyIds(int listId);

	// list info
	CompanyList getCompanyList(int listId);

	void createList(int userId, String name);

	UserList getRelatedList(int userId, int companyId);
}
