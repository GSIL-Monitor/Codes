package com.tsb.dao.read.org;

import java.util.List;

import com.tsb.model.org.ColdcallFile;

public interface ColdcallFileReadDao {
	List<ColdcallFile> listByColdcallId(int coldcallId);
}
