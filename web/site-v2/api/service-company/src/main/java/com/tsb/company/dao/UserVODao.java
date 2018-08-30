package com.tsb.company.dao;

import java.util.List;

import com.tsb.company.vo.UserVO;

public interface UserVODao {
	List<UserVO> getCollegues(int userId);
}
