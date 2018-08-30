package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.Tag;

@SuppressWarnings("rawtypes")
public interface TagReadDao {
	Tag get(Integer id);
	List getByIds(@Param("ids") List ids);
	Tag getByName(String name);
	String getNameById(Integer id);
}
