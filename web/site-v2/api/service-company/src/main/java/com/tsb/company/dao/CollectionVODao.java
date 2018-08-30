package com.tsb.company.dao;

import java.util.List;

import com.tsb.company.vo.CollectionVO;

public interface CollectionVODao {
	
	List<CollectionVO> getHotCols(Integer type);
}
