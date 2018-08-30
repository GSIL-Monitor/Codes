package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.Member;

public interface MemberReadDao {

	Member getById(Integer id);

	@SuppressWarnings("rawtypes")
	List<Member> getByIds(@Param("ids") List ids);
}
