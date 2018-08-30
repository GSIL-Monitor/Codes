package com.tsb.dao.write.company;

import com.tsb.model.company.Footprint;

public interface FootprintWriteDao {
	void insert(Footprint footprint);
	void update(Footprint footprint);
	void delete(Integer id);
}
