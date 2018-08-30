package com.tsb.admin.dao;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.admin.vo.UsersInfoVO;

public interface UsersInfoReadDao {
	List<UsersInfoVO> getById(int id);

	List<UsersInfoVO> get(@Param("id") int id, @Param("from") int from, @Param("pageSize") int pageSize);

	int getUsersNum(int id);
}
