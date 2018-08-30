package com.tsb.dao.read.org;

import com.tsb.model.org.Coldcall;

public interface ColdcallReadDao {
	Coldcall get(int id);
	Integer getTotal();
	Integer getUnMatched();
}
