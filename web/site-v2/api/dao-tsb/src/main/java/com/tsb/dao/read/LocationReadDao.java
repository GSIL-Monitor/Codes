package com.tsb.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.Location;

public interface LocationReadDao {
	String get(Integer id);
	Integer getByName(String name);
	List<Location> getByIds(@Param("ids") List<Integer> ids);
}
